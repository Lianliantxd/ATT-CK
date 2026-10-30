"""Independent audit of trained heads; never optimizes, mutates CPs or connects remotely."""
from __future__ import annotations
import os
for _name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_name] = '2'
import hashlib
import json
from pathlib import Path
from collections import defaultdict
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
METHODS = ('B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B9_CONST')
WEIGHT_SHA = '3e85899d5728cb7de79781c0c3acfb91ccef9f875f1f7e0b3c9f3dd4b6a724ba'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arrsha(values: list[np.ndarray]) -> str:
    return hashlib.sha256(b''.join(x.tobytes() for x in values)).hexdigest()


def load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def projected(logs: np.ndarray, knowledge: np.ndarray, wl: np.ndarray, wt: np.ndarray) -> np.ndarray:
    left, right = logs @ wl, knowledge @ wt
    left /= np.maximum(np.linalg.norm(left, axis=1, keepdims=True), 1e-8)
    right /= np.maximum(np.linalg.norm(right, axis=1, keepdims=True), 1e-8)
    return left @ right.T / .1


def main() -> None:
    assert (ROOT/'results/HEADS_MATRIX_COMPLETE.json').exists(), 'Wait for parent confirmation and actual completed matrix'
    complete = json.loads((ROOT/'results/HEADS_MATRIX_COMPLETE.json').read_text())
    assert complete['configurations'] == 336 and complete['total_optimizer_updates'] == 40320
    protocol_path = ROOT/'manifests/TRAINING_PROTOCOL.json'
    protocol = json.loads(protocol_path.read_text())
    assert protocol['epochs'] == 120 and protocol['seeds'] == [17, 42, 73]
    assert protocol['B4_B9']['projection_dim'] == 32 and protocol['B4_B9']['temperature'] == .1
    split_path = ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json'
    assert protocol['split_file_sha256'] == sha(split_path)
    splits = json.loads(split_path.read_text())['folds']
    feature_path = ROOT/'embeddings/FROZEN_GTE_FEATURES.npz'
    feature_sha = sha(feature_path)
    extraction_path = ROOT/'embeddings/FEATURE_EXTRACTION_RECEIPT.json'
    extraction = json.loads(extraction_path.read_text())
    assert extraction['status'] == 'COMPLETE_FROZEN_FEATURES_ONLY'
    assert extraction['weight_sha256'] == WEIGHT_SHA and extraction['feature_sha256'] == feature_sha
    assert extraction['model_revision'] == 'e7f32e3c00f91d699e8c43b53106206bcc72bb22'
    assert extraction['trainable_parameters'] == 0 and not extraction['Gold_loaded'] and extraction['new_model_downloads'] == 0
    assert extraction['source_sha256'] == sha(ROOT/'embeddings/extract_frozen_gte.py')
    with np.load(feature_path, allow_pickle=False) as features:
        log_vectors = features['log_vectors'].copy()
        knowledge_vectors = features['knowledge_vectors'].astype(np.float64)
        sample_ids = features['sample_ids'].tolist()
        ids = features['technique_ids'].tolist()
        input_hashes = dict(zip(sample_ids, features['input_hashes'].tolist()))
        knowledge_hashes = features['knowledge_hashes'].tolist()
    assert log_vectors.shape == (975, 768) and knowledge_vectors.shape == (216, 768)
    assert log_vectors.dtype == np.float32 and np.isfinite(log_vectors).all() and np.isfinite(knowledge_vectors).all()
    assert len(set(sample_ids)) == 975 and ids == sorted(json.loads((ROOT/'data/CANDIDATE_TECHNIQUE_IDS.json').read_text()))
    knowledge = json.loads((ROOT/'data/KNOWLEDGE_K2.json').read_text())
    assert knowledge_hashes == [hashlib.sha256(knowledge[t].encode()).hexdigest() for t in ids]
    assert np.allclose(np.linalg.norm(log_vectors, axis=1), 1, atol=2e-6)
    assert np.allclose(np.linalg.norm(knowledge_vectors, axis=1), 1, atol=2e-6)
    log_map = dict(zip(sample_ids, log_vectors))
    source_hashes = {'feature_sha256': feature_sha, 'protocol_sha256': sha(protocol_path), 'trainer_sha256': sha(ROOT/'contrastive/train_heads.py'), 'math_source_sha256': sha(ROOT/'contrastive/numpy_models.py')}
    receipt_paths = sorted((ROOT/'results/runs_heads').glob('*_receipt.json'))
    assert len(receipt_paths) == 336
    assert len(list((ROOT/'checkpoints/heads').glob('*.npz'))) == 336
    saved_configs = {(json.loads(p.read_text())['method'], json.loads(p.read_text())['fold_id'], json.loads(p.read_text())['seed'], json.loads(p.read_text())['augmentation']): p for p in receipt_paths}
    assert len(saved_configs) == 336
    audits = []
    negative_rows_checked = 0
    for fold in splits:
        train = load(ROOT/fold['paths']['train'])
        held = load(ROOT/fold['paths']['heldout_inputs'])
        valid = load(ROOT/fold['paths']['validation_inputs'])
        assert all('gold_technique_ids' not in r for r in held+valid)
        groups = defaultdict(list)
        for row in train:
            assert row['scenario_id'] not in (fold['heldout_scenario'], fold['validation_scenario'])
            groups[row['logical_step_id']].append(row)
        steps = sorted(groups)
        canonical = [sorted(groups[k], key=lambda r: r['sampling_replica_id'])[0] for k in steps]
        positives = [set(r['gold_technique_ids']) for r in canonical]
        seen = sorted(set.union(*positives))
        seen_columns = np.asarray([ids.index(t) for t in seen])
        y = np.asarray([[t in p for t in ids] for p in positives], dtype=bool)
        co = y.astype(float).T @ y
        count = y.sum(0)
        train_ids = sorted(r['sample_id'] for r in train)
        train_ids_sha = hashlib.sha256(json.dumps(train_ids).encode()).hexdigest()
        for row in train+held+valid:
            assert input_hashes[row['sample_id']] == hashlib.sha256(row['input_log_text'].encode()).hexdigest()
        matrix = {partition: np.stack([log_map[r['sample_id']] for r in rows]).astype(np.float64) for partition, rows in [('HELDOUT', held), ('INNER_VALIDATION', valid), ('TRAIN_DIAGNOSTIC_R0', canonical)]}
        for seed in (17, 42, 73):
            for augmentation in ('ONE_VIEW_PER_STEP', 'MULTI_VIEW_AUGMENTATION'):
                pools = {}
                for method in METHODS:
                    receipt_path = saved_configs[method, fold['fold_id'], seed, augmentation]
                    receipt = json.loads(receipt_path.read_text())
                    tag = f"{method}_{fold['fold_id']}_seed{seed}_{augmentation}"
                    cp = ROOT/'checkpoints/heads'/f'{tag}.npz'
                    assert sha(cp) == receipt['checkpoint_sha256'] and cp.stat().st_size == receipt['checkpoint_bytes']
                    assert receipt['epochs'] == receipt['updates'] == 120 and receipt['train_parameters_updated']
                    assert receipt['actual_training_steps'] == len(canonical)
                    assert receipt['optimization_step_views'] == 120*len(canonical)
                    assert receipt['train_sample_ids'] == train_ids and receipt['seen_techniques'] == seen
                    assert receipt['source_training_sha256'] == sha(ROOT/fold['paths']['train'])
                    assert receipt['source_training_file'] == fold['paths']['train']
                    assert receipt['feature_source_sha256'] == feature_sha and receipt['source_sha256'] == source_hashes['trainer_sha256']
                    assert not receipt['GTE_backbone_trainable'] and not receipt['heldout_reference_read'] and not receipt['validation_reference_read']
                    assert receipt['no_hyperparameter_selection'] and receipt['checkpoint_reload_score_max_abs_delta'] == 0
                    for field in ('seconds', 'cpu_method_seconds', 'peak_rss_bytes', 'inference_seconds_held_valid_train', 'mining_seconds'):
                        assert np.isfinite(receipt[field]) and receipt[field] >= 0
                    assert receipt['peak_rss_scope'] == 'cumulative process high-water mark; not per-method incremental peak'
                    rng = np.random.default_rng(seed)
                    with np.load(cp, allow_pickle=False) as saved:
                        assert saved['ids'].tolist() == ids
                        assert saved['train_ids_sha256'].item() == train_ids_sha
                        assert saved['train_file_sha256'].item() == sha(ROOT/fold['paths']['train'])
                        for key, value in source_hashes.items():
                            assert saved[key].item() == value, (tag, key)
                        if method == 'B3':
                            assert np.array_equal(saved['seen'], seen_columns)
                            params = [saved['w'].copy(), saved['b'].copy()]
                            initial = [rng.normal(0, .001, (768, len(seen))), np.zeros(len(seen))]
                            assert params[0].shape == (768, len(seen)) and params[1].shape == (len(seen),)
                        else:
                            params = [saved['wl'].copy(), saved['wt'].copy()]
                            first = rng.normal(0, 1/np.sqrt(768), (768, 32))
                            initial = [first, first.copy()]
                            assert all(p.shape == (768, 32) for p in params)
                    assert all(np.isfinite(p).all() for p in params)
                    assert receipt['initial_parameters_sha256'] == arrsha(initial)
                    assert receipt['final_parameters_sha256'] == arrsha(params) != arrsha(initial)
                    change = float(np.sqrt(sum(np.square(p-q).sum() for p, q in zip(params, initial))))
                    assert change > 0 and np.isclose(change, receipt['parameter_L2_change'], rtol=0, atol=1e-12)
                    assert receipt['trainable_parameters'] == sum(p.size for p in params)
                    assert method == 'B3' or receipt['trainable_parameters'] == 49152
                    logs = json.loads((ROOT/'results/runs_heads'/f'{tag}_training.json').read_text())
                    assert [r['epoch'] for r in logs] == [1]+list(range(10, 121, 10))
                    assert all(np.isfinite(r['loss']) and np.isfinite(r['gradient_norm']) and r['updates'] == r['epoch'] for r in logs)
                    predictions = load(ROOT/'results/runs_heads'/f'{tag}_predictions.jsonl')
                    max_score_delta = 0.
                    for partition, rows in [('HELDOUT', held), ('INNER_VALIDATION', valid), ('TRAIN_DIAGNOSTIC_R0', canonical)]:
                        if method == 'B3':
                            scores = np.full((len(rows), 216), -1e6)
                            scores[:, seen_columns] = matrix[partition] @ params[0] + params[1]
                        else:
                            scores = projected(matrix[partition], knowledge_vectors, *params)
                        saved_rows = {r['sample_id']: r for r in predictions if r['evaluation_partition'] == partition}
                        assert set(saved_rows) == {r['sample_id'] for r in rows}
                        for row, values in zip(rows, scores):
                            record = saved_rows[row['sample_id']]
                            order = sorted(range(216), key=lambda j: (-values[j], ids[j]))
                            ranked = [ids[j] for j in order]
                            assert ranked == record['ranking_all216'] and ranked[:10] == record['predictions']
                            assert len(set(ranked)) == 216
                            assert record['method'] == method and record['seed'] == seed and record['augmentation'] == augmentation
                            assert record['fold_id'] == fold['fold_id'] and record['checkpoint_path'] == str(cp.relative_to(ROOT))
                            delta = float(np.max(np.abs(values[order[:10]]-record['scores_top10'])))
                            max_score_delta = max(max_score_delta, delta)
                            assert delta < 1e-10
                    assert len(predictions) == len(held)+len(valid)+len(canonical)
                    if method in ('B6', 'B7', 'B8', 'B9', 'B9_CONST'):
                        negatives = load(ROOT/'results/runs_heads'/f'{tag}_negatives.jsonl')
                        assert len(negatives) == 32*len(canonical)
                        per_step = defaultdict(list)
                        for row in negatives:
                            per_step[row['logical_step_id']].append(row)
                        assert set(per_step) == set(steps)
                        pools[method] = {}
                        for i, step in enumerate(steps):
                            selected = per_step[step]
                            chosen = [r['candidate_id'] for r in selected]
                            assert len(chosen) == len(set(chosen)) == 32 and not (set(chosen) & positives[i])
                            pools[method][step] = chosen
                            for row in selected:
                                j = ids.index(row['candidate_id'])
                                risk = float(max(co[p, j]/max(1, count[p]) for p in np.where(y[i])[0]))
                                weight = 1-.75*risk if method == 'B9' else .5 if method == 'B9_CONST' else 1.
                                assert set(row['positive_ids']) == positives[i]
                                assert row['risk_proxy_train_only'] == risk and row['weight'] == weight
                                assert not row['evidence_certified_negative'] and not row['known_positive_overlap']
                        negative_rows_checked += len(negatives)
                    audits.append({'method': method, 'fold_id': fold['fold_id'], 'seed': seed, 'augmentation': augmentation, 'parameter_L2_change_recomputed': change, 'score_max_abs_delta': max_score_delta, 'all_partitions_rankings_recomputed': True, 'lineage_pass': True, 'checkpoint_sha256': sha(cp), 'receipt_sha256': sha(receipt_path), 'heldout_rows': len(held)})
                assert pools['B8'] == pools['B9'] == pools['B9_CONST']
    b2_receipts = sorted((ROOT/'results/runs_B2').glob('*_receipt.json'))
    assert len(b2_receipts) == 42 and len(list((ROOT/'checkpoints/B2').glob('*.npz'))) == 42
    for path in b2_receipts:
        receipt = json.loads(path.read_text())
        assert sha(ROOT/receipt['checkpoint_path']) == receipt['checkpoint_sha256']
        assert receipt['W_changed'] and receipt['reload_max_abs_diff'] == 0 and receipt['optimizer_updates'] == 120
    frozen_rows = load(ROOT/'results/runs_frozen/B1_predictions.jsonl')
    historic_rows = {r['sample_id']: r for r in load(ROOT/'inherited/CPU_ONLY_B1_PREDICTIONS.jsonl')}
    assert len(frozen_rows) == len(historic_rows) == 975
    frozen_scores = log_vectors @ knowledge_vectors.astype(np.float32).T
    frozen_scores_by_id = dict(zip(sample_ids, frozen_scores))
    historic_top10_differences = 0
    baseline_max_delta = 0.
    for record in frozen_rows:
        assert record['feature_sha256'] == feature_sha
        values = frozen_scores_by_id[record['sample_id']]
        order = sorted(range(216), key=lambda j: (-values[j], ids[j]))
        ranking = [ids[j] for j in order]
        assert ranking == record['ranking_all216'] and ranking[:10] == record['predictions']
        baseline_max_delta = max(baseline_max_delta, float(np.max(np.abs(values[order[:10]]-record['scores_top10']))))
        historic_top10_differences += record['predictions'] != historic_rows[record['sample_id']]['predictions']
    assert baseline_max_delta < 1e-7
    report = {'status': 'PASS', 'new_head_configurations_audited': len(audits), 'B2_original_configurations_preserved': len(b2_receipts), 'total_trained_configurations': len(audits)+len(b2_receipts), 'new_heads_updates': len(audits)*120, 'total_updates_including_B2': (len(audits)+len(b2_receipts))*120, 'authentic_feature_sha256': feature_sha, 'source_hashes': source_hashes, 'feature_dimensions': {'log': [975, 768], 'knowledge': [216, 768]}, 'all_initial_and_final_parameter_hashes_recomputed': True, 'all_parameter_L2_changes_recomputed': True, 'all_heldout_validation_and_train_rankings_independently_recomputed': True, 'maximum_score_abs_delta': max(r['score_max_abs_delta'] for r in audits), 'negative_rows_checked': negative_rows_checked, 'B8_B9_CONST_identical_candidate_pools': True, 'zero_certified_negative_assertions': True, 'raw_model_weight_sha256_from_extraction_receipt': extraction['weight_sha256'], 'raw_model_integrity_scope': 'Fixed weight hash checked before forward and recorded again after extraction by authorized extractor; no fresh remote read by this local auditor. CPU trainer loads vectors and heads only.', 'resource_scope': 'CPU method process_time and wall seconds are method-specific; peak RSS is cumulative process high-water mark, not additive or incremental per-method. Mining is additional pipeline cost.', 'no_training_performed_by_auditor': True, 'no_server_or_LLM_calls': True, 'configurations': audits}
    report['matched_frozen_B1_independently_recomputed_queries'] = 975
    report['matched_frozen_B1_max_abs_score_delta'] = baseline_max_delta
    report['historical_vs_current_B1_top10_order_different_queries'] = historic_top10_differences
    report['historical_B1_variation_qualification'] = 'Observed difference is confirmed. FP16 forward batch packing is a plausible explanation, not independently isolated causal proof; current B1 and all heads use the same authentic feature cache.'
    (ROOT/'results/TRAINED_HEADS_INDEPENDENT_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n')
    (ROOT/'reports/TRAINED_HEADS_INDEPENDENT_AUDIT.md').write_text(f'''# 训练头独立审计\n\n结论：PASS。独立核查 {len(audits)} 个新增训练头及保留的 42 个 B2 工件，总计 378 配置。没有重新训练或调参。\n\n逐配置核查特征、训练文件、训练ID、协议、训练器、数学实现六类血缘；从注册随机种子重建初始参数，独立复算初末参数哈希、参数改变量、有限性、120 次更新日志及 Checkpoint 哈希。使用独立评分实现重载每个 Checkpoint，从真实 768 维 GTE 向量重算外层保留、内层验证和训练 r0 的全部 216 候选排序与 Top10 分数，最大分数偏差 {report['maximum_score_abs_delta']:.3g}。\n\n审计 {negative_rows_checked} 个未标注负候选，确认正例掩码、仅训练步骤共现风险及权重，B8/B9/CONST 使用相同候选池；这些候选均未被声明为证据认证的真实负例。\n\nCPU 时间为方法级 process_time；峰值 RSS 是复用进程的累计高水位，不能逐方法相加或当作各方法新增内存。B8/B9 的挖掘有额外流水线成本，匹配的是优化更新数而非整个流程总成本。\n\n固定原始权重 SHA256 与授权特征提取前后检查一致。本审计未再次连接服务器读取权重，因此原始模型完整性的证据来自真实特征提取回执及其源码；本地 CPU 训练器仅加载冻结向量和小型头，不加载或更新 GTE 主干。\n\n逐配置细节见 results/TRAINED_HEADS_INDEPENDENT_AUDIT.json。本审计不替代分组评价或独立外部泛化资格判断。\n''')
    with (ROOT/'reports/TRAINED_HEADS_INDEPENDENT_AUDIT.md').open('a') as handle:
        handle.write(f'\n另独立复算同批真实向量上的 B1：975 条完整 216 排名全部一致，最大 Top10 分数偏差 {baseline_max_delta:.3g}。保留的旧 B1 与新 B1 有 {historic_top10_differences} 条 Top10 顺序不同，变化事实已确认；FP16 前向批次组织是合理解释，但本审计没有隔离验证其因果作用。正式匹配对照使用同一真实向量缓存上的新 B1。\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'configurations'}, indent=2))


if __name__ == '__main__':
    main()
