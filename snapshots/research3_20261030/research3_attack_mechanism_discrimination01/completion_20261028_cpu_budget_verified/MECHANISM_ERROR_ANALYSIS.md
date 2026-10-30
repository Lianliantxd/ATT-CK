# 错误与消融

两种CPU协议分别报告，禁止混合：

- BYTE：继承已冻结49条件，日志≤2000 UTF8字节、知识≤1000字节；所有视图来自同一个公共原生片段前缀。
- FEATURE：本续作真实执行49条件（40主对照、8清洗消融、1同预算字面匹配），日志同时≤2048个字符3/4/5-gram出现次数及256个BM25词，知识同时≤1024个字符ngram及128个BM25词。所有视图使用再次缩减后的相同原始观察。具体长度、截断位置和事件数见FEATURE_INPUT_BUDGETS.csv。

这里的特征计数是CPU检索器的实际输入单位，**不是GTE Token数**。相同预算指相同上限，不代表每个视图恰好相同长度。原版49条件中LiteralMechanismMatching使用完整K2卡片概念，存在知识预算差异，须单独看待；新MATCHED_K2使用同一截断K2，未作标签定制。

共98条件、95,550预测行；其中47,775行是继承的真实CPU输出，47,775行为本续作新运行。每条件完整975查询、216候选，无失败删除。原神经结果只用于审计，不作为本轮Literal神经预测。共有144项固定差值分析，完整表保留负结果。所有实验为确定性单次运行，无训练种子重复。

公共前缀的二分选择已验证可行，但字段解析和规范化使预算函数未证明全局单调；不能声称取得全局最大前缀。该限制不会使已验证的预算上限失效，但构成输入选择偏差边界。

|预算协议|方法|输入|Top1 %|Top10 %|MRR@10|
|---|---|---|---:|---:|---:|
|BYTE|bm25|LITERAL_PLUS_RELATIONS|1.128|17.026|0.04166|
|BYTE|bm25|LITERAL|1.128|17.026|0.04166|
|BYTE|bm25|RAW_PLUS_LITERAL|0.718|16.308|0.03646|
|BYTE|bm25|RAW|1.231|13.538|0.03564|
|BYTE|char|LITERAL_PLUS_RELATIONS|0.821|9.846|0.03209|
|BYTE|char|LITERAL|0.821|9.128|0.03066|
|BYTE|char|RAW_PLUS_LITERAL|0.923|13.744|0.03533|
|BYTE|char|RAW|1.846|14.872|0.05164|
|FEATURE|bm25|LITERAL_PLUS_RELATIONS|1.026|9.231|0.02994|
|FEATURE|bm25|LITERAL|1.026|9.231|0.02994|
|FEATURE|bm25|RAW_PLUS_LITERAL|1.026|9.333|0.03235|
|FEATURE|bm25|RAW|1.436|11.077|0.03749|
|FEATURE|char|LITERAL_PLUS_RELATIONS|0.615|3.385|0.01072|
|FEATURE|char|LITERAL|0.615|3.385|0.01072|
|FEATURE|char|RAW_PLUS_LITERAL|1.641|6.667|0.02423|
|FEATURE|char|RAW|2.872|11.692|0.04614|
|FEATURE|literal_jaccard|LITERAL|0.410|7.077|0.02227|


BYTE BM25 Literal较RAW Top10上升3.487个百分点，MRR上升约.0061；但FEATURE同对照Top10下降1.846个百分点，字符方法亦退化。小幅字节预算结果不构成稳定算法贡献。

关系模块在K2下多数条件与Literal完全相同。必须补充：BM25原生关系/normalized_action标记不在知识文档词表，得分通道不活跃；char则没有显式结构组合能力。故目前既不能宣称关系独立增益，也不能将零增益概括为关系语义无价值。见results/INHERITED_SCORER_CHANNEL_AUDIT.json。实际feature预算对照有时进一步截断掉关系，不能冒称关系充分暴露。

清洗、去角色、去结果、去动作规范化均已执行，并保存负结果。词汇与字面机制匹配不足以检验GTE机制能力。MATCHED_K2字面匹配Top10=7.077%，MRR=.02227，未超过FEATURE K2 RAW字符11.692%或BM25 11.077%。原完整卡片字面匹配Top10=4.308%，不能跨预算称更差或更优。

30例独立固定后保留，逐例真实top10、官方标签、错误层次见results/DIAGNOSTIC_30_ANALYSIS.jsonl，属于管理员文件，不送盲审。未把每例标为“缺乏机制理解”或“局部证据不充分”：后两种因果归因还没有人工参考。当前不能估计可观测性错误的占比。
