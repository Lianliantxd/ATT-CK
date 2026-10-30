"""Independent post-run audit: reads train labels, never heldout references.

No optimizer, feature extraction, tokenizer, network access, or model training.
Run only after the parent confirms the full 336-head matrix is complete.
"""
import os
for _name in ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS']:
    os.environ[_name] = '2'
import collections
import hashlib
import itertools
import json
import math
from pathlib import Path
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
METHODS = ['B6', 'B7', 'B8', 'B9', 'B9_CONST']
ALL_HEADS = ['B3', 'B4', 'B5', *METHODS]
KNOWN_WEIGHT = '3e85899d5728cb7de79781c0c3acfb91ccef9f875f1f7e0b3c9f3dd4b6a724ba'
KNOWN_REVISION = 'e7f32e3c00f91d699e8c43b53106206bcc72bb22'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_json(path):
    return json.loads(Path(path).read_text())

def load_lines(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]

def require(value, message):
    if not bool(value):
        raise AssertionError(message)

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def independently_project(x, t, wl, wt):
    """Reimplement frozen score formula; do not import the training module."""
    zl = x @ wl
    zt = t @ wt
    zl = zl / np.maximum(np.linalg.norm(zl, axis=1, keepdims=True), 1e-8)
    zt = zt / np.maximum(np.linalg.norm(zt, axis=1, keepdims=True), 1e-8)
    return zl @ zt.T / .1

def new_stats():
    return {'rows': 0, 'step_pools': 0, 'positive_overlap': 0,
            'evidence_certified_negative': 0, 'train_cooccurrence_risk_positive_rows': 0,
            'risk_sum': 0., 'risk_min': 1., 'risk_max': 0.,
            'weight_sum': 0., 'weight_min': 1., 'weight_max': 0.}

def report_md(result):
    out = ['# 实际负例挖掘与公平性独立审计', '',
           '审计日期：2026-10-28。结论：' + result['status'] + '。', '',
           '只读训练文件中的标签、固定向量、B5参数、挖掘行及运行回执；没有读取heldout/validation reference，没有执行参数更新、服务器操作或下载。', '',
           f"核验 {result['head_configurations']} 个头配置的回执存在，逐项重算 {result['negative_files']} 份负例文件、{result['total_negative_rows']:,} 行、{result['total_step_pools']:,} 个32候选池。", '',
           '每个候选必须是冻结216父技术之一；每池32个不同ID；候选与该训练步骤全部已知Gold正例无交集。对B6重建同种子随机数状态，对B7重算公开知识最大正例相似度，对B8重算同fold/seed/mode B5在训练r0上的分数和tie-break。B8/B9/CONST池的成员及顺序逐步完全一致。', '',
           '| 方法 | 候选行 | 步骤池 | 共现风险>0比例 | 平均权重 | 认证负例 |',
           '|---|---:|---:|---:|---:|---:|']
    for method in METHODS:
        s = result['by_method'][method]
        out.append(f"| {method} | {s['rows']:,} | {s['step_pools']:,} | {s['train_cooccurrence_risk_positive_rate']:.4%} | {s['mean_weight']:.6f} | {s['evidence_certified_negative']} |")
    out += ['', '风险由唯一训练逻辑步骤的共现重新计算：risk=max_p count_train(p,j)/count_train(p)。B9权重为1−0.75×risk，CONST恒为0.5，其他方法恒为1。risk>0仅表示训练标签曾共现，risk=0不表示候选为真负例；不能把该比例称作假负例率或人工验证准确率。', '',
            '| 采样来源对 | 逐池平均交集数/32 | 平均Jaccard |', '|---|---:|---:|']
    for pair, s in result['source_pool_overlap'].items():
        out.append(f"| {pair} | {s['mean_intersection_count']:.6f} | {s['mean_jaccard']:.6f} |")
    out += ['', '随机、公开知识语义及模型混淆重合以同一fold/seed/mode/step配对计算，不跨训练步骤混合。ONE与MULTI是训练增强条件；它们不是额外独立攻击执行。', '',
            '训练来源资格：每个挖掘行都属于该fold的合法训练逻辑步骤；元数据中的全部positive_ids等于训练步骤标签集合；回执绑定训练文件、特征与源代码；B5 checkpoint绑定特征、训练文件、协议、trainer及math源码哈希。未使用heldout标签来构造或验证负例公式。', '',
            '正例保护的证据范围：实际保存的候选与完整训练Gold集合逐行无交集，且冻结源码从y构造候选mask、正例权重保持1并在损失中断言。训练没有保存每一轮实际mask张量，故本审计属于“实际候选重构＋冻结执行源码/回执”资格，不冒称逐梯度运行轨迹完整观测。', '',
            '所有行 EVIDENCE_CERTIFIED_NEGATIVE=0；该结果不新增证据认证，也不证明未知候选在语义上必为错误技术。B8/B9复用B5的额外上游训练成本不能被120次更新数抹去；这里核对同池与训练来源，最终成本由父报告汇总。', '',
            f"最大权重重算差={result['max_weight_abs_error']:.3g}；最大风险重算差={result['max_risk_abs_error']:.3g}。", '',
            '全部配置、文件哈希、逐配置池哈希及详细计数见 results/NEGATIVE_MINING_AUDIT.json。没有修改冻结训练代码、模型文件或根结果CSV。', '']
    return '\n'.join(out)

def audit():
    started = time.monotonic()
    protocol_path = ROOT / 'manifests/TRAINING_PROTOCOL.json'
    protocol = load_json(protocol_path)
    split_path = ROOT / 'GROUPED_TRAIN_VALIDATION_SPLITS.json'
    splits = load_json(split_path)
    require(sha(split_path) == protocol['split_file_sha256'], 'Split manifest differs from registration')
    complete = load_json(ROOT / 'results/HEADS_MATRIX_COMPLETE.json')
    require(complete['status'] == 'ALL_REGISTERED_HEADS_TRAINED' and complete['configurations'] == 336,
            'Audit is gated on completion of all 336 registered heads')
    require(complete['total_optimizer_updates'] == 336 * 120, 'Unexpected update count')
    feature_path = ROOT / 'embeddings/FROZEN_GTE_FEATURES.npz'
    feature_sha = sha(feature_path)
    extraction = load_json(ROOT / 'embeddings/FEATURE_EXTRACTION_RECEIPT.json')
    require(extraction['feature_sha256'] == feature_sha and extraction['weight_sha256'] == KNOWN_WEIGHT
            and extraction['model_revision'] == KNOWN_REVISION and not extraction['Gold_loaded'],
            'Frozen-feature receipt invalid')
    feature = np.load(feature_path, allow_pickle=False)
    ids = feature['technique_ids'].tolist()
    knowledge = load_json(ROOT / 'data/KNOWLEDGE_K2.json')
    require(ids == sorted(knowledge) and len(ids) == len(set(ids)) == 216, 'Candidate space mismatch')
    require(feature['knowledge_hashes'].tolist() == [hashlib.sha256(knowledge[t].encode()).hexdigest() for t in ids],
            'Knowledge hashes do not match K2')
    sample_ids = feature['sample_ids'].tolist()
    require(len(sample_ids) == len(set(sample_ids)) == 975, 'Feature sample IDs invalid')
    require(feature['log_vectors'].shape == (975, 768) and np.isfinite(feature['log_vectors']).all(), 'Invalid log features')
    log_vectors = dict(zip(sample_ids, feature['log_vectors']))
    input_hashes = dict(zip(sample_ids, feature['input_hashes'].tolist()))
    tech = feature['knowledge_vectors'].astype(np.float64)
    require(tech.shape == (216, 768) and np.isfinite(tech).all(), 'Invalid knowledge features')
    require(np.allclose(np.linalg.norm(tech, axis=1), 1., atol=1e-5, rtol=0), 'Public knowledge vectors are not L2-normalized cosine inputs')
    ididx = {t: j for j, t in enumerate(ids)}
    semantic_similarity = tech @ tech.T
    trainer_sha = sha(ROOT / 'contrastive/train_heads.py')
    math_sha = sha(ROOT / 'contrastive/numpy_models.py')
    protocol_sha = sha(protocol_path)
    root = ROOT / 'results/runs_heads'
    rootcp = ROOT / 'checkpoints/heads'
    by_method = {m: new_stats() for m in METHODS}
    overlap = {f'{a}_vs_{b}': {'pools': 0, 'intersection_sum': 0, 'jaccard_sum': 0.}
               for a, b in itertools.combinations(['B6', 'B7', 'B8'], 2)}
    configurations = []
    head_count = negative_files = total_rows = total_pools = 0
    max_risk_error = max_weight_error = 0.
    receipts = []
    for fold in splits['folds']:
        train_path = ROOT / fold['paths']['train']
        train = load_lines(train_path)
        train_sha = sha(train_path)
        require(all(r['scenario_id'] not in [fold['heldout_scenario'], fold['validation_scenario']] for r in train),
                'Evaluation scenario appeared in training source')
        groups_dict = collections.defaultdict(list)
        for row in train:
            require(input_hashes[row['sample_id']] == hashlib.sha256(row['input_log_text'].encode()).hexdigest(), 'Train input hash mismatch')
            groups_dict[row['logical_step_id']].append(row)
        keys = sorted(groups_dict)
        groups = [sorted(groups_dict[k], key=lambda r: r['sampling_replica_id']) for k in keys]
        require(all(len(g) == 5 and len({r['sample_id'] for r in g}) == 5 for g in groups), 'Each train step must have five unique views')
        y = np.zeros((len(groups), 216), dtype=bool)
        for i, group in enumerate(groups):
            gold = set(group[0]['gold_technique_ids'])
            require(gold and all(set(r['gold_technique_ids']) == gold for r in group), 'Inconsistent/missing train step labels')
            require(gold <= set(ids), 'Non-candidate positive ID')
            for t in gold:
                y[i, ididx[t]] = True
        # Unique steps only: do not multiply counts by the five sampling views.
        counts = y.sum(0)
        co = y.astype(float).T @ y
        htrain = np.stack([log_vectors[g[0]['sample_id']] for g in groups]).astype(float)
        train_ids = sorted(r['sample_id'] for r in train)
        train_ids_sha = hashlib.sha256(json.dumps(train_ids).encode()).hexdigest()
        for seed in protocol['seeds']:
            for mode in protocol['augmentation']:
                name = f"{fold['fold_id']}_seed{seed}_{mode}"
                for head in ALL_HEADS:
                    receipt_path = root / f'{head}_{name}_receipt.json'
                    receipt = load_json(receipt_path)
                    require(receipt['method'] == head and receipt['fold_id'] == fold['fold_id']
                            and receipt['seed'] == seed and receipt['augmentation'] == mode, 'Receipt context mismatch')
                    require(receipt['train_sample_ids'] == train_ids and receipt['source_training_sha256'] == train_sha
                            and receipt['source_training_file'] == fold['paths']['train'], 'Receipt source is not current train fold')
                    require(receipt['train_parameters_updated'] and receipt['epochs'] == receipt['updates'] == 120
                            and not receipt['heldout_reference_read'] and not receipt['validation_reference_read'],
                            'Invalid completed training receipt')
                    require(receipt['feature_source_sha256'] == feature_sha and receipt['source_sha256'] == trainer_sha,
                            'Receipt source feature/trainer lineage mismatch')
                    head_count += 1
                b5path = rootcp / f'B5_{name}.npz'
                b5_receipt = load_json(root / f'B5_{name}_receipt.json')
                b5_sha = sha(b5path)
                require(b5_sha == b5_receipt['checkpoint_sha256'], 'B5 file differs from completed receipt')
                with np.load(b5path, allow_pickle=False) as b5:
                    expected = {'train_ids_sha256': train_ids_sha, 'feature_sha256': feature_sha,
                                'train_file_sha256': train_sha, 'protocol_sha256': protocol_sha,
                                'trainer_sha256': trainer_sha, 'math_source_sha256': math_sha}
                    for field, value in expected.items():
                        require(b5[field].item() == value, 'B5 lineage mismatch: ' + field)
                    require(b5['ids'].tolist() == ids, 'B5 candidate IDs mismatch')
                    confusion_scores = independently_project(htrain, tech, b5['wl'], b5['wt'])
                rng = np.random.default_rng(seed)
                # The frozen trainer consumes this draw before B6 sampling.
                rng.normal(0, 1 / np.sqrt(768), (768, 32))
                expected_pools = {'B6': [], 'B7': [], 'B8': []}
                for i in range(len(groups)):
                    eligible = np.where(~y[i])[0]
                    expected_pools['B6'].append([ids[j] for j in rng.choice(eligible, 32, replace=False).tolist()])
                    relevance = semantic_similarity[np.where(y[i])[0]].max(0)
                    expected_pools['B7'].append([ids[j] for j in sorted(eligible, key=lambda j: (-relevance[j], ids[j]))[:32]])
                    expected_pools['B8'].append([ids[j] for j in sorted(eligible, key=lambda j: (-confusion_scores[i, j], ids[j]))[:32]])
                actual_pools = {}
                file_receipts = []
                for method in METHODS:
                    path = root / f'{method}_{name}_negatives.jsonl'
                    rows = load_lines(path)
                    require(len(rows) == len(groups) * 32, f'Unexpected row count: {path.name}')
                    require([r['logical_step_id'] for r in rows] == [key for key in keys for _ in range(32)],
                            'Actual row ordering or train step coverage mismatch')
                    pools = []
                    source = str(b5path.relative_to(ROOT)) if method in ['B8', 'B9', 'B9_CONST'] else 'PUBLIC_KNOWLEDGE_COSINE' if method == 'B7' else 'RANDOM_SEED'
                    qualification = 'SEMANTIC_HARD_UNLABELED' if method == 'B7' else 'UNLABELED_MODEL_CONFUSION' if method in ['B8', 'B9', 'B9_CONST'] else 'UNLABELED_CANDIDATE'
                    stat = by_method[method]
                    for i, key in enumerate(keys):
                        pool_rows = rows[i * 32:(i + 1) * 32]
                        candidates = [r['candidate_id'] for r in pool_rows]
                        positive_ids = [ids[j] for j in np.where(y[i])[0]]
                        require(len(candidates) == len(set(candidates)) == 32 and set(candidates) <= set(ids), 'Invalid/duplicate negative candidate IDs')
                        require(not set(candidates) & set(positive_ids), 'Known positive entered negative pool')
                        expected_pool = expected_pools[method if method in ['B6', 'B7'] else 'B8'][i]
                        require(candidates == expected_pool, f'{method} does not match independent mining recomputation: {name}/{key}')
                        for row in pool_rows:
                            require(row['method'] == method and row['fold_id'] == fold['fold_id'] and row['seed'] == seed
                                    and row['augmentation'] == mode and row['logical_step_id'] == key, 'Negative row context mismatch')
                            require(row['positive_ids'] == positive_ids and not row['known_positive_overlap'], 'Full multi-positive set not protected')
                            require(row['source_model_checkpoint'] == source and row['qualification'] == qualification
                                    and row['cooccurrence_unit'] == 'UNIQUE_TRAIN_STEP_ONLY', 'Negative source qualification mismatch')
                            require(row['evidence_certified_negative'] is False, 'Unlabeled candidate relabeled as certified negative')
                            j = ididx[row['candidate_id']]
                            risk = float(max(co[p, j] / max(1, counts[p]) for p in np.where(y[i])[0]))
                            weight = 1 - .75 * risk if method == 'B9' else .5 if method == 'B9_CONST' else 1.
                            risk_error = abs(float(row['risk_proxy_train_only']) - risk)
                            weight_error = abs(float(row['weight']) - weight)
                            require(math.isfinite(risk_error) and risk_error <= 1e-12, 'Train-only cooccurrence risk formula mismatch')
                            require(math.isfinite(weight_error) and weight_error <= 1e-12, 'Reliability/CONST weight formula mismatch')
                            max_risk_error = max(max_risk_error, risk_error)
                            max_weight_error = max(max_weight_error, weight_error)
                            stat['rows'] += 1
                            stat['train_cooccurrence_risk_positive_rows'] += int(risk > 0)
                            stat['risk_sum'] += risk
                            stat['risk_min'] = min(stat['risk_min'], risk)
                            stat['risk_max'] = max(stat['risk_max'], risk)
                            stat['weight_sum'] += weight
                            stat['weight_min'] = min(stat['weight_min'], weight)
                            stat['weight_max'] = max(stat['weight_max'], weight)
                        stat['step_pools'] += 1
                        pools.append(candidates)
                    actual_pools[method] = pools
                    file_receipts.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path),
                                          'rows': len(rows), 'step_pools': len(groups), 'ordered_pool_sha256': digest(list(zip(keys, pools)))})
                    negative_files += 1
                    total_rows += len(rows)
                    total_pools += len(groups)
                require(actual_pools['B8'] == actual_pools['B9'] == actual_pools['B9_CONST'], 'B8/B9/CONST pools or ordering differ')
                for a, b in itertools.combinations(['B6', 'B7', 'B8'], 2):
                    stat = overlap[f'{a}_vs_{b}']
                    for pa, pb in zip(actual_pools[a], actual_pools[b]):
                        aa, bb = set(pa), set(pb)
                        stat['pools'] += 1
                        stat['intersection_sum'] += len(aa & bb)
                        stat['jaccard_sum'] += len(aa & bb) / len(aa | bb)
                configurations.append({'fold_id': fold['fold_id'], 'seed': seed, 'augmentation': mode,
                                       'train_unique_steps': len(groups), 'train_queries': len(train),
                                       'train_file_sha256': train_sha, 'train_ids_sha256': train_ids_sha,
                                       'B5_checkpoint_path': str(b5path.relative_to(ROOT)), 'B5_checkpoint_sha256': b5_sha,
                                       'B8_B9_CONST_identical_ordered_pools': True, 'files': file_receipts})
                print('AUDITED', name, flush=True)
    require(head_count == 336 and negative_files == 210 and len(configurations) == 42, 'Incomplete registered matrix')
    for stat in by_method.values():
        stat['train_cooccurrence_risk_positive_rate'] = stat['train_cooccurrence_risk_positive_rows'] / stat['rows']
        stat['mean_risk'] = stat['risk_sum'] / stat['rows']
        stat['mean_weight'] = stat['weight_sum'] / stat['rows']
    for stat in overlap.values():
        stat['mean_intersection_count'] = stat['intersection_sum'] / stat['pools']
        stat['mean_jaccard'] = stat['jaccard_sum'] / stat['pools']
    return {'status': 'PASS', 'date_asia_shanghai': '2026-10-28',
            'head_configurations': head_count, 'negative_files': negative_files,
            'total_negative_rows': total_rows, 'total_step_pools': total_pools,
            'by_method': by_method, 'source_pool_overlap': overlap, 'configurations': configurations,
            'max_risk_abs_error': max_risk_error, 'max_weight_abs_error': max_weight_error,
            'EVIDENCE_CERTIFIED_NEGATIVE': 0, 'heldout_labels_read': False, 'validation_labels_read': False,
            'new_optimizer_updates': 0, 'new_feature_extraction': False, 'new_downloads': 0,
            'positive_protection_evidence': 'ACTUAL_CANDIDATES_VS_FULL_TRAIN_GOLD_PLUS_FROZEN_EXECUTION_SOURCE; runtime mask tensors not separately saved',
            'feature_sha256': feature_sha, 'protocol_sha256': protocol_sha,
            'split_sha256': sha(split_path), 'trainer_sha256': trainer_sha, 'math_source_sha256': math_sha,
            'audit_source_sha256': sha(Path(__file__)), 'seconds': time.monotonic() - started}

def main():
    try:
        result = audit()
    except Exception as exc:
        result = {'status': 'FAIL', 'date_asia_shanghai': '2026-10-28',
                  'error_type': type(exc).__name__, 'error': str(exc),
                  'heldout_labels_read': False, 'validation_labels_read': False,
                  'new_optimizer_updates': 0, 'audit_source_sha256': sha(Path(__file__))}
        (ROOT / 'results/NEGATIVE_MINING_AUDIT.json').write_text(json.dumps(result, indent=2) + '\n')
        (ROOT / 'reports/NEGATIVE_MINING_EXECUTION_AUDIT.md').write_text('# 负例审计未通过\n\n' + str(exc) + '\n\n没有据此宣称候选池合格；未执行训练或读取heldout标签。\n')
        raise
    (ROOT / 'results/NEGATIVE_MINING_AUDIT.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'reports/NEGATIVE_MINING_EXECUTION_AUDIT.md').write_text(report_md(result))
    print(json.dumps({k: result[k] for k in ['status', 'head_configurations', 'negative_files', 'total_negative_rows', 'total_step_pools', 'seconds']}))

if __name__ == '__main__':
    main()
