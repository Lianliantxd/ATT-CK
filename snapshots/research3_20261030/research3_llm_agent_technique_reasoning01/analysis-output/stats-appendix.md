# 统计附录

- ADAPTIVE_HEURISTIC_S−STATIC_BM25_S top1: Δ=-0.012987; 95% cluster interval [-0.028777, 0.003521]; scene macro Δ±SD=-0.010217±0.020005; exact signflip p=0.375000, Holm p=1.000000.
- ADAPTIVE_HEURISTIC_S−STATIC_BM25_S top10: Δ=-0.018182; 95% cluster interval [-0.046693, 0.000000]; scene macro Δ±SD=-0.037458±0.060995; exact signflip p=0.250000, Holm p=1.000000.
- ADAPTIVE_HEURISTIC_S−STATIC_BM25_S mrr: Δ=-0.008864; 95% cluster interval [-0.021717, 0.006015]; scene macro Δ±SD=-0.009537±0.015243; exact signflip p=0.281250, Holm p=1.000000.
- ADAPTIVE_HEURISTIC_M−STATIC_BM25_M top1: Δ=0.007792; 95% cluster interval [-0.014493, 0.027888]; scene macro Δ±SD=0.010978±0.040316; exact signflip p=0.625000, Holm p=1.000000.
- ADAPTIVE_HEURISTIC_M−STATIC_BM25_M top10: Δ=-0.002597; 95% cluster interval [-0.029851, 0.009479]; scene macro Δ±SD=-0.026257±0.066383; exact signflip p=1.000000, Holm p=1.000000.
- ADAPTIVE_HEURISTIC_M−STATIC_BM25_M mrr: Δ=0.002579; 95% cluster interval [-0.013156, 0.013256]; scene macro Δ±SD=0.001590±0.023609; exact signflip p=0.625000, Holm p=1.000000.

Bootstrap重抽7场景并将簇内执行—步骤一起保留，分母随抽取簇大小变化。区间为事后描述性敏感性分析；7簇过少、场景并非随机独立抽样，因此不作总体保证。符号翻转枚举128种、双侧，以簇内配对差和为统计量；要求场景差分交换对称且场景独立，当前不能充分确认。六比较Holm校正仅为探索信息，不生成显著性或泛化结论。未使用t检验，不声称正态；不因正态性检验未拒绝就认定正态。Δ是原始效应量；场景SD不是随机种子SD。LLM小样本且缺失不均，禁止显著性与收益结论。
