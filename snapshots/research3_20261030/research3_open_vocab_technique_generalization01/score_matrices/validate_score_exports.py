"""Check the saved fusion interface independently of inference implementation."""
from __future__ import annotations
import os
for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "2"
import ast
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / "FULL_216_SCORE_MATRIX_MANIFEST.json").read_text())
    assert len(manifest["matrices"]) == 42
    folds = {}
    matrix_rows = 0
    for entry in manifest["matrices"]:
        path = ROOT / entry["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        with np.load(path, allow_pickle=False) as data:
            n = len(data["sample_ids"])
            assert len(set(data["sample_ids"])) == n
            assert data["technique_ids"].tolist() == sorted(data["technique_ids"].tolist())
            assert len(data["technique_ids"]) == 216
            assert np.array_equal(data["seen"], data["support"] > 0)
            assert np.isnan(data["b3_scores"][:, ~data["seen"]]).all()
            assert np.isfinite(data["b3_scores"][:, data["seen"]]).all()
            assert not np.any(data["b3_scores"][:, data["seen"]] == -1e6)
            partition_sets = {p: set(data["sample_ids"][data["partitions"] == p]) for p in ("TRAIN", "VALIDATION", "HELDOUT")}
            assert sum(len(v) for v in partition_sets.values()) == n
            assert not (partition_sets["TRAIN"] & partition_sets["VALIDATION"])
            assert not (partition_sets["TRAIN"] & partition_sets["HELDOUT"])
            assert not (partition_sets["VALIDATION"] & partition_sets["HELDOUT"])
            for key in ("gte_scores", "b4_scores", "b5_scores"):
                assert data[key].shape == (n, 216) and np.isfinite(data[key]).all()
            folds[entry["fold_id"]] = {"seen": int(data["seen"].sum()), "unseen": int((~data["seen"]).sum())}
            matrix_rows += n
    export_counts = {}
    for name in ("FROZEN_GTE_SCORES.jsonl", "B3_SUPERVISED_SCORES.jsonl"):
        total = 0
        with (ROOT / name).open() as f:
            for line in f:
                row = json.loads(line)
                assert len(row["technique_ids"]) == 216
                assert len(row["training_class_support"]) == 216
                assert "gold_technique_ids" not in row
                if name.startswith("B3"):
                    assert len(row["supervised_b3_scores"]) == len(row["supervised_score_available"]) == 216
                    assert all((score is None) == (not available) for score, available in zip(row["supervised_b3_scores"], row["supervised_score_available"]))
                else:
                    assert len(row["frozen_gte_scores"]) == 216
                total += 1
        export_counts[name] = total
    assert export_counts["FROZEN_GTE_SCORES.jsonl"] == 2909
    assert export_counts["B3_SUPERVISED_SCORES.jsonl"] == matrix_rows == 17454
    ast.parse((ROOT / "score_matrices/reconstruct_scores.py").read_text())
    result = {"status": "PASS", "matrices_checked": 42, "matrix_rows": matrix_rows, "jsonl_counts": export_counts, "fold_seen_unseen": folds, "NaN_null_availability_consistent": True, "historical_sentinel_in_fusion_matrices": False, "inference_source_AST": "PASS", "validator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (ROOT / "inherited/EXPORT_SCHEMA_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
