from __future__ import annotations

import json
import re
from pathlib import Path

import jsonschema
from publish_benchmark import (
    ROOT,
    combined_digest,
    combined_git_digest,
    validate_run,
)
from publish_benchmark import (
    run as run_command,
)

V1_PATH = ROOT / "benchmarks" / "results" / "summary.json"
V2_PATH = ROOT / "benchmarks" / "publication" / "mlops-lifecycle-v2.json"
SCHEMA_PATH = ROOT / ".portfolio" / "contracts" / "benchmark-result-v2.schema.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evidence_digest(paths: list[str]) -> str:
    status = run_command(
        ["git", "-c", f"safe.directory={ROOT}", "status", "--porcelain", "--", *paths]
    ).stdout.strip()
    return combined_digest(paths) if status else combined_git_digest(paths, "HEAD")


def main() -> None:
    v1 = read_json(V1_PATH)
    v2 = read_json(V2_PATH)
    jsonschema.validate(v2, read_json(SCHEMA_PATH))

    raw_paths = v1["proof"]["raw_artifacts"]
    raw_runs = [read_json(ROOT / relative) for relative in raw_paths]
    for run in raw_runs:
        validate_run(run)

    assert v1["repeat"] == len(raw_runs) == 3
    assert v1["measured_lifecycle_runs"] == 3
    assert v1["value"] == v1["metrics"]["time_to_production_seconds"]
    assert v1["value"] == v2["metrics"][0]["value"]
    assert v2["execution"]["repeat"] == 3
    assert v2["workload"]["measured_iterations"] == 3
    assert v2["metrics"][0]["samples"] == [run["value"] for run in raw_runs]

    provenance = v2["provenance"]
    assert provenance["source_commit"] == v1["proof"]["source_commit"]
    assert provenance["image_digest"] == v1["proof"]["image_digest"]
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", provenance["image_digest"])
    assert provenance["artifact_digest"] == evidence_digest(raw_paths)
    assert provenance["dependency_lock_digest"] == combined_git_digest(
        ["pyproject.toml", "requirements.txt"], provenance["source_commit"]
    )
    assert v2["workload"]["fixture_digest"] == combined_git_digest(
        [
            "dags/mlops_end2end.py",
            "src/mlops_end2end/adapters/data.py",
            "src/mlops_end2end/adapters/training.py",
            "src/mlops_end2end/application/promotion.py",
            "src/mlops_end2end/domain/quality.py",
        ],
        provenance["source_commit"],
    )
    assert v2["workload"]["config_digest"] == combined_git_digest(
        [
            "Dockerfile",
            "benchmarks/config/mlops-lifecycle-v2.json",
            "src/mlops_end2end/config.py",
            "src/mlops_end2end/runner.py",
            "tools/publish_benchmark.py",
        ],
        provenance["source_commit"],
    )
    serialized = json.dumps({"v1": v1, "v2": v2})
    assert "C:\\Users\\" not in serialized
    assert ("github" + "_pat_") not in serialized
    assert ("gh" + "p_") not in serialized
    print("publication_evidence=passed")


if __name__ == "__main__":
    main()
