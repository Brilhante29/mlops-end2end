from mlops_end2end import runner
from mlops_end2end.runner import _airflow_dag_test_command, _percentile


def test_percentile_uses_nearest_rank() -> None:
    assert _percentile([5.0, 1.0, 4.0, 2.0, 3.0], 0.95) == 5.0
    assert _percentile([5.0, 1.0, 4.0, 2.0, 3.0], 0.50) == 3.0


def test_api_benchmark_separates_warmup_from_measured_requests(monkeypatch) -> None:
    calls: list[str] = []

    def record_prediction(api_url: str, features: list[float]) -> float:
        calls.append(api_url)
        assert len(features) == 8
        return 1.0

    monkeypatch.setattr(runner, "_post_prediction", record_prediction)

    result = runner._benchmark_api(
        "http://example.test", requests=4, concurrency=2, warmup_requests=3
    )

    assert len(calls) == 7
    assert result["inference_p50_ms"] == 1.0
    assert result["inference_p95_ms"] == 1.0
    assert result["inference_requests_per_second"] > 0


def test_airflow_command_executes_the_versioned_dag() -> None:
    assert _airflow_dag_test_command() == [
        "airflow",
        "dags",
        "test",
        "mlops_end2end",
        "2026-01-01T00:00:00+00:00",
        "--dagfile-path",
        "/opt/portfolio/dags/mlops_end2end.py",
    ]
