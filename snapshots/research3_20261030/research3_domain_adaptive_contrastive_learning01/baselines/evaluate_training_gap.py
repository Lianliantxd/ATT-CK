"""Read-only checkpoint scoring on legal training r0 views; no optimization."""
from __future__ import annotations
import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
from train_tfidf_linear import transform, ranking

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT.parent / 'research3_attack_technique_benchmark01'


def main() -> None:
    spec = importlib.util.spec_from_file_location('frozen_technique_evaluator_gap', BENCH/'evaluate_techniques.py')
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    splits = {f['fold_id']: f for f in json.loads((ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json').read_text())['folds']}
    with (ROOT/'GROUPED_VALIDATION_RESULTS.csv').open() as handle:
        reference_metrics = {(r['fold_id'], int(r['seed']), r['augmentation'], r['evaluation_partition'].upper()): r for r in csv.DictReader(handle) if r['method'] == 'B2'}
    results = []
    for path in sorted((ROOT/'results/runs_B2').glob('*_receipt.json')):
        receipt = json.loads(path.read_text())
        fold = splits[receipt['fold_id']]
        train_path = ROOT/fold['one_view_train_path']
        train = [json.loads(line) for line in train_path.read_text().splitlines()]
        assert len(train) == receipt['train_step_count']
        assert all(r['sampling_replica_id'] == 0 for r in train)
        checkpoint = ROOT/receipt['checkpoint_path']
        assert hashlib.sha256(checkpoint.read_bytes()).hexdigest() == receipt['checkpoint_sha256']
        with np.load(checkpoint, allow_pickle=False) as saved:
            x = transform(train, saved['vocab'].tolist(), saved['idf'])
            candidates = saved['candidate_ids'].tolist()
            seen = saved['labels'].tolist()
            logits = x @ saved['W'] + saved['b']
        scores = np.full((len(train), len(candidates)), -1e6, dtype=np.float32)
        scores[:, [candidates.index(t) for t in seen]] = logits
        records = []
        for row, values in zip(train, scores):
            order = ranking(values, candidates)
            records.append({'ground_truth': row['gold_technique_ids'], 'predictions': [candidates[i] for i in order[:10]]})
        metric = evaluator.summarize(records, candidates)
        result = {'method': 'B2', 'fold_id': receipt['fold_id'], 'seed': receipt['seed'], 'augmentation': receipt['augmentation'], 'train_r0_steps': len(train), 'train_seen_classes': len(seen), 'train_r0_mrr': metric['mrr'], 'train_r0_top10_accuracy': metric['top10_accuracy'], 'checkpoint_path': receipt['checkpoint_path'], 'checkpoint_sha256': receipt['checkpoint_sha256'], 'diagnostic_qualification': 'POSTHOC_NO_RETRAINING_OR_MODEL_SELECTION'}
        for partition in ('VALIDATION', 'HELDOUT'):
            ref = reference_metrics[receipt['fold_id'], receipt['seed'], receipt['augmentation'], partition]
            label = partition.lower()
            result[label+'_queries'] = int(ref['n_records'])
            result[label+'_mrr'] = float(ref['mrr'])
            result[label+'_top10_accuracy'] = float(ref['top10_accuracy'])
            result['train_minus_'+label+'_mrr'] = metric['mrr'] - float(ref['mrr'])
            result['train_minus_'+label+'_top10'] = metric['top10_accuracy'] - float(ref['top10_accuracy'])
        results.append(result)
    assert len(results) == 42
    with (ROOT/'results/B2_TRAIN_GENERALIZATION_GAP.csv').open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0])); writer.writeheader(); writer.writerows(results)
    lines = ['# B2 训练与分组保留表现差距诊断', '', '已重新加载全部 42 个已训练 Checkpoint，仅在各自合法训练折的 r0 输入上前向评分；没有参数更新、重新训练、调参或模型选择。训练标签仅用于事后评价，验证和外层保留指标直接读取父任务已生成的 GROUPED_VALIDATION_RESULTS.csv。所有排序仍包含 216 个候选，未见技术得分固定为 −1e6。', '', '| 采样模式 | 训练 r0 MRR | 验证 MRR | 外层保留 MRR | 训练 r0 Top10 | 验证 Top10 | 外层保留 Top10 |', '|---|---:|---:|---:|---:|---:|---:|']
    descriptions = []
    for mode in ('ONE_VIEW_PER_STEP', 'MULTI_VIEW_AUGMENTATION'):
        group = [r for r in results if r['augmentation'] == mode]
        avg = lambda key: float(np.mean([r[key] for r in group]))
        values = [avg(key) for key in ['train_r0_mrr', 'validation_mrr', 'heldout_mrr', 'train_r0_top10_accuracy', 'validation_top10_accuracy', 'heldout_top10_accuracy']]
        lines.append('| '+mode+' | '+' | '.join(f'{value:.4f}' for value in values)+' |')
        n_mrr = sum(r['train_minus_heldout_mrr'] > 0 for r in group)
        n_top10 = sum(r['train_minus_heldout_top10'] > 0 for r in group)
        descriptions.extend(['', f'{mode}：21 个折×种子配置中，训练 r0 MRR 高于外层保留 {n_mrr}/21，Top10 高于外层保留 {n_top10}/21。训练减外层保留的平均 MRR 差为 {avg("train_minus_heldout_mrr"):.4f}，平均 Top10 差为 {avg("train_minus_heldout_top10"):.4f}。', ''])
    lines.extend(descriptions)
    lines.extend(['这些是各折与种子的等权描述均值，种子不构成独立攻击样本。训练每逻辑步骤只评价 r0，验证和外层保留使用相关的多采样查询，因此此表用于诊断，并非完全同采样单位的确认性泛化检验。', '', '训练表现高于验证/外层保留，说明存在训练—保留表现差距，与过拟合或分布偏移风险一致；不能单凭该差距证明模型记忆了场景或攻击脚本。差距还可能受到技术类别覆盖、训练未见类别无法学习、标签非穷尽、视图差异与场景日志分布变化影响。因未增加专门控制实验，本报告不区分这些机制，也不据此追加损失函数或超参数搜索。', '', 'Checkpoint SHA256 均与原训练回执一致；所有训练评价通过冻结 evaluate_techniques.py 的 summarize 计算 MRR@10 和 Top10。逐折、种子与采样模式的实际数值见 results/B2_TRAIN_GENERALIZATION_GAP.csv。'])
    (ROOT/'reports/B2_OVERFIT_DIAGNOSTIC.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'status': 'PASS', 'checkpoints_reloaded': len(results), 'new_parameter_updates': 0, 'mean_train_mrr': float(np.mean([r['train_r0_mrr'] for r in results])), 'mean_heldout_mrr': float(np.mean([r['heldout_mrr'] for r in results])), 'positive_mrr_gap_configs': sum(r['train_minus_heldout_mrr'] > 0 for r in results)}, indent=2))


if __name__ == '__main__':
    main()
