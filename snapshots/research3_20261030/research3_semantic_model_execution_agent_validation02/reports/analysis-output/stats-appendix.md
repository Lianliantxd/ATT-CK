# 统计口径

seed42一次确定性推理，无训练重复；不报告跨seed mean±std。逐查询描述值与195逻辑步骤等权macro同时给出，P0每逻辑步骤5查询，宏均值一致。7场景/34执行逐组结果保存，相关执行和脚本不能当独立测试。

NEURAL_EXPLORATORY_PAIRED_STATS.csv：13个预列分析对比×Top10/MRR两指标=26项。每个逻辑步骤先平均5查询的成对差，报告195个差的mean、SD、5000次有放回bootstrap percentile95%CI，10000次sign-flip（+1修正）双侧p；全26项Holm校正。随机seed42。

条件假设：逻辑步骤对比差可交换且近似独立。相同场景/脚本可违反此假设，故这些CI/p仅为暴露开发集的探索性条件量，不能支持场景或外部泛化。离散成对差不服从正态的默认假设，因此不使用普通独立t检验。bootstrap CI与离散sign-flip p可能不完全一致；不得选择性使用CI或未校正p。

CE Embed20 vs E1：Top10 delta .050256，SD .352513，95%CI [.002051,.098462]，raw p .053695，Holm p .644336；MRR delta -.017950，CI[-.045735,.010360]，Holm p1。不能据正CI边界宣称确认性显著收益。窗口E3 vs matched TF-IDF Top10 delta .033846，CI[-.045128,.112821]，Holm p1；MRR delta+.001076，CI[-.048047,.048004]。

Agent严格有效对仅N1或N2，选择性有效输出导致条件选择偏差；不做显著性检验、置信泛化或效果因果估计。提供valid-only、model-attempted failures-empty和planned-system三分母；超时算实际请求，context调用前失败只进入系统分母。历史54条与本轮预算完全独立。
