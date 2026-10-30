# 科研决策

主状态：**OPEN_VOCAB_TRADEOFF_UNRESOLVED**。

次状态：OPEN_VOCAB_BASELINES_EVALUATED；UNSEEN_RANKING_RECOVERED_ON_DEV；EXTERNAL_TEST_NOT_READY；NO_SUPPORTED_NEW_ALGORITHMIC_GAIN。全部DEVELOPMENT_ONLY。

C4较B3恢复Unseen MRR到.023053，但Seen只保留59.30%，Unseen只保留Z0的51.85%；未达到预登记Seen≥50%且Unseen≥80%的联合工作阈值。C3的总体/H略高于C4，RRF/频率/旧B3也完整保留。正式模型中Z0的H最高，S0总体MRR最高；没有证据支持把残差公式视作独立新算法。

固定曲线gamma=.4点的H=.053182高于Z0 .049493，说明不是所有简单参数都无法改善H；但该点是在外层诊断中观察到，不能据此改正式模型或称为新的无偏验证成绩。其Unseen仍只保留Z0约72.46%。目前的问题同时包含有限语义召回、类间竞争、薄弱内部参数选择和长尾覆盖，不能归为一个已证实因果机制。

GO：保留本轮完整分数/成熟简单融合为后续强基线，优先补全独立执行来源和非穷尽Bag标签评价接口。NO-GO：本轮算法创新成立、跨来源泛化成立、继续扩大已曝光P0搜索、直接LoRA或新GPU训练。

候选研究问题是如何在不泄漏标签的条件下保持未见语义排名及Mixed双目标覆盖，并在更可靠内部划分上选择校准。它是问题定位，不是新算法贡献证明。后续新数据模型前向与训练需独立明确范围，当前完成后停止。
