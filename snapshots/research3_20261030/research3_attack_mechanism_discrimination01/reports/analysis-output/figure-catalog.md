# 图解释

figure-01-mechanism.pdf/svg/png：同一观测、检索器、描述或卡片的Top10比较，取MECHANISM_BASELINE_RESULTS.csv。看Literal在CHAR退化、BM25提升但不稳定，以及Relations缺乏独立收益；决定不继续叠加关系复杂度。无误差条，是975查询描述统计，单协议EXPOSED_DEV；推断区间另见统计表。

figure-02-knowledge-control.pdf/svg/png：卡片/只从可见前缀提取卡片/相同词频乱序控制。它区分结构、词汇和知识内容分配。BM25乱序完全同分同排名，不能将卡片提升归因结构推理；CHAR变化也可能只是字符n-gram邻接。posthoc控制，不能据此提出确认性新方法。

figure-03-neural.pdf/svg/png：真实固定GTE Embedding/CE的4日志×2知识Top10；数据NEURAL_BASELINE_RESULTS，刻度一致，无误差条。CE所有视图统一旧Top20，与Embedding全216不可解释为纯模型能力差。观察同模型表示变化；按292联合检验与Token信息预算边界解释，不选择最高柱宣称泛化。
