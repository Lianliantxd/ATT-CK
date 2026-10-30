"""Finalize only after all workers/reports stop writing. Run with Python -B.

This validator does not train, score, tune, download, contact servers, or read
heldout references. It checks saved products and rehashes all immutable assets.
It writes only FINAL_VALIDATION.json and DELIVERY_SHA256.json after success.
"""
from __future__ import annotations
import os
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "2"
import ast
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / "research3_domain_adaptive_contrastive_learning01"
BENCH = ROOT.parent / "research3_attack_technique_benchmark01"
PROTOCOL_SHA = "cceb35fc46eaeb5cc4db5973e315ab0a7288cbac5a1d0d1722031944a42289e3"
REQUIRED_ROOT = (
    "INHERITED_MODEL_SCORE_AUDIT.md", "FULL_216_SCORE_MATRIX_MANIFEST.json",
    "FROZEN_GTE_SCORES.jsonl", "B3_SUPERVISED_SCORES.jsonl", "SEEN_CLASS_INVENTORY_BY_FOLD.csv",
    "GENERALIZED_ZERO_SHOT_PROTOCOL.md", "FUSION_METHOD_DEFINITIONS.md", "FUSION_PARAMETER_REGISTRATION.json",
    "FUSION_PREDICTIONS.jsonl", "FUSION_RESULTS.csv", "SCORE_CALIBRATION_DIAGNOSTICS.csv",
    "SEEN_UNSEEN_MIXED_RESULTS.csv", "MIXED_SAMPLE_COVERAGE.csv", "LONG_TAIL_TECHNIQUE_RESULTS.csv",
    "SEEN_UNSEEN_TRADEOFF.csv", "CLASS_BIAS_ANALYSIS.md", "MACRO_F1_COMPARISON.csv",
    "TRAINING_CLASS_PRIORS.csv", "PRIOR_BASELINE_RESULTS.csv", "CLASS_FREQUENCY_ERROR_ANALYSIS.md",
    "EXTERNAL_DATA_INSTANCE_REGISTER.csv", "EXTERNAL_LABEL_UNIT_AUDIT.md", "EXTERNAL_DATASET_QUALIFICATION.md",
    "EXTERNAL_EVALUATION_PREDICTIONS.jsonl", "EXTERNAL_EVALUATION_RESULTS.csv",
    "OPEN_VOCAB_ERROR_ANALYSIS.md", "OPEN_VOCAB_METHOD_COMPARISON.md", "METHOD_RESEARCH_DECISION.md",
    "R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION_RESULTS.md",
)
FIGURES = ("figure01_main_seen_unseen", "figure02_seen_unseen_tradeoff", "figure03_mixed_coverage", "figure04_long_tail_class_mrr")
EXCLUDED_DIRS = {"venvs", "__pycache__", ".git"}
EXCLUDED_FILES = {"manifests/DELIVERY_SHA256.json", "results/FINAL_VALIDATION.json"}


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(relative):
    return json.loads((ROOT / relative).read_text())


def rows_csv(relative):
    with (ROOT / relative).open() as f:
        yield from csv.DictReader(f)


def count_jsonl(relative, expected, candidates=None, prediction=False):
    count = 0
    groups = collections.Counter()
    with (ROOT / relative).open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if prediction:
                order = row["ranking_all216"]
                assert len(order) == len(set(order)) == 216 and set(order) == candidates
                assert row["predictions"] == order[:10]
                assert len(row["scores_all216"]) == 216
                assert all(v is None or isinstance(v, (int, float)) and math.isfinite(v) for v in row["scores_all216"])
                assert row["evaluation_partition"] == "HELDOUT"
                assert "gold_technique_ids" not in row and "sample_type" not in row
                groups[row["method"], row["seed"], row["view_id"]] += 1
            count += 1
    assert count == expected, (relative, count, expected)
    return {"rows": count, "method_seed_view_groups": len(groups)}


def source_bound(receipt, field, relative):
    assert receipt[field] == sha(ROOT / relative), (field, relative)


def external_status():
    qualification = read_json("external_dataset/QUALIFICATION_AUDIT.json")
    assert qualification["scientific_state"] == "EXTERNAL_TEST_NOT_READY"
    assert qualification["bags_evaluated"] == qualification["prediction_rows"] == 0
    assert qualification.get("local_log_body_bytes_downloaded", 0) == 0
    assert (ROOT / "EXTERNAL_EVALUATION_PREDICTIONS.jsonl").read_text().strip() == ""
    results = list(rows_csv("EXTERNAL_EVALUATION_RESULTS.csv"))
    assert len(results) == qualification["not_executed_result_rows"]
    for row in results:
        assert row["evaluation_unit"] == "DATASET_LEVEL_BAG" and int(row["evaluated_bags"]) == 0
        assert all(row[k] in {"NA", "N/A", ""} for k in ("top1", "top5", "top10", "mrr10"))
    manifest = read_json("external_dataset/SERVER_DOWNLOAD_MANIFEST.json")
    grant = read_json("external_dataset/SERVER_DOWNLOAD_AUTHORIZATION.json")
    assert grant["authorized"] and manifest["authorized"]
    assert manifest["raw_storage_policy"] == "SERVER_ONLY_NO_LOCAL_RAW_COPY"
    assert grant["total_bytes"] == manifest["total_payload_bytes"] == 12905849
    assert not any(grant[k] for k in ("model_downloads", "gpu_calls", "training", "llm_calls"))
    raw_names = {r["name"] for r in manifest["files"]}
    assert len(raw_names) == 3
    local_raw = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and (p.name in raw_names or "raw" in p.relative_to(ROOT).parts)]
    assert not local_raw, local_raw
    receipt_path = ROOT / "external_dataset/server_receipts/SERVER_DOWNLOAD_RECEIPT.json"
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        assert receipt["status"] == "THREE_EXACT_PUBLIC_LOGS_ACQUIRED_AND_HASH_VERIFIED"
        assert receipt["host"] == "10.109.119.118"
        assert receipt["total_payload_bytes"] == 12905849 and not receipt["raw_logs_returned_to_local"]
        assert all(receipt[k] == 0 for k in ("model_calls", "gpu_calls", "training_runs", "llm_calls", "packages_installed", "captured_commands_executed"))
        expected = {x["name"]: x for x in manifest["files"]}
        assert {x["name"] for x in receipt["files"]} == set(expected)
        for item in receipt["files"]:
            assert item["verified"] and item["bytes"] == expected[item["name"]]["bytes"] and item["sha256"] == expected[item["name"]]["sha256"]
            assert item["server_path"].startswith("/home/tianxiaodan/code/ATT/R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION01/")
        assert qualification["server_log_body_bytes_acquired"] == 12905849
        assert qualification["qualification"].startswith("E1_BAG_FEASIBILITY")
        assert qualification["status"] == "PASS_SERVER_ONLY_ACQUISITION_NO_MODEL_EVALUATION"
        preprocess = read_json("external_dataset/server_receipts/PREPROCESS_AUDIT.json")
        assert preprocess["bag_count"] == qualification["bags_prepared"] == 1
        assert preprocess["model_calls"] == 0 and preprocess["event_level_gold_created"] == 0 and preprocess["commands_executed"] == 0
        assert len(preprocess["inputs"]) == 3
        for entry in qualification.get("server_receipt_files", []):
            assert sha(ROOT / entry["path"]) == entry["sha256"]
        return {"status": qualification["status"], "qualification": qualification["qualification"], "server_raw_bytes": 12905849, "local_raw_bytes": 0, "bags_prepared": 1, "bags_evaluated": 0, "external_metrics": "N/A", "parser_status": preprocess["parse_status"]}
    # A failed acquisition remains a documented blocker. An unchanged pre-grant
    # metadata snapshot is not accepted as final evidence after authorization.
    assert qualification.get("server_log_body_bytes_acquired", 0) == 0
    assert "CURRENT_EXPLICIT_DOWNLOAD_AUTHORIZATION_MISSING" not in qualification.get("remaining_blockers", [])
    assert any(word in qualification["status"] for word in ("FAILED", "BLOCKED", "INCOMPLETE")), qualification["status"]
    return {"status": qualification["status"], "server_raw_bytes": 0, "local_raw_bytes": 0, "bags_evaluated": 0, "external_metrics": "N/A"}


def main():
    began = time.monotonic()
    for name in REQUIRED_ROOT:
        path = ROOT / name
        assert path.is_file(), name
        assert path.stat().st_size > 0 or name == "EXTERNAL_EVALUATION_PREDICTIONS.jsonl", name
    report = (ROOT / "R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION_RESULTS.md").read_text()
    questions = [int(n) for n in re.findall(r"^### Q(\d+)\.", report, flags=re.M)]
    assert questions == list(range(1, 45)), questions
    assert "DEVELOPMENT_ONLY" in report and "EXTERNAL_TEST_NOT_READY" in report
    assert "Gold" in report and ("时序" in report or "提前" in report)
    assert sha(ROOT / "FUSION_PARAMETER_REGISTRATION.json") == PROTOCOL_SHA
    assert (ROOT / "frozen_protocol/REGISTRATION_SHA256.txt").read_text().strip() == PROTOCOL_SHA
    protocol = read_json("FUSION_PARAMETER_REGISTRATION.json")
    assert protocol["resource"]["local_disk_guard_bytes"] == 2000000000
    matrix_manifest = read_json("FULL_216_SCORE_MATRIX_MANIFEST.json")
    assert matrix_manifest["old_manifest_entries_verified"] == 1938 and matrix_manifest["checkpoints_verified"] == 378
    assert len(matrix_manifest["matrices"]) == len(list((ROOT / "score_matrices").glob("*.npz"))) == 42
    candidate_ids = None
    matrix_rows = 0
    for entry in matrix_manifest["matrices"]:
        path = ROOT / entry["path"]
        assert sha(path) == entry["sha256"] and path.stat().st_size == entry["bytes"]
        with np.load(path, allow_pickle=False) as data:
            ids = data["technique_ids"].tolist()
            assert ids == sorted(set(ids)) and len(ids) == 216
            candidate_ids = ids if candidate_ids is None else candidate_ids
            assert ids == candidate_ids
            n = len(data["sample_ids"])
            assert n == len(set(data["sample_ids"]))
            assert np.array_equal(data["seen"], data["support"] > 0)
            assert np.isnan(data["b3_scores"][:, ~data["seen"]]).all()
            assert np.isfinite(data["b3_scores"][:, data["seen"]]).all()
            assert all(data[k].shape == (n, 216) and np.isfinite(data[k]).all() for k in ("gte_scores", "b4_scores", "b5_scores"))
            matrix_rows += n
    assert matrix_rows == 17454
    prediction_counts = {
        "main": count_jsonl("FUSION_PREDICTIONS.jsonl", 64350, set(candidate_ids), True),
        "tradeoff": count_jsonl("predictions/TRADEOFF_PREDICTIONS.jsonl", 23400, set(candidate_ids), True),
        "gte_export": count_jsonl("FROZEN_GTE_SCORES.jsonl", 2909),
        "b3_export": count_jsonl("B3_SUPERVISED_SCORES.jsonl", 17454),
    }
    fit = read_json("calibration/FITTING_RECEIPT.json")
    predicted = read_json("predictions/PREDICTION_RECEIPT.json")
    assert fit["selected_conditions"] == len(read_json("calibration/SELECTED_PARAMETERS.json")) == 462
    assert fit["grid_conditions"] == sum(1 for _ in rows_csv("calibration/ALL_PARAMETER_CANDIDATES.csv")) == 1722
    assert fit["protocol_sha256"] == predicted["protocol_sha256"] == PROTOCOL_SHA
    assert fit["parameters_sha256"] == predicted["parameters_sha256"] == sha(ROOT / "calibration/SELECTED_PARAMETERS.json")
    source_bound(fit, "source_sha256", "calibration/fit_calibrators.py")
    source_bound(predicted, "source_sha256", "fusion/predict.py")
    source_bound(predicted, "core_sha256", "fusion/core.py")
    source_bound(predicted, "main_prediction_sha256", "FUSION_PREDICTIONS.jsonl")
    source_bound(predicted, "tradeoff_sha256", "predictions/TRADEOFF_PREDICTIONS.jsonl")
    assert predicted["main_rows"] == 64350 and predicted["tradeoff_rows"] == 23400
    independent = read_json("results/FUSION_INDEPENDENT_AUDIT.json")
    assert independent["status"].startswith("PASS")
    assert independent["matrix_configurations"] == 42 and independent["grid_validation_conditions"] == 1722
    assert independent["selected_parameter_mismatches"] == independent["ranking_mismatches"] == 0
    assert independent["prediction_score_max_abs_error"] == 0 and independent["full216_score_cells_checked"] == 18954000
    source_bound(independent, "auditor_sha256", "fusion/independent_audit.py")
    timing = independent["session_timing_disclosure"]
    assert sha(ROOT / timing["path"]) == timing["sha256"]
    assert not timing["Gold_transmitted_to_fitter_or_predictor"] and not timing["parameters_changed_as_result"]
    expected_counts = {"queries": 975, "logical_steps": 195, "scenarios": 7, "all_seen": 525, "all_unseen": 305, "mixed": 145, "seen_target": 670, "unseen_target": 450}
    for filename, prediction_path, expected_rows, conditions in (("results/EVALUATION_AUDIT.json", "FUSION_PREDICTIONS.jsonl", 64350, 462), ("results/TRADEOFF_EVALUATION_AUDIT.json", "predictions/TRADEOFF_PREDICTIONS.jsonl", 23400, 168)):
        audit = read_json(filename)
        assert audit["status"] == "PASS" and audit["prediction_rows"] == expected_rows and audit["evaluation_conditions"] == conditions
        assert audit["max_absolute_metric_difference"] == 0 and audit["full216_candidates_preserved"]
        assert audit["counts_per_method_seed_view"] == expected_counts
        assert audit["parameter_registration_sha256"] == PROTOCOL_SHA
        source_bound(audit, "evaluator_sha256", "open_vocab_evaluation/evaluate_saved.py")
        source_bound(audit, "prediction_sha256", prediction_path)
        assert audit["frozen_evaluator_sha256"] == sha(BENCH / "evaluate_techniques.py")
        disclosure = audit["pre_prediction_reference_preflight_disclosure"]
        assert disclosure["occurrences"] == 2 and not disclosure["new_fusion_performance_computed_during_preflight"]
        assert not disclosure["labels_sent_to_predictor_or_parameter_fitter"]
    lineage = read_json("results/PIPELINE_LINEAGE_AUDIT.json")
    assert lineage["status"].startswith("PASS")
    strata = collections.defaultdict(collections.Counter)
    sample_rows = 0
    for row in rows_csv("results/PER_SAMPLE_RESULTS.csv"):
        strata[row["method"], row["seed"], row["view_id"]][row["sample_type"]] += 1
        sample_rows += 1
    assert sample_rows == 64350 and len(strata) == 66
    assert all(dict(counts) == {"ALL_SEEN": 525, "ALL_UNSEEN": 305, "MIXED": 145} for counts in strata.values())
    assert sum(1 for _ in rows_csv("FUSION_RESULTS.csv")) == 22
    bundle = ROOT / "reports/analysis-output"
    for name in ("analysis-report.md", "stats-appendix.md", "figure-catalog.md", "provenance.json"):
        assert (bundle / name).is_file() and (bundle / name).stat().st_size > 0
    json.loads((bundle / "provenance.json").read_text())
    figure_checks = []
    for stem in FIGURES:
        base = bundle / "figures" / stem
        png = base.with_suffix(".png").read_bytes()
        assert png[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", png[16:24])
        assert width >= 400 and height >= 300 and len(png) > 10000
        pdf = base.with_suffix(".pdf").read_bytes()
        assert pdf.startswith(b"%PDF-") and len(pdf) > 1000
        svg = base.with_suffix(".svg").read_text()
        assert "<svg" in svg and len(svg) > 1000
        figure_checks.append({"stem": stem, "png_dimensions": [width, height], "formats": ["PNG", "PDF", "SVG"], "check_scope": "file format/dimensions; visual QA documented separately"})
    external = external_status()
    source_files = []
    all_files = []
    for path in sorted(ROOT.rglob("*")):
        if path.is_symlink() or not path.is_file() or any(p in EXCLUDED_DIRS for p in path.relative_to(ROOT).parts):
            continue
        if path.suffix == ".py":
            ast.parse(path.read_text(), filename=str(path))
            source_files.append(str(path.relative_to(ROOT)))
        all_files.append(path)
    total_disk = sum(p.stat().st_size for p in all_files)
    assert total_disk < 2000000000, total_disk
    # Last substantive operation before sealing: recheck every immutable old
    # byte, including all 378 checkpoints, without importing/executing old code.
    old_manifest = json.loads((OLD / "manifests/DELIVERY_SHA256.json").read_text())
    assert len(old_manifest) == 1938
    for entry in old_manifest:
        path = OLD / entry["path"]
        assert path.stat().st_size == entry["bytes"] and sha(path) == entry["sha256"], entry["path"]
    old_cp = json.loads((OLD / "CONTRASTIVE_CHECKPOINT_MANIFEST.json").read_text())["checkpoints"]
    assert len(old_cp) == 378
    old_map = {entry["path"]: entry for entry in old_manifest}
    assert all(old_map[cp["checkpoint_path"]]["sha256"] == cp["sha256"] for cp in old_cp)
    delivery = []
    for path in all_files:
        relative = str(path.relative_to(ROOT))
        if relative in EXCLUDED_FILES or path.suffix == ".log":
            continue
        delivery.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha(path)})
    manifest_path = ROOT / "manifests/DELIVERY_SHA256.json"
    manifest_path.write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + "\n")
    result = {"status": "PASS_FOR_COMPLETED_AUTHORIZED_SCOPE_WITH_DOCUMENTED_LIMITATIONS", "root_deliverables": len(REQUIRED_ROOT), "questions_covered": 44, "matrix_count": 42, "matrix_rows": matrix_rows, "inherited_checkpoints_unchanged": 378, "immutable_old_files_rehashed": 1938, "prediction_counts": prediction_counts, "parameters": 462, "grid_conditions": 1722, "sample_type_counts_per_condition": expected_counts, "independent_fusion_audit": independent["status"], "evaluation_audits": "PASS", "pipeline_lineage_audit": lineage["status"], "session_Gold_timing_deviation_disclosed": True, "no_claim_of_whole_session_zero_early_Gold_access": True, "external": external, "scientific_qualification": "DEVELOPMENT_ONLY", "new_training_updates": 0, "new_GPU_calls": 0, "new_model_downloads": 0, "new_LLM_calls": 0, "python_AST_files": source_files, "figure_checks": figure_checks, "total_local_nonvenv_disk_bytes_before_seal": total_disk, "local_disk_guard_bytes": 2000000000, "delivery_file_count": len(delivery), "delivery_sha256": sha(manifest_path), "manifest_exclusions": ["self", "results/FINAL_VALIDATION.json", "venvs", "__pycache__", ".git", "symlinks", "*.log"], "validator_sha256": sha(Path(__file__)), "seconds": time.monotonic() - began}
    output = ROOT / "results/FINAL_VALIDATION.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    # Include the two final output sizes in the disk check, not merely preseal.
    final_disk = sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file() and not p.is_symlink() and not any(part in EXCLUDED_DIRS for part in p.relative_to(ROOT).parts))
    assert final_disk < 2000000000, final_disk
    result["total_local_nonvenv_disk_bytes_after_seal"] = final_disk
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    for entry in delivery:
        assert sha(ROOT / entry["path"]) == entry["sha256"], "Concurrent write detected: " + entry["path"]
    print(json.dumps({key: result[key] for key in ("status", "root_deliverables", "questions_covered", "immutable_old_files_rehashed", "delivery_file_count", "total_local_nonvenv_disk_bytes_after_seal", "seconds")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
