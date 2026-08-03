from pathlib import Path

from mlops_end2end.config import Settings


def test_default_tracking_uri_uses_runtime_local_sqlite(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("MLOPS_RUNTIME_DIR", str(tmp_path))
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)

    settings = Settings.from_env()

    expected_database = (tmp_path / "mlflow" / "mlflow.db").as_posix()
    assert settings.tracking_uri == f"sqlite:///{expected_database}"
    settings.prepare()
    assert settings.artifact_dir.is_dir()
