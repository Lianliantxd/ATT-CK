# D1—D6实际离线诊断

D1继承canonical E1 Embedding原始排名；D2依据官方高logit方向重建CE；D3比较Top20/50/100；D4计算每条件Spearman；D5逐样本逐候选核对分数；D6保存所有候选的升降级及分层错误。历史D1—D6仍为离线复算；新授权GPU主实验及sanity另见reports/GPU_MAIN_EXPERIMENT_RESULTS.md。

| pool | K | N | CANDIDATE_NOT_RETRIEVED | CANDIDATE_RETRIEVED_BUT_RANKED_LOW | CANDIDATE_DEMOTED_BY_RERANKER | CANDIDATE_PROMOTED_BY_RERANKER | mean_Spearman |
| --- | --- | --- | --- | --- | --- | --- | --- |
| embedding | 20 | 975 | 520 | 71 | 55 | 104 | 0.0679467900520532 |
| embedding | 50 | 975 | 313 | 303 | 194 | 79 | 0.06527051435958998 |
| embedding | 100 | 975 | 101 | 518 | 232 | 76 | 0.08451668551470531 |
| lexical | 20 | 975 | 569 | 61 | 135 | 60 | -0.15104222093695777 |
| lexical | 50 | 975 | 372 | 253 | 221 | 65 | -0.08830535291039493 |
| lexical | 100 | 975 | 186 | 439 | 254 | 65 | 0.01372150753536892 |

Embedding Top100：101/975无Gold候选；750/975有候选Gold但最终前十没有Gold；另48原已命中仍命中、76原未前十而被提升。两类失败分别为10.36%与76.92%，不混称语义推理失败。Top20到100时部分非步骤Gold的高分候选替换Gold；最常见替换ID及次数：[['T1204', 199], ['T1601', 151], ['T1592', 144], ['T1574', 138], ['T1567', 116], ['T1561', 109], ['T1216', 106], ['T1071', 101]]。这些是相对步骤标签的非Gold，不表示该技术在日志中必然没有发生。

原排1—10/11—20/21—50/51—100的分数分布见SCORE_DISTRIBUTION_SUMMARY：候选池后部也存在高logit尾部。扩大池改变可竞争集合而非原对分数；排序相关性很低。可确认阶段为候选内排序，不足以确定原因是缺少机制理解。上游截取/领域适配/标签可观测性仍UNRESOLVED。没有修复方向/归一化或搜索融合权重，没有MODEL_SCORING_IMPLEMENTATION_CORRECTION贡献。
