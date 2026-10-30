"""Independent frozen-protocol calibration/prediction audit; never imports fusion.core.

Evaluation Gold is not needed: only each fold's inner validation references are
allowed. Full heldout score/ranking checks use saved matrices and frozen params.
"""
from __future__ import annotations
import os
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "2"
import ast
import builtins
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT.parent / "research3_domain_adaptive_contrastive_learning01"
EXPECTED_PROTOCOL_HASH = "cceb35fc46eaeb5cc4db5973e315ab0a7288cbac5a1d0d1722031944a42289e3"
READS = []


def guarded(base):
    def access(file, *args, **kwargs):
        if isinstance(file, (str, os.PathLike)):
            path = Path(file).resolve()
            mode = str(args[0] if args else kwargs.get("mode", "r"))
            if not any(c in mode for c in "wax"):
                if path.is_relative_to(OLD):
                    assert path.name != "GROUPED_TRAIN_VALIDATION_SPLITS.json"
                    if "reference" in path.name.lower():
                        assert path.parent == OLD / "data/validation" and path.name.endswith("_reference.jsonl")
                READS.append(str(path))
        return base(file, *args, **kwargs)
    return access


builtins.open = guarded(builtins.open)
io.open = guarded(io.open)


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_jsonl(path):
    with path.open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def sorted_columns(matrix):
    # Independent Python ordering, including explicit missing-class handling.
    return np.asarray([sorted(range(len(row)), key=lambda j: (not np.isfinite(row[j]), -row[j] if np.isfinite(row[j]) else 0.0, j)) for row in matrix])


def normalizers(data):
    training = np.flatnonzero(data["partitions"] == "TRAIN")
    prior = np.log1p(data["support"].astype(np.float64))
    arrays = {
        "gte": data["gte_scores"][training].astype(np.float64),
        "b3": data["b3_scores"][training][:, data["seen"]],
        "prior_all": prior,
        "prior_seen": prior[data["seen"]],
    }
    norms = {k: {"mean": float(a.mean()), "sd": max(float(a.std()), 1e-8), "fit_cells": int(a.size)} for k, a in arrays.items()}
    norms["train_sample_ids"] = data["sample_ids"][training].tolist()
    return norms


def compute(data, norms, method, parameters, indices):
    semantic = data["gte_scores"][indices].astype(np.float64)
    supervised = data["b3_scores"][indices]
    seen = data["seen"]
    if method == "Z0":
        return semantic
    if method == "S0":
        return supervised.copy()
    if method == "C0":
        return np.tile(data["support"].astype(np.float64), (len(indices), 1))
    if method == "C1":
        return semantic - parameters["gamma"] * seen.astype(float)[None, :]
    if method == "C2":
        gte_order = sorted_columns(semantic)
        b3_order = sorted_columns(supervised[:, seen])
        semantic_rank = np.empty(gte_order.shape, dtype=np.int64)
        supervised_rank = np.empty(b3_order.shape, dtype=np.int64)
        for i in range(len(indices)):
            semantic_rank[i, gte_order[i]] = np.arange(1, 217)
            supervised_rank[i, b3_order[i]] = np.arange(1, int(seen.sum()) + 1)
        output = 1 / (60 + semantic_rank)
        output[:, seen] += parameters["lambda"] / (60 + supervised_rank)
        return output
    if method in ("C6_B4", "C6_B5"):
        return data["b4_scores" if method == "C6_B4" else "b5_scores"][indices].copy()
    zs = (semantic - norms["gte"]["mean"]) / norms["gte"]["sd"]
    zb = np.zeros(supervised.shape, dtype=np.float64)
    zb[:, seen] = (supervised[:, seen] - norms["b3"]["mean"]) / norms["b3"]["sd"]
    if method in ("C3", "C4"):
        return zs + parameters["lambda"] * zb - parameters.get("gamma", 0) * seen.astype(float)[None, :]
    p = np.log1p(data["support"].astype(np.float64))
    if method == "C5":
        return zs + parameters["alpha"] * ((p - norms["prior_all"]["mean"]) / norms["prior_all"]["sd"])[None, :]
    if method == "P2":
        output = np.full(supervised.shape, np.nan)
        output[:, seen] = zb[:, seen] - parameters["alpha"] * ((p[seen] - norms["prior_seen"]["mean"]) / norms["prior_seen"]["sd"])[None, :]
        return output
    raise AssertionError(method)


def validation_statistics(order, golds, seen, steps):
    grouped = {k: collections.defaultdict(list) for k in ("overall", "seen", "unseen")}
    for row, targets, step in zip(order, golds, steps):
        seen_targets = set(targets).intersection(np.flatnonzero(seen).tolist())
        for key, relevant in (("overall", targets), ("seen", seen_targets), ("unseen", set(targets) - seen_targets)):
            if not relevant:
                continue
            positions = [position + 1 for position, technique in enumerate(row[:10]) if technique in relevant]
            grouped[key][step].append(1.0 / min(positions) if positions else 0.0)
    values = {key: float(np.mean([np.mean(views) for views in step_scores.values()])) if step_scores else None for key, step_scores in grouped.items()}
    s, u = values["seen"], values["unseen"]
    values["H"] = None if s is None or u is None else 2 * s * u / (s + u) if s + u else 0.0
    return values


def same_number(actual, expected, label, max_errors):
    if expected is None:
        assert actual in (None, ""), (label, actual)
    else:
        error = abs(float(actual) - float(expected))
        max_errors[label] = max(max_errors.get(label, 0.0), error)
        assert error <= 1e-14, (label, actual, expected)


def inspect_static_sources():
    files = (ROOT / "fusion/core.py", ROOT / "calibration/fit_calibrators.py", ROOT / "fusion/predict.py")
    source = {p.name: p.read_text() for p in files}
    for name, text in source.items():
        ast.parse(text)
        assert "-1e6" not in text
    assert "tr=d['partitions']=='TRAIN'" in source["core.py"]
    assert "bs=b[:,seen]" in source["core.py"]
    assert "out[:,seen]+=param['lambda']/(60+rb)" in source["core.py"]
    assert "if method in ['C3','C4']" in source["core.py"]
    assert 'refpath=D/\'data/validation\'/f"{meta[\'fold_id\']}_reference.jsonl"' in source["fit_calibrators.py"]
    assert "Forbidden fitting read" in source["fit_calibrators.py"]
    assert "Prediction cannot read reference" in source["predict.py"]
    return {p.name: sha(p) for p in files}


def main():
    start = time.monotonic()
    receipt_path = ROOT / "predictions/PREDICTION_RECEIPT.json"
    assert receipt_path.exists(), "Wait until complete prediction receipt exists; never inspect half-written outputs."
    protocol_path = ROOT / "FUSION_PARAMETER_REGISTRATION.json"
    assert sha(protocol_path) == EXPECTED_PROTOCOL_HASH
    protocol = json.loads(protocol_path.read_text())
    source_hashes = inspect_static_sources()
    fit_receipt = json.loads((ROOT / "calibration/FITTING_RECEIPT.json").read_text())
    prediction_receipt = json.loads(receipt_path.read_text())
    selected_path = ROOT / "calibration/SELECTED_PARAMETERS.json"
    assert sha(selected_path) == fit_receipt["parameters_sha256"] == prediction_receipt["parameters_sha256"]
    assert fit_receipt["protocol_sha256"] == prediction_receipt["protocol_sha256"] == EXPECTED_PROTOCOL_HASH
    assert fit_receipt["source_sha256"] == source_hashes["fit_calibrators.py"]
    assert prediction_receipt["source_sha256"] == source_hashes["predict.py"]
    assert prediction_receipt["core_sha256"] == source_hashes["core.py"]
    expected_validation_paths = {str(OLD / "data/validation" / f"fold_heldout_{fold}_reference.jsonl") for fold in range(1, 8)}
    actual_fit_reference_paths = {p for p in fit_receipt["read_paths"] if "reference" in Path(p).name.lower()}
    assert actual_fit_reference_paths == expected_validation_paths
    assert all(Path(p).name != "GROUPED_TRAIN_VALIDATION_SPLITS.json" for p in fit_receipt["read_paths"])
    assert not any("reference" in Path(p).name.lower() or Path(p).name == "GROUPED_TRAIN_VALIDATION_SPLITS.json" for p in prediction_receipt["read_paths"])
    assert set(prediction_receipt["read_paths"]).isdisjoint(expected_validation_paths)
    assert not fit_receipt["heldout_gold_read"] and not prediction_receipt["gold_read"]
    assert fit_receipt["all_parameters_locked_before_heldout_prediction"]
    assert all(prediction_receipt[k] == 0 for k in ("training_updates", "GPU_calls", "model_downloads", "LLM_calls"))
    selected = json.loads(selected_path.read_text())
    selected_map = {(s["fold_id"], s["seed"], s["view_id"], s["method"]): s for s in selected}
    assert len(selected) == len(selected_map) == 462
    with (ROOT / "calibration/ALL_PARAMETER_CANDIDATES.csv").open() as f:
        grid_records = list(csv.DictReader(f))
    grid_map = {(s["fold_id"], int(s["seed"]), s["view_id"], s["method"], int(s["grid_index"])): s for s in grid_records}
    assert len(grid_records) == len(grid_map) == 1722
    errors = {}
    recalculated = {}
    normalizer_cache = {}
    support_summary = {}
    fallback_reasons = collections.Counter()
    nested_cases = 0
    for matrix_path in sorted((ROOT / "score_matrices").glob("*.npz")):
        meta = json.loads(matrix_path.with_suffix(".json").read_text())
        with np.load(matrix_path, allow_pickle=False) as loaded:
            data = dict(loaded)
        matrix_hash = sha(matrix_path)
        assert matrix_hash == meta["sha256"]
        fid, seed, view = meta["fold_id"], meta["seed"], meta["augmentation"]
        ids = data["technique_ids"].tolist()
        lookup = {t: j for j, t in enumerate(ids)}
        support = np.zeros(216, dtype=int)
        unique_steps = set()
        train_ids = set(data["sample_ids"][data["partitions"] == "TRAIN"].tolist())
        for row in read_jsonl(OLD / "data/train" / f"{fid}_one_view.jsonl"):
            assert row["logical_step_id"] not in unique_steps
            unique_steps.add(row["logical_step_id"])
            assert row["sample_id"] in train_ids and row["sampling_replica_id"] == 0
            for technique in set(row["gold_technique_ids"]):
                support[lookup[technique]] += 1
        assert len(unique_steps) == len(train_ids)
        assert np.array_equal(support, data["support"])
        assert np.array_equal(support > 0, data["seen"])
        norm = normalizers(data)
        normalizer_cache[fid, seed, view] = norm
        valid = np.flatnonzero(data["partitions"] == "VALIDATION")
        ref_path = OLD / "data/validation" / f"{fid}_reference.jsonl"
        ref_sha = sha(ref_path)
        refs = {r["sample_id"]: r for r in read_jsonl(ref_path)}
        assert set(refs) == set(data["sample_ids"][valid])
        assert set(refs).isdisjoint(train_ids)
        assert set(refs).isdisjoint(data["sample_ids"][data["partitions"] == "HELDOUT"].tolist())
        golds = [{lookup[t] for t in refs[s]["gold_technique_ids"]} for s in data["sample_ids"][valid]]
        steps = data["logical_step_ids"][valid].tolist()
        seen = data["seen"]
        counts = {"validation_steps": len(set(steps)), "seen_target_steps": len({step for targets, step in zip(golds, steps) if any(seen[j] for j in targets)}), "unseen_target_steps": len({step for targets, step in zip(golds, steps) if any(not seen[j] for j in targets)})}
        eligible = counts["validation_steps"] >= protocol["selection"]["minimum_validation_steps"] and counts["seen_target_steps"] >= protocol["selection"]["minimum_seen_target_steps"] and counts["unseen_target_steps"] >= protocol["selection"]["minimum_unseen_target_steps"]
        support_summary[fid] = {**counts, "eligible": eligible}
        for method, specification in protocol["methods"].items():
            key = fid, seed, view, method
            saved = selected_map[key]
            assert saved["normalization"] == norm
            assert saved["matrix_sha256"] == matrix_hash
            assert saved["validation_reference_path"] == str(ref_path)
            assert saved["validation_reference_sha256"] == ref_sha
            assert saved["protocol_sha256"] == EXPECTED_PROTOCOL_HASH
            assert saved["fit_source_sha256"] == source_hashes["fit_calibrators.py"]
            assert saved["core_source_sha256"] == source_hashes["core.py"]
            assert not saved["heldout_reference_read"]
            assert all(saved[k] == v for k, v in counts.items())
            candidates = []
            for index, parameters in enumerate(specification["grid"]):
                values = validation_statistics(sorted_columns(compute(data, norm, method, parameters, valid)), golds, seen, steps)
                expected = {"parameters": parameters, "grid_index": index, **values}
                candidates.append(expected)
                grid = grid_map[(*key, index)]
                assert json.loads(grid["parameters"]) == parameters
                for field, label in (("validation_overall_mrr", "overall"), ("validation_seen_mrr", "seen"), ("validation_unseen_mrr", "unseen"), ("validation_H", "H")):
                    same_number(grid[field], values[label], label, errors)
            if len(candidates) == 1:
                choice = candidates[0]
                reason = "FIXED_METHOD"
            elif not eligible:
                choice = next(c for c in candidates if c["parameters"] == specification["default"])
                reason = "REGISTERED_DEFAULT_INSUFFICIENT_VALIDATION_SUPPORT"
            else:
                choice = sorted(candidates, key=lambda c: (-c["H"], -c["overall"], c["grid_index"]))[0]
                reason = "INNER_VALIDATION_H_THEN_MRR_THEN_GRID_ORDER"
            assert saved["parameters"] == choice["parameters"], (key, saved["parameters"], choice)
            assert saved["selection_reason"] == reason
            fallback_reasons[reason] += 1
            for c in candidates:
                record = grid_map[(*key, c["grid_index"])]
                assert (record["selected"] == "True") == (c["grid_index"] == choice["grid_index"])
                expected_rejection = "" if c["grid_index"] == choice["grid_index"] else "NOT_SELECTED_BY_FROZEN_RULE" if eligible else "INSUFFICIENT_SUPPORT_DEFAULT_ONLY"
                assert record["rejection_reason"] == expected_rejection
            recalculated[key] = choice["parameters"]
        for strength in (0, .25, .5, 1):
            assert np.array_equal(compute(data, norm, "C3", {"lambda": strength}, valid), compute(data, norm, "C4", {"lambda": strength, "gamma": 0}, valid))
            nested_cases += 1
        print("INDEPENDENT_CALIBRATION_PASS", fid, seed, view, flush=True)
    scores_checked = 0
    max_score_error = 0.0
    counts_by_file = {}
    for relative_path, expected_count, hash_key in (("FUSION_PREDICTIONS.jsonl", 64350, "main_prediction_sha256"), ("predictions/TRADEOFF_PREDICTIONS.jsonl", 23400, "tradeoff_sha256")):
        path = ROOT / relative_path
        assert sha(path) == prediction_receipt[hash_key]
        last_context = None
        actual_context_rows = set()
        all_keys = set()
        row_count = 0
        for row in read_jsonl(path):
            key = row["fold_id"], row["seed"], row["view_id"], row["method"]
            params = recalculated[key]
            tradeoff = relative_path.startswith("predictions/")
            if tradeoff:
                assert row["method"] == "C4" and row["tradeoff_only"]
                assert row["gamma"] in protocol["tradeoff"]["gamma"]
                params = {"lambda": params["lambda"], "gamma": row["gamma"]}
            context = (*key, json.dumps(params, sort_keys=True))
            if context != last_context:
                if last_context is not None:
                    assert actual_context_rows == expected_context_rows
                source = selected_map[key]
                with np.load(ROOT / source["matrix_path"], allow_pickle=False) as loaded:
                    current = dict(loaded)
                held = np.flatnonzero(current["partitions"] == "HELDOUT")
                values = compute(current, normalizer_cache[key[:3]], key[3], params, held)
                orders = sorted_columns(values)
                ids = current["technique_ids"].tolist()
                row_lookup = {str(current["sample_ids"][i]): j for j, i in enumerate(held)}
                expected_context_rows = set(row_lookup)
                actual_context_rows = set()
                last_context = context
            sample = row["sample_id"]
            assert sample in row_lookup and sample not in actual_context_rows
            actual_context_rows.add(sample)
            unique = (*context, sample)
            assert unique not in all_keys
            all_keys.add(unique)
            j = row_lookup[sample]
            assert row["logical_step_id"] == str(current["logical_step_ids"][held[j]])
            assert row["chosen_parameters"] == params
            assert row["selection_reason"] == selected_map[key]["selection_reason"]
            assert row["evaluation_partition"] == "HELDOUT"
            assert row["score_column_order"] == "LEXICOGRAPHIC_TECHNIQUE_ID"
            assert len(row["scores_all216"]) == 216
            scores = np.array([np.nan if value is None else value for value in row["scores_all216"]])
            assert np.array_equal(np.isnan(scores), np.isnan(values[j]))
            finite = np.isfinite(values[j])
            error = float(np.max(np.abs(scores[finite] - values[j, finite])))
            max_score_error = max(max_score_error, error)
            assert error <= 1e-12, (key, sample, error)
            expected_ranking = [ids[k] for k in orders[j]]
            assert row["ranking_all216"] == expected_ranking
            assert row["predictions"] == expected_ranking[:10]
            assert len(set(row["ranking_all216"])) == 216
            scores_checked += 216
            row_count += 1
        assert actual_context_rows == expected_context_rows
        assert row_count == expected_count
        counts_by_file[relative_path] = row_count
        print("INDEPENDENT_PREDICTIONS_PASS", relative_path, row_count, flush=True)
    result = {"status": "PASS_WITH_SCOPE_LIMITATIONS", "protocol_sha256": EXPECTED_PROTOCOL_HASH, "source_hashes": source_hashes, "matrix_configurations": 42, "selected_conditions": 462, "grid_validation_conditions": 1722, "normalization_recomputed_train_only": True, "unique_train_step_support_recomputed": True, "validation_metric_max_abs_errors": errors, "selected_parameter_mismatches": 0, "selection_reason_counts": dict(fallback_reasons), "validation_qualification_by_fold": support_summary, "C3_equals_C4_gamma0_checked_conditions": nested_cases, "prediction_rows_checked": counts_by_file, "full216_score_cells_checked": scores_checked, "prediction_score_max_abs_error": max_score_error, "ranking_mismatches": 0, "fitter_reference_read_paths": sorted(actual_fit_reference_paths), "predictor_reference_reads": [], "auditor_reference_paths": sorted({p for p in READS if 'reference' in Path(p).name.lower()}), "heldout_reference_read": False, "old_split_with_label_summaries_read_by_fitter_predictor_or_auditor": False, "fit_parameter_hash_verified_before_prediction": True, "new_training_updates": 0, "new_GPU_calls": 0, "new_LLM_calls": 0, "new_model_downloads": 0, "limitations": ["Audit verifies computation and input isolation, not heldout metric efficacy or external generalization.", "Read traces and source inspection are application-level evidence, not an operating-system access-control guarantee.", "Seven exposed scenarios retain development-only status; no confirmatory significance inference."], "seconds": time.monotonic() - start, "auditor_sha256": sha(Path(__file__))}
    (ROOT / "results/FUSION_INDEPENDENT_AUDIT.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    table = "\n".join(f"| {f} | {d['validation_steps']} | {d['seen_target_steps']} | {d['unseen_target_steps']} | {d['eligible']} |" for f, d in sorted(support_summary.items()))
    text = f"""# 融合与校准独立复算\n\n状态：PASS_WITH_SCOPE_LIMITATIONS。独立脚本未导入fusion.core，也未打开外层保留Gold。冻结登记SHA-256为{EXPECTED_PROTOCOL_HASH}，与拟合和预测回执一致。\n\n已重新计算42配置的全部归一化统计、1722组内部验证指标、462个选中条件，选参差异0。归一化只使用TRAIN唯一训练步骤r0；Seen与频率支持直接从每折one_view训练标签重新统计。内部验证先在每一步内平均5次采样，再对步骤平均Seen/Unseen MRR，随后求H；按H、总体MRR和登记顺序选择。未达10步骤与Seen/Unseen各3步骤时使用登记默认值。\n\n| 折 | 内验证步骤 | Seen目标步骤 | Unseen目标步骤 | 允许选参 |\n|---|---:|---:|---:|---|\n{table}\n\n选择原因计数：{dict(fallback_reasons)}。全部验证指标最大数值差{max(errors.values()):.17g}；不是利用外层保留Gold重新选择。\n\n11种主条件64350条及4个固定gamma敏感性条件23400条，共{scores_checked}个216列分数逐项复算；最大绝对差{max_score_error:.17g}，完整216排名差异0。B3缺失类别保持NaN/null及末尾字典序，不进入监督残差；RRF只在Seen列产生监督排名贡献。C3与C4(gamma=0)在168种配置/强度对照中精确相同，明确属于嵌套简单方法。\n\n实际拟合read_paths中的reference只包含7个对应fold validation_reference。逐selected记录的路径、hash、矩阵fold与代码当前fold路径构造一致；预测read_paths没有任何reference或旧split。校准、预测和独立审核均未读取附带heldout标签摘要的旧split JSON。归一化train ID与heldout/validation互斥；参数文件hash在预测启动时与拟合回执一致。代码与read_paths提供应用级可审计证据，不能替代操作系统级访问证明。\n\n本审计仅确认计算、登记一致性与输入隔离，不根据分数宣称模型有效，也不替代独立指标审核。当前实验仍为DEVELOPMENT_ONLY。\n"""
    (ROOT / "reports/FUSION_INDEPENDENT_AUDIT.md").write_text(text)
    print(json.dumps({k: v for k, v in result.items() if not k.endswith("paths")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
