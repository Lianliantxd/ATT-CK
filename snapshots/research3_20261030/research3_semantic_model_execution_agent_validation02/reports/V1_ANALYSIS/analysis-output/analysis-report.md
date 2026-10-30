# 严格分析：配对、指标与分母

主问题：固定预训练模型在相同观察和公开知识预算下是否改善父技术排名？次问题：同固定LLM、同合法池及证据cap下动态查询是否有独立收益？

| 方法 | N | Top1 | Top10 | MRR@10 |
| --- | --- | --- | --- | --- |
| E1_NATIVE_PREFIX | 975 | 3.79% | 28.00% | 0.1031 |
| E2_NATIVE_FIELDS_PREFIX | 975 | 3.08% | 22.67% | 0.0797 |
| E3_NATIVE_WINDOW_DIRECT | 975 | 6.15% | 29.85% | 0.1246 |
| E4_NATIVE_WINDOW_CHUNK_MAX | 975 | 3.79% | 27.18% | 0.0982 |
| E5_NATIVE_WINDOW_CHUNK_MEAN | 975 | 2.36% | 28.72% | 0.0913 |
| M0_MATCHED_E1_NATIVE_PREFIX | 975 | 9.23% | 28.51% | 0.1385 |
| M0_MATCHED_E2_NATIVE_FIELDS_PREFIX | 975 | 5.03% | 26.77% | 0.1008 |
| M0_MATCHED_E3_NATIVE_WINDOW_DIRECT | 975 | 8.41% | 26.67% | 0.1260 |
| GTE_RERANKER_EMBEDDING_TOP100 | 975 | 2.05% | 12.72% | 0.0427 |
| GTE_RERANKER_EMBEDDING_TOP20 | 975 | 2.05% | 33.03% | 0.0874 |
| GTE_RERANKER_EMBEDDING_TOP50 | 975 | 2.26% | 16.41% | 0.0522 |
| GTE_RERANKER_LEXICAL_TOP100 | 975 | 1.33% | 9.85% | 0.0295 |
| GTE_RERANKER_LEXICAL_TOP20 | 975 | 2.36% | 20.82% | 0.0582 |
| GTE_RERANKER_LEXICAL_TOP50 | 975 | 1.23% | 12.72% | 0.0357 |

原生预测13650行=5×975 Embedding+3×975 matched lexical+6×975 CE。每条件975个唯一sample_id，195个逻辑步骤、7场景、34执行标识；不是975个独立样本。全部预测先固定，Gold只在本地离线进入冻结V1评价器。MRR仅前10，父技术归一化，multi-label recall与any-Gold hit区分。

主比较E1与matched prefix lexical：Top10差-0.51个百分点，MRR差-.0354；窗口matched比较Top10+3.18个百分点，MRR差-.0013。CE Embed20对E1的Top10+5.03个百分点，MRR-.0157。26个探索性对比检验统一Holm校正，未支持CE Embed20 Top10的确认性增益。主表显示全部条件，不选择最高分作为独立测试结论。

Claim candidates：
- 两种预训练模型已全P0真实推理并评价。证据：原生GPU预测/哈希/预检/日志。允许“基线已运行”，禁止“泛化已证明”；不确定性为数据相关性；决定keep。
- Embedding Top100覆盖优于匹配词法。证据：候选召回表。允许“开发集覆盖较高”，禁止“全面排序更好”；单seed/领域限制；下一步独立数据；决定weaken。
- CE扩大候选有候选内降级。证据：排名转移表。允许“本模型本协议观察到”，禁止“所有CE不适用”；因果机制未知；下一步机制标注；决定keep。
- Agent未证明增益。证据：严格同案N1/N2且无超越。允许“未支持”，禁止“普遍无效”；功效极低；下一步输出资格和证据干预；决定weaken。
