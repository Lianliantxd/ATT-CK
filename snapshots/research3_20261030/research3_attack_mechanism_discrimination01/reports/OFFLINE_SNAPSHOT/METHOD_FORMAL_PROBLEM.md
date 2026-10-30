# 问题形式与实际最小实现

给定冻结合法日志L、知识K和216技术集合T，构造z=phi(L)，认证原生关系R=g(z)。phi只读取原生字段/源span，g只在同source的明确audit key或时间字段上产生关系；未知身份、结果和状态变化保留UNKNOWN。卡片C_t=h(K_t)是知识词形与原文片段，不是必要条件逻辑公式。

技术排名为rank_t s_theta(render(z,R),render(C_t))。本轮theta只有冻结CharacterNgramTFIDF、BM25与简单动作/对象Jaccard；未训练新参数，未新增GTE前向。LiteralMechanismMatching使用两个集合相似度等权和，不采用技术专属规则，不输出机制充分性真值。

评价目标是步骤级多标签Top1/5/10、MRR@10、Precision/Recall/F1；机制语义支持判断是另一任务，缺独立人工参考时不可评分。日志不完整时不以机制未出现构成NOT_OCCURRED；技术描述常见手段不强制为所有实例必要条件。

实际假设是“同观察和检索器下显式表示是否改善排名”，不是已经建立新理论。P0已暴露，脚本/场景相关；本轮结果不能证明外部泛化，也不触发RL、DGPR或大型知识图谱开发。
