# GO / NO-GO

主状态：MECHANISM_REPRESENTATION_EXECUTED。

次状态：RERANKER_FAILURE_DIAGNOSED（保存分数层面；运行时维度/独立批次复测仍缺）、NO_SUPPORTED_ALGORITHMIC_GAIN（仅已执行非神经实验）、MODEL_FORWARD_AUTHORIZATION_BLOCKED、EXTERNAL_TEST_NOT_READY。不使用PAPER_READY或GENERALIZATION_PROVEN。

NO-GO：当前Literal/Relations/卡片组合作为已验证独立算法贡献；不增加规则、图复杂度、reflection、RL或DGPR-V3。BM25 Literal有小幅开发数值提升但不稳健，字符检索退化；卡片成绩受词汇和可见知识分配混杂，关系在BM25的评分通道没有生效，CHAR也未支持稳定收益。工程可追溯性成立，机制语义准确性尚未独立认证。

条件GO：保留可追溯IR作为诊断工具。若用户批准已具体列出的新前向，执行同固定模型/同观察的神经表示对照；未批准就保持NA。先确认表示的新增机制特征实际进入评分（当前BM25关系/动作标签通道未生效），再完成30例真实独立审查，区分不可观察标签、动作/对象绑定错误和模型相关性偏差。只有证据显示表示本身有独立价值才继续机制判别；否则优先考虑领域对比学习/困难负例适配，但本轮不启动训练。
