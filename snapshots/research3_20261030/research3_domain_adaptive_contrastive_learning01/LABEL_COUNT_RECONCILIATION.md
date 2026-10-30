# 多标签 285 / 295 差异复核

确认结论：冻结父技术集合协议应使用 **285/975 查询、57/195 逻辑步骤为多标签**，分别占29.2308%。同一源标签文件在保留子技术原始ID粒度时为 **295/975 查询、59/195 逻辑步骤**。这不是两套样本或标签版本的差异。

复核方法是逐条执行 `sorted(set(t.split('.')[0] for t in ground_truth))`，然后计算集合大小是否大于1；不取第一个标签，不按原始数组长度代替集合大小。195个逻辑步骤的5条采样引用相同Gold。

差额恰好来自场景6逻辑步骤 **6-33、6-34**。每步的原始标签都是 `T1056.004` 与 `T1056.001`，原始ID集合大小2；父技术集合规范化后都是 `{T1056}`，集合大小1。两步各5个采样产生10查询差额。

已定位历史文字：

- `research3_attack_technique_benchmark01/OFFICIAL_DATA_ASSET_AUDIT.md:7`、`R3_ATTACK_TECHNIQUE_BENCHMARK_RESULTS.md:17`与`BASELINE_ERROR_ANALYSIS.md:44`报告285/975及57/195，符合冻结父技术评价协议。
- `research3_attack_mechanism_discrimination01/R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md:22`报告295/975并将其用于父技术任务描述；该数字符合原始子技术ID粒度，却未说明粒度，属于该报告统计口径表述错误。本轮明确更正，不改写旧资产。
- 第一轮`datasets/reference_view.jsonl`和强基线`datasets/p0_reference.jsonl`按sample_id比较，975条ground_truth完全一致。因此没有证据支持“标签版本更换”解释。

可复核证据：`data/manifests/LABEL_NORMALIZATION_DIFFERENCE.json`保存全部10条差异记录，`MULTILABEL_DISTRIBUTION.csv`给出全部、场景、模拟执行的两种口径。`data/prepare_grouped_data.py`可重建统计；`TRAINING_DATA_MANIFEST.json`冻结源文件SHA256。

本轮监督信号始终为规范化父技术集合。作者步骤级技术标签不等同于每条抽样日志都观测到了该技术机制；未标注候选仍是UNLABELED_CANDIDATE，而不是经证据认证的反例。
