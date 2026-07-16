from __future__ import annotations

import time
from contextlib import asynccontextmanager
from dataclasses import dataclass

import mlflow
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from mlflow import MlflowClient
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field, field_validator

from mlops_end2end.adapters.data import feature_names
from mlops_end2end.config import Settings

PREDICTIONS = Counter(
    "mlops_predictions_total",
    "Total predictions served by outcome.",
    labelnames=("outcome",),
)
PREDICTION_LATENCY = Histogram(
    "mlops_prediction_latency_seconds",
    "Prediction latency in seconds.",
)
MODEL_INFO = Gauge(
    "mlops_model_info",
    "Loaded model metadata.",
    labelnames=("model", "alias", "version"),
)


class PredictionRequest(BaseModel):
    features: list[float] = Field(min_length=1, max_length=128)

    @field_validator("features")
    @classmethod
    def validate_feature_count(cls, values: list[float]) -> list[float]:
        expected = Settings.from_env().feature_count
        if len(values) != expected:
            raise ValueError(f"expected exactly {expected} features")
        return values


class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    model_alias: str
    model_version: str


@dataclass
class ModelState:
    model: object | None = None
    version: str = ""

    def load(self, settings: Settings) -> None:
        mlflow.set_tracking_uri(settings.tracking_uri)
        model_uri = f"models:/{settings.model_name}@{settings.model_alias}"
        self.model = mlflow.pyfunc.load_model(model_uri)
        registered = MlflowClient(tracking_uri=settings.tracking_uri).get_model_version_by_alias(
            settings.model_name,
            settings.model_alias,
        )
        self.version = str(registered.version)
        MODEL_INFO.labels(settings.model_name, settings.model_alias, self.version).set(1)

    def predict(self, features: list[float], settings: Settings) -> PredictionResponse:
        if self.model is None:
            raise RuntimeError("model is not loaded")
        frame = pd.DataFrame([features], columns=feature_names(settings.feature_count))
        started = time.perf_counter()
        raw = np.asarray(self.model.predict(frame))
        probability = float(raw[0, 1] if raw.ndim == 2 else raw[0])
        prediction = int(probability >= 0.5)
        PREDICTION_LATENCY.observe(time.perf_counter() - started)
        PREDICTIONS.labels(outcome=str(prediction)).inc()
        return PredictionResponse(
            prediction=prediction,
            probability=probability,
            model_alias=settings.model_alias,
            model_version=self.version,
        )


settings = Settings.from_env()
model_state = ModelState()


@asynccontextmanager
async def lifespan(_: FastAPI):
    model_state.load(settings)
    yield


app = FastAPI(
    title="MLOps End-to-End Inference",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    if model_state.model is None:
        raise HTTPException(status_code=503, detail="model is not loaded")
    return {
        "status": "healthy",
        "model": settings.model_name,
        "alias": settings.model_alias,
        "version": model_state.version,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    try:
        return model_state.predict(payload.features, settings)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

