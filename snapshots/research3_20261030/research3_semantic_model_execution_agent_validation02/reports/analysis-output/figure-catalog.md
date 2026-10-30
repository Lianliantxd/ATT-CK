# 图目录与解释要求

figure-01-main.pdf/svg/png：全部值来自EMBEDDING_REAL_RESULTS.csv及RERANKER_REAL_RESULTS.csv。目的：分开Top10覆盖与靠前排序；读者应看到CE Embed20 Top10上升而MRR下降，字段/分块没有一致改善。下一步应验证机制判别，而非只最大化Top10。柱无误差条，是975查询描述统计；相关性、单seed、EXPOSED_DEV必须随图注明。PNG已目视核验，数值没有溢出、遮挡。

figure-02-candidates.pdf/svg/png：来源RERANKER_CANDIDATE_UPPER_BOUNDS.csv。目的：区分召回上界和排序转化；K增加提高CandidateHit却使实际Top10下降。上界指至少一个Gold进入候选，不是多标签全覆盖。下一步优先检查候选内判别；图不能证明缺哪类语义。柱无CI，比例是全部975查询描述值。
