"""Read-only inherited model inference; no optimization or evaluation-Gold access.

Use Python -B. CPU thread caps are established before importing NumPy.
Only training Gold is consumed to construct support/availability. Input text is
not used: immutable vectors and existing input hashes supply all model inputs.
"""
from __future__ import annotations
import os
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "2"
import collections
import csv
import hashlib
import json
from pathlib import Path
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / "research3_domain_adaptive_contrastive_learning01"
KNOWLEDGE_VERSION = "ATTACK_16_1"
METHODS = ("B3", "B4", "B5")
PARTITIONS = ("TRAIN", "VALIDATION", "HELDOUT")
HISTORICAL_PARTITION = {"TRAIN": "TRAIN_DIAGNOSTIC_R0", "VALIDATION": "INNER_VALIDATION", "HELDOUT": "HELDOUT"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def read_jsonl(path: Path):
    with path.open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def metadata(path: Path, training: bool = False) -> list[dict]:
    result = []
    for record in read_jsonl(path):
        # Explicit allowlist prevents text or any incidental answer fields from
        # propagating to inference. Gold is allowed solely in training rows.
        row = {key: record[key] for key in ("sample_id", "logical_step_id", "scenario_id", "sampling_replica_id", "input_hash", "knowledge_version")}
        assert row["knowledge_version"] == KNOWLEDGE_VERSION
        assert row["logical_step_id"] not in {"1-35", "1-36", "1-37"}
        assert "CONV-A01" not in row["sample_id"]
        if training:
            row["gold_technique_ids"] = record["gold_technique_ids"]
        else:
            assert "gold_technique_ids" not in record
        result.append(row)
    return result


def project(x, knowledge, wl, wt):
    left, right = x @ wl, knowledge @ wt
    left = left / np.maximum(np.linalg.norm(left, axis=1, keepdims=True), 1e-8)
    right = right / np.maximum(np.linalg.norm(right, axis=1, keepdims=True), 1e-8)
    return left @ right.T / .1


def ranking(scores: np.ndarray, ids: list[str]) -> list[str]:
    # ids already sorted; stable sort implements lexicographic ID tie-breaking.
    return [ids[j] for j in np.argsort(-scores, kind="stable")]


def csv_write(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(dict.fromkeys(key for row in rows for key in row)))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    started = time.monotonic()
    (ROOT / "inherited").mkdir(exist_ok=True)
    delivery_path = OLD / "manifests/DELIVERY_SHA256.json"
    delivery = json.loads(delivery_path.read_text())
    assert len(delivery) == 1938
    verified = []
    for entry in delivery:
        path = OLD / entry["path"]
        assert path.is_file() and path.stat().st_size == entry["bytes"], entry["path"]
        observed = sha(path)
        assert observed == entry["sha256"], entry["path"]
        verified.append({**entry, "verification": "MATCH"})
    write_json(ROOT / "inherited/DELIVERY_HASH_VERIFICATION.json", {"status": "PASS", "source_root": str(OLD), "source_manifest_sha256": sha(delivery_path), "checked_files": len(verified), "entries": verified})
    checkpoints_path = OLD / "CONTRASTIVE_CHECKPOINT_MANIFEST.json"
    checkpoint_manifest = json.loads(checkpoints_path.read_text())
    checkpoints = checkpoint_manifest["checkpoints"]
    assert len(checkpoints) == 378
    actual_cp = list((OLD / "checkpoints").rglob("*.npz"))
    assert len(actual_cp) == 378
    checkpoint_results = []
    for item in checkpoints:
        path = OLD / item["checkpoint_path"]
        assert sha(path) == item["sha256"] and path.stat().st_size == item["bytes"]
        with np.load(path, allow_pickle=False) as cp:
            assert cp.files
            for key in cp.files:
                values = cp[key]
                if np.issubdtype(values.dtype, np.number):
                    assert np.isfinite(values).all(), (path.name, key)
        checkpoint_results.append({**item, "reload_numeric_finiteness": "PASS", "inheritance": "READ_ONLY_PATH_REFERENCE"})
    write_json(ROOT / "inherited/CHECKPOINT_VERIFICATION.json", {"status": "PASS", "count": len(checkpoints), "counts_by_method": dict(collections.Counter(r["method"] for r in checkpoints)), "checkpoints": checkpoint_results})
    print("INHERITED_HASHES_AND_378_CHECKPOINTS_PASS", flush=True)

    split_path = OLD / "GROUPED_TRAIN_VALIDATION_SPLITS.json"
    # Historical split files contain historical evaluation summaries. Only this
    # explicit field whitelist is propagated, never heldout label inventories.
    raw_splits = json.loads(split_path.read_text())["folds"]
    folds = [{key: fold[key] for key in ("fold_id", "heldout_scenario", "validation_scenario", "train_scenarios", "paths", "one_view_train_path", "train_sample_ids", "validation_sample_ids", "heldout_sample_ids")} for fold in raw_splits]
    del raw_splits
    for fold in folds:
        fold["paths"] = {key: value for key, value in fold["paths"].items() if key in ("train", "validation_inputs", "heldout_inputs")}
    write_json(ROOT / "inherited/SPLITS_WITHOUT_EVALUATION_LABEL_SUMMARIES.json", {"source_sha256": sha(split_path), "folds": folds, "evaluation_reference_paths_removed": True})
    feature_path = OLD / "embeddings/FROZEN_GTE_FEATURES.npz"
    feature_hash = sha(feature_path)
    extraction = json.loads((OLD / "embeddings/FEATURE_EXTRACTION_RECEIPT.json").read_text())
    assert extraction["feature_sha256"] == feature_hash
    with np.load(feature_path, allow_pickle=False) as feature:
        sample_ids = feature["sample_ids"].tolist()
        ids = feature["technique_ids"].tolist()
        log_vectors = feature["log_vectors"].copy()
        knowledge_vectors = feature["knowledge_vectors"].copy()
        input_hashes = dict(zip(sample_ids, feature["input_hashes"].tolist()))
        knowledge_hashes = feature["knowledge_hashes"].tolist()
    assert log_vectors.shape == (975, 768) and knowledge_vectors.shape == (216, 768)
    assert log_vectors.dtype == knowledge_vectors.dtype == np.float32
    assert len(set(sample_ids)) == 975 and len(set(ids)) == 216 and ids == sorted(ids)
    assert np.isfinite(log_vectors).all() and np.isfinite(knowledge_vectors).all()
    assert np.allclose(np.linalg.norm(log_vectors, axis=1), 1, atol=2e-6)
    assert np.allclose(np.linalg.norm(knowledge_vectors, axis=1), 1, atol=2e-6)
    knowledge = json.loads((OLD / "data/KNOWLEDGE_K2.json").read_text())
    assert knowledge_hashes == [hashlib.sha256(knowledge[t].encode()).hexdigest() for t in ids]
    assert ids == sorted(json.loads((OLD / "data/CANDIDATE_TECHNIQUE_IDS.json").read_text()))
    sample_index = {sample: i for i, sample in enumerate(sample_ids)}
    technique_index = {technique: i for i, technique in enumerate(ids)}
    gte = log_vectors @ knowledge_vectors.T
    assert gte.dtype == np.float32 and np.isfinite(gte).all()
    old_b1 = {r["sample_id"]: r for r in read_jsonl(OLD / "results/runs_frozen/B1_predictions.jsonl")}
    assert set(old_b1) == set(sample_ids)
    differences = []
    b1_max_delta = 0.0
    for sample, scores in zip(sample_ids, gte):
        old = old_b1[sample]
        order = ranking(scores, ids)
        top10_scores = [float(scores[technique_index[t]]) for t in old["predictions"]]
        delta = float(np.max(np.abs(np.array(top10_scores) - old["scores_top10"])))
        b1_max_delta = max(b1_max_delta, delta)
        if order != old["ranking_all216"] or delta != 0:
            differences.append({"method": "B1", "sample_id": sample, "ranking_equal": order == old["ranking_all216"], "max_abs_saved_top10_score_difference": delta, "new_ranking": order, "historical_ranking": old["ranking_all216"]})
    comparisons = [{"method": "B1", "configurations": 1, "rows": 975, "ranking_mismatches": sum(not d["ranking_equal"] for d in differences), "score_mismatches": sum(d["max_abs_saved_top10_score_difference"] != 0 for d in differences), "max_abs_saved_top10_score_difference": b1_max_delta}]
    source_binding = {"feature_sha256": feature_hash, "protocol_sha256": sha(OLD / "manifests/TRAINING_PROTOCOL.json"), "trainer_sha256": sha(OLD / "contrastive/train_heads.py"), "math_source_sha256": sha(OLD / "contrastive/numpy_models.py")}
    matrix_manifest = []
    inventory, priors = [], []
    fold_summary = []
    frozen_rows = 0
    b3_rows = 0
    with (ROOT / "FROZEN_GTE_SCORES.jsonl").open("w") as gte_out, (ROOT / "B3_SUPERVISED_SCORES.jsonl").open("w") as b3_out:
        for fold in folds:
            fid = fold["fold_id"]
            rows = {
                "TRAIN": sorted(metadata(OLD / fold["one_view_train_path"], training=True), key=lambda r: r["logical_step_id"]),
                "VALIDATION": metadata(OLD / fold["paths"]["validation_inputs"]),
                "HELDOUT": metadata(OLD / fold["paths"]["heldout_inputs"]),
            }
            assert all(r["sampling_replica_id"] == 0 for r in rows["TRAIN"])
            assert len({r["logical_step_id"] for r in rows["TRAIN"]}) == len(rows["TRAIN"])
            for partition, records in rows.items():
                assert len({r["sample_id"] for r in records}) == len(records)
                for r in records:
                    assert input_hashes[r["sample_id"]] == r["input_hash"]
                    if partition == "TRAIN":
                        assert r["scenario_id"] in fold["train_scenarios"]
                    else:
                        expected = fold["validation_scenario"] if partition == "VALIDATION" else fold["heldout_scenario"]
                        assert r["scenario_id"] == expected
            assert set(r["sample_id"] for r in rows["VALIDATION"]) == set(fold["validation_sample_ids"])
            assert set(r["sample_id"] for r in rows["HELDOUT"]) == set(fold["heldout_sample_ids"])
            assert set(fold["train_sample_ids"]) == {f"{r['logical_step_id']}-r{i}" for r in rows["TRAIN"] for i in range(5)}
            support = np.zeros(216, dtype=np.int64)
            for r in rows["TRAIN"]:
                for technique in set(r["gold_technique_ids"]):
                    support[technique_index[technique]] += 1
            seen = support > 0
            seen_columns = np.flatnonzero(seen)
            n_train = len(rows["TRAIN"])
            fold_summary.append({"fold_id": fid, "seen_techniques": int(seen.sum()), "unseen_techniques": int((~seen).sum()), "unique_train_steps": n_train, "train_r0_rows": n_train, "validation_rows": len(rows["VALIDATION"]), "heldout_rows": len(rows["HELDOUT"])})
            for j, technique in enumerate(ids):
                base = {"fold_id": fid, "candidate_technique_id": technique, "candidate_seen_in_training": bool(seen[j]), "training_class_support": int(support[j]), "training_step_count": n_train, "support_unit": "UNIQUE_TRAIN_LOGICAL_STEP", "knowledge_version": KNOWLEDGE_VERSION}
                inventory.append(base)
                priors.append({**base, "training_step_frequency": float(support[j] / n_train), "training_label_mass_fraction": float(support[j] / support.sum()), "laplace_add_one_step_prevalence": float((support[j] + 1) / (n_train + 2)), "laplace_add_one_categorical_mass": float((support[j] + 1) / (support.sum() + 216)), "source_train_one_view_sha256": sha(OLD / fold["one_view_train_path"])})
            ordered_rows = [(partition, row) for partition in PARTITIONS for row in rows[partition]]
            sample_order = [r["sample_id"] for _, r in ordered_rows]
            for partition, r in ordered_rows:
                record = {"fold_id": fid, "seed": "FROZEN", "view_id": "SHARED_ONE_MULTI", "sample_id": r["sample_id"], "logical_step_id": r["logical_step_id"], "partition": partition, "technique_ids": ids, "frozen_gte_scores": gte[sample_index[r["sample_id"]]].astype(float).tolist(), "candidate_seen_in_training": seen.tolist(), "training_class_support": support.tolist(), "knowledge_version": KNOWLEDGE_VERSION}
                gte_out.write(json.dumps(record, separators=(",", ":"), allow_nan=False) + "\n")
                frozen_rows += 1
            matrix_x = {partition: np.stack([log_vectors[sample_index[r["sample_id"]]] for r in rows[partition]]).astype(np.float64) for partition in PARTITIONS}
            for seed in (17, 42, 73):
                for augmentation in ("ONE_VIEW_PER_STEP", "MULTI_VIEW_AUGMENTATION"):
                    stem = f"{fid}_seed{seed}_{augmentation}"
                    matrices = {}
                    configuration_sources = {}
                    for method in METHODS:
                        cp_path = OLD / "checkpoints/heads" / f"{method}_{stem}.npz"
                        pred_path = OLD / "results/runs_heads" / f"{method}_{stem}_predictions.jsonl"
                        saved_rows = {(r["evaluation_partition"], r["sample_id"]): r for r in read_jsonl(pred_path)}
                        assert len(saved_rows) == len(ordered_rows)
                        with np.load(cp_path, allow_pickle=False) as cp:
                            assert cp["ids"].tolist() == ids
                            for key, value in source_binding.items():
                                assert cp[key].item() == value
                            assert cp["train_file_sha256"].item() == sha(OLD / fold["paths"]["train"])
                            assert cp["train_ids_sha256"].item() == hashlib.sha256(json.dumps(sorted(fold["train_sample_ids"])).encode()).hexdigest()
                            if method == "B3":
                                assert np.array_equal(cp["seen"], seen_columns)
                                assert cp["w"].shape == (768, len(seen_columns)) and cp["b"].shape == (len(seen_columns),)
                                part_scores = {}
                                for partition in PARTITIONS:
                                    score = np.full((len(rows[partition]), 216), np.nan, dtype=np.float64)
                                    score[:, seen_columns] = matrix_x[partition] @ cp["w"] + cp["b"]
                                    part_scores[partition] = score
                                assert all(np.isnan(s[:, ~seen]).all() and np.isfinite(s[:, seen]).all() for s in part_scores.values())
                            else:
                                part_scores = {partition: project(matrix_x[partition], knowledge_vectors.astype(np.float64), cp["wl"], cp["wt"]) for partition in PARTITIONS}
                                assert all(np.isfinite(s).all() for s in part_scores.values())
                        stats = {"method": method, "fold_id": fid, "seed": seed, "view_id": augmentation, "rows": len(ordered_rows), "ranking_mismatches": 0, "score_mismatches": 0, "max_abs_saved_top10_score_difference": 0.0}
                        for partition in PARTITIONS:
                            for r, score in zip(rows[partition], part_scores[partition]):
                                historical = saved_rows[HISTORICAL_PARTITION[partition], r["sample_id"]]
                                # Historical sentinel is recreated exclusively to
                                # compare old rankings. It never enters matrices.
                                comparison_score = np.where(seen, score, -1e6) if method == "B3" else score
                                order = ranking(comparison_score, ids)
                                delta = float(np.max(np.abs(np.asarray([comparison_score[technique_index[t]] for t in historical["predictions"]]) - historical["scores_top10"])))
                                ranking_equal = order == historical["ranking_all216"]
                                stats["ranking_mismatches"] += int(not ranking_equal)
                                stats["score_mismatches"] += int(delta != 0)
                                stats["max_abs_saved_top10_score_difference"] = max(stats["max_abs_saved_top10_score_difference"], delta)
                                if not ranking_equal or delta != 0:
                                    differences.append({"method": method, "fold_id": fid, "seed": seed, "view_id": augmentation, "partition": partition, "sample_id": r["sample_id"], "ranking_equal": ranking_equal, "max_abs_saved_top10_score_difference": delta, "new_ranking": order, "historical_ranking": historical["ranking_all216"]})
                                if method == "B3":
                                    record = {"fold_id": fid, "seed": seed, "view_id": augmentation, "sample_id": r["sample_id"], "logical_step_id": r["logical_step_id"], "partition": partition, "technique_ids": ids, "supervised_b3_scores": [float(v) if available else None for v, available in zip(score, seen)], "supervised_score_available": seen.tolist(), "candidate_seen_in_training": seen.tolist(), "training_class_support": support.tolist(), "unavailable_status": "NO_SUPERVISED_CLASSIFIER", "knowledge_version": KNOWLEDGE_VERSION}
                                    b3_out.write(json.dumps(record, separators=(",", ":"), allow_nan=False) + "\n")
                                    b3_rows += 1
                        comparisons.append(stats)
                        matrices[method.lower() + "_scores"] = np.vstack([part_scores[p] for p in PARTITIONS])
                        configuration_sources[method] = {"checkpoint_path": str(cp_path), "checkpoint_sha256": sha(cp_path), "historical_predictions_sha256": sha(pred_path)}
                    target = ROOT / "score_matrices" / f"{stem}.npz"
                    np.savez_compressed(target, sample_ids=np.asarray(sample_order), logical_step_ids=np.asarray([r["logical_step_id"] for _, r in ordered_rows]), partitions=np.asarray([p for p, _ in ordered_rows]), technique_ids=np.asarray(ids), gte_scores=gte[[sample_index[s] for s in sample_order]], seen=seen, support=support, **matrices)
                    with np.load(target, allow_pickle=False) as saved:
                        assert saved["gte_scores"].dtype == np.float32
                        assert saved["b3_scores"].dtype == np.float64
                        assert np.isnan(saved["b3_scores"][:, ~seen]).all()
                        assert np.isfinite(saved["b3_scores"][:, seen]).all()
                        assert all(saved[key].shape == (len(sample_order), 216) for key in ("gte_scores", "b3_scores", "b4_scores", "b5_scores"))
                    meta = {"fold_id": fid, "seed": seed, "augmentation": augmentation, "knowledge_version": KNOWLEDGE_VERSION, "knowledge_sha256": sha(OLD / "data/KNOWLEDGE_K2.json"), "source_feature_sha256": feature_hash, "source_split_sha256": sha(split_path), "source_train_one_view_sha256": sha(OLD / fold["one_view_train_path"]), "source_train_sha256": sha(OLD / fold["paths"]["train"]), "source_validation_inputs_sha256": sha(OLD / fold["paths"]["validation_inputs"]), "source_heldout_inputs_sha256": sha(OLD / fold["paths"]["heldout_inputs"]), "model_revision": extraction["model_revision"], "weight_sha256": extraction["weight_sha256"], "source_models": configuration_sources, "path": str(target.relative_to(ROOT)), "sha256": sha(target), "bytes": target.stat().st_size, "rows": len(sample_order), "columns": 216, "partition_rows": {p: len(rows[p]) for p in PARTITIONS}, "B3_missing_representation": "NaN; availability=seen; no supervised classifier; never sentinel in fusion", "row_order": list(PARTITIONS), "column_order": "LEXICOGRAPHIC_TECHNIQUE_ID", "heldout_reference_read": False, "validation_reference_read": False, "new_training_updates": 0, "new_GPU_calls": 0}
                    write_json(target.with_suffix(".json"), meta)
                    matrix_manifest.append(meta)
                    print("SCORE_MATRIX_READY", stem, len(sample_order), flush=True)
    csv_write(ROOT / "SEEN_CLASS_INVENTORY_BY_FOLD.csv", inventory)
    csv_write(ROOT / "TRAINING_CLASS_PRIORS.csv", priors)
    csv_write(ROOT / "inherited/FOLD_SUPPORT_SUMMARY.csv", fold_summary)
    csv_write(ROOT / "inherited/PREDICTION_RECONSTRUCTION_COMPARISON.csv", comparisons)
    with (ROOT / "inherited/PREDICTION_RECONSTRUCTION_DIFFERENCES.jsonl").open("w") as f:
        for row in differences:
            f.write(json.dumps(row, allow_nan=False) + "\n")
    summary = {"status": "SCORE_RECONSTRUCTION_READY", "old_manifest_entries_verified": len(verified), "checkpoints_verified": len(checkpoints), "model_forward_configurations": 126, "matrix_files": len(matrix_manifest), "frozen_gte_jsonl_rows": frozen_rows, "b3_jsonl_rows": b3_rows, "b3_matrix_rows": sum(m["rows"] for m in matrix_manifest), "comparison_rows": sum(s["rows"] for s in comparisons), "ranking_mismatch_rows": sum(s["ranking_mismatches"] for s in comparisons), "nonzero_score_difference_rows": sum(s["score_mismatches"] for s in comparisons), "max_abs_saved_top10_score_difference": max(s["max_abs_saved_top10_score_difference"] for s in comparisons), "seconds": time.monotonic() - started, "numpy_version": np.__version__, "old_assets_mutated": False, "new_training_updates": 0, "new_GPU_forward_calls": 0, "new_model_downloads": 0, "validation_reference_read": False, "heldout_reference_read": False, "known_metadata_limitation": "Original split JSON includes historical heldout-label summaries; explicit whitelist removes them before use. No evaluation reference file was opened and no heldout label field was used.", "source_sha256": sha(Path(__file__))}
    write_json(ROOT / "inherited/SCORE_RECONSTRUCTION_VALIDATION.json", summary)
    write_json(ROOT / "FULL_216_SCORE_MATRIX_MANIFEST.json", {**summary, "old_source_root": str(OLD), "knowledge_version": KNOWLEDGE_VERSION, "candidate_count": 216, "source_hashes": source_binding, "score_definitions": {"gte_scores": "float32 saved log_vectors @ saved knowledge_vectors.T", "b3_scores": "float64 X @ W + b for train-seen columns, NaN otherwise", "b4_scores": "float64 cosine(X @ WL, K @ WT) / 0.1", "b5_scores": "float64 cosine(X @ WL, K @ WT) / 0.1"}, "matrices": matrix_manifest, "jsonl_exports": [{"path": n, "sha256": sha(ROOT / n), "bytes": (ROOT / n).stat().st_size} for n in ("FROZEN_GTE_SCORES.jsonl", "B3_SUPERVISED_SCORES.jsonl")]})
    table = "\n".join(f"| {r['fold_id']} | {r['unique_train_steps']} | {r['seen_techniques']} | {r['unseen_techniques']} | {r['validation_rows']} | {r['heldout_rows']} |" for r in fold_summary)
    report = f"""# 冻结模型继承与完整分数重建审计\n\n状态：SCORE_RECONSTRUCTION_READY。旧交付清单1938项内容SHA-256及字节数全部匹配；378份checkpoint全部存在、哈希相符、可加载且数值有限。通过只读绝对路径继承，未复制或改写旧权重。\n\n复用真实975×768日志向量与216×768公开技术向量；没有新GPU前向、模型下载、训练更新或LLM调用。ATT&CK知识版本为ATTACK_16_1；源知识及模型修订、权重、特征、训练代码、split与各checkpoint哈希见FULL_216_SCORE_MATRIX_MANIFEST.json。\n\n| 折 | 唯一训练步 | Seen技术 | Unseen技术 | 内验证查询 | 外保留查询 |\n|---|---:|---:|---:|---:|---:|\n{table}\n\nSeen/support仅逐折读取合法one_view_train的标签，支持单位为唯一逻辑步骤。五个replica未重复计数。训练r0、全部内验证及全部外保留查询分别按旧推理批次形状计算，输出42份统一NPZ、126个B3/B4/B5模型条件。各NPZ的完整列顺序固定为216技术ID字典序。训练和验证/保留元数据字段经过白名单，仅训练Gold进入类别统计；没有打开内验证/外保留reference文件。历史split JSON本身包含旧标签汇总，程序只取字段白名单，未使用这些汇总。\n\nB3在未见类别无分类器：NPZ写NaN、JSON写null，availability=false，状态NO_SUPERVISED_CLASSIFIER。旧-1e6只在历史输出复算副本内重建以核对旧排名，未写入可融合B3矩阵。这确认STRUCTURAL_UNSEEN_EXCLUSION，而非GTE主干遗忘。B4/B5为所有216类计算有效投影分数，其未见排序退化需要后续独立评价解释。\n\n共比较{summary['comparison_rows']}条历史预测（含B1全部975条以及B3/B4/B5训练r0、内验证和外保留行），完整216排名差异{summary['ranking_mismatch_rows']}条，已保存Top10分数非零差异{summary['nonzero_score_difference_rows']}条，最大绝对差{summary['max_abs_saved_top10_score_difference']:.17g}。逐条差异保留于inherited/PREDICTION_RECONSTRUCTION_DIFFERENCES.jsonl；不修分数、不改排序。历史文件仅保存Top10分数与Top216排名，所以数值一致性核验限于保存的Top10位置；完整216数值来自真实checkpoint重新前向，未由Top10反推。\n\nNPZ内含sample_ids、logical_step_ids、partitions、technique_ids、gte_scores（float32）、b3_scores/b4_scores/b5_scores（float64）、seen与support。partitions为TRAIN、VALIDATION、HELDOUT。JSONL为查询级向量格式，每行的technique_ids与各score/support/availability列表逐位对齐；不含该查询Gold。FROZEN_GTE_SCORES有{frozen_rows}行，B3_SUPERVISED_SCORES有{b3_rows}行。\n\nTRAINING_CLASS_PRIORS保存训练步prevalence、标签总质量比例以及明确命名的Laplace平滑列；这些是统计输出，具体融合用哪一列由主任务预注册，不在本脚本内根据结果选择。\n\n本重建器未执行新融合、参数选择或性能评估。新结果资格仍为已曝光场景的开发研究。\n"""
    (ROOT / "INHERITED_MODEL_SCORE_AUDIT.md").write_text(report)
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
