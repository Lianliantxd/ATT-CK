# 有限证据预审分析

问题：384个已冻结漏召回查询的当前视图是否实际包含目标Gold相关的可观察动作？本轮只回答这个有限问题；竞争排序和独立语义充分性未完成。

完整结果在QUERY_EVIDENCE_REVIEWS.jsonl，所有计数由REVIEW_COUNTS.json及CSV重现。顶层互斥：直接24、部分102、背景74、无相关148、输入不足4、粒度疑问32，其他两类0。目标级非互斥：任一直接31、任一部分95、任一背景94、任一无相关197、任一粒度疑问34、输入不足4。

没有比较算法，无法给出最优模型或模型失败根因。最强事实是“当前冻结文本与既有目标之间的证据资格尚未得到独立裁定”。这削弱了仅从漏召回现象直接跳到“语义表示失败”的推断，也不能反向证明预处理或Gold一定错误。

## Claim Candidates

- Claim：31个查询至少对一个目标呈现直接相关动作/尝试。
  Source evidence：逐目标gold_reviews、当前查询Fact引用，9个逻辑步骤。
  Allowed wording：同上下文AI预审记录到相关动作，完整技术及恶意归属未认证。
  Forbidden stronger wording：31次已确认攻击、模型必须召回、Gold唯一正确。
  Uncertainty：145种文本中的重复视图、没有独立裁定、复合命题中的目的/结果可能仍未知。
  Next check：独立人工核验引用、动作与技术范围及竞争解释。
  Decision：weaken。

- Claim：34个查询至少有一个目标存在具体范围/粒度疑问。
  Source evidence：gold_reviews及逐案冻结正文；例如父技术条目正文只展开特定变体。
  Allowed wording：冻结参考不足以裁定完整父类，需核查映射合同。
  Forbidden stronger wording：34个错标、修正映射必然提高召回。
  Uncertainty：完整父类定义与独立标注依据未提供。
  Next check：人工核验对应冻结知识生成链和原标注粒度。
  Decision：keep。

- Claim：主要失败原因是语义表示、截断或标签错误。
  Source evidence：目前没有足以排除竞争解释的独立证据。
  Allowed wording：这些原因仍未确定。
  Forbidden stronger wording：已找到主因及各原因真实占比。
  Uncertainty：全部384个Top10比较未评价，独立盲审0。
  Next check：先完成证据资格与标签范围人工核验。
  Decision：discard作为已证实结论。
