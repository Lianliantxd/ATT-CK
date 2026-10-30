# 图目录

1. figures/figure01_candidate_competition.pdf / .svg / .png。源results/NEURAL_CANDIDATE_DIAGNOSTICS.csv；x=候选20/50/100，y=候选命中率与CE Top10。目的：分离召回和候选内排序。应观察召回升而Top10降；改变的判断是不能继续仅扩大候选池。无误差条，为同975开发查询的描述结果；不是独立攻击统计或机制归因。
2. figures/figure02_budget_sensitivity.pdf / .svg / .png。源MECHANISM_BASELINE_RESULTS.csv；4面板为BYTE/FEATURE×字符/BM25，4输入、统一K2，y=Top10%。目的：检查字面/关系效果是否跨预算保留；观察BYTE BM25小增益在FEATURE不保留。无误差条；各协议有共同观察但跨协议观察长度不同。不能解释为GTE机制实验，也不能因关系通道不活跃宣称关系理论失败。
