# 已暴露开发集的严格分析

主问题：相同新增证据上限下，动态启发式能否超过静态BM25？两预算均以Top10为描述主指标，Top1/MRR为并列辅助。不是LLM Agent测试。

|Condition|Top-1|Top-10|MRR|
|---|---:|---:|---:|
|NO_EXTRA|0.070130|0.285714|0.119622|
|STATIC_BM25_S|0.101299|0.314286|0.147408|
|STATIC_BM25_M|0.088312|0.322078|0.143334|
|FIXED_SOURCE_S|0.098701|0.311688|0.147462|
|FIXED_SOURCE_M|0.098701|0.309091|0.146391|
|ADAPTIVE_HEURISTIC_S|0.088312|0.296104|0.138544|
|ADAPTIVE_HEURISTIC_M|0.096104|0.319481|0.145913|

385个执行—步骤重复覆盖195个逻辑步骤、34执行、7场景；不把385视作独立实验。一次确定性运行，无多seed方差。按场景汇总并保留全部关联样本；事后20,000次场景簇bootstrap仅反映7场景组合敏感性。

## Claim Candidates

- Claim: 当前动态启发式没有稳定超过静态检索。
  - Source evidence: statistics.json、scene_metrics.csv及完整2695条预测。
  - Allowed wording: S下点估计较低，M下Top10略低但Top1/MRR略高，没有一致优势。
  - Forbidden stronger wording: 所有Agent无效、静态方法普遍优越、独立泛化已证明。
  - Uncertainty: 仅7关联开发场景，一次冻结策略，实际消耗预算不完全相同。
  - Next check: 合法语义召回及有效固定LLM受控配对。
  - Decision: keep

- Claim: P0 Top20词汇候选的任何Gold覆盖只有38.9744%。
  - Source evidence: CANDIDATE_RECALL_UPPER_BOUNDS.csv。
  - Allowed wording: 限定该候选的完美重排Top10仍不可能超过38.9744%。
  - Forbidden stronger wording: 所有语义检索均受此上限约束、证明LLM推理无效。
  - Uncertainty: 仅当前冻结字符检索及合法P0。
  - Next check: 更好的候选召回。
  - Decision: keep
