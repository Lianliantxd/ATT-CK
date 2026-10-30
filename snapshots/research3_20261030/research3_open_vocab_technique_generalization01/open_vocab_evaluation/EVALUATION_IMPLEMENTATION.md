# 独立广义零样本评价实现

本目录仅从已保存预测计算指标，不产生模型分数、不校准参数、不训练、不访问服务器。外层参考仅在完整216候选预测保存后，由评价器读取冻结的逐折 `heldout_reference`。评价输出属于 `PUBLIC_EXPOSED_DEVELOPMENT`。

`evaluate_saved.py` 使用标准库独立实现排名、多标签Precision/Recall和F1，再以旧冻结 `evaluate_techniques.py` 对每一条件的总体和全部非空目标/样本/支持桶分层逐项交叉复算。历史 Z0/B1、S0/B3、C6_B4/B4、C6_B5/B5 指标额外与旧保存指标核对。所有读操作使用 `python -B`，旧目录保持只读。

## 指标与分层

- Top-K为至少命中一个当前目标Gold的查询比例；MRR截断在10；Precision为命中数/K；Recall为命中数/当前目标Gold数量。
- F1@5以Top5候选集合计算。Macro-F1始终平均固定216类，分母为0的类F1按0计入；未出现的类不会从216分母删除。
- Seen/Unseen定义来自该折合法训练集合，并与重建分数矩阵中 `seen`、`support>0` 核对。
- Seen-target与Unseen-target只限制Gold，完整216候选预测及其排序不变。Mixed查询会出现在两个目标子集中；670与450不能相加当作独立样本数。
- ALL_SEEN、ALL_UNSEEN、MIXED为互斥样本分组；525+305+145=975。父技术单标签690、多标签285。
- Gold目标子集中的Precision/F1会把另一目标子集中的真实标签作为当前目标的FP，因此子集解释主要使用MRR、Top10和Recall10。
- 无当前目标的条件为NA；不得以0代替缺失目标。存在目标但无命中才计0。
- 支持桶固定为0、1、2—4、至少5个唯一训练逻辑步骤。长尾表同时保存查询加权指标与按有Gold的 `(fold, technique)` 等权的类MRR/Recall10；全216逐类表包含没有评价正例的类，其类MRR/Recall为NA。
- 某项技术可以在不同折进入不同支持桶；桶内跨折唯一技术数不能相加当作216类的互斥划分。`candidate_fold_technique_pairs` 按折—技术组合计数，4桶合计应为7×216；每一折内才是互斥的216类划分。

## 汇总与不确定性

每个方法、随机种子和视图恰好覆盖975查询、195逻辑步骤、7个场景。根 `FUSION_RESULTS.csv` 为3个种子的均值，`*_seed_SD` 为样本标准差（ddof=1），只描述训练或校准波动，不是3组独立攻击的不确定性。

查询加权指标从所有保留查询合并计算；场景等权指标先计算每个场景再平均，非空目标场景数明确报告。尤其Macro-F1、调和平均不通过样本数简单加权恢复。

主 `H_MRR` 先分别计算跨折Seen-target和Unseen-target查询加权MRR，再计算 `2SU/(S+U)`。S+U为0时H=0；缺少任一目标时H=NA。`H_MRR_equal_scene_mean` 先逐场景计算H再平均；`harmonic_of_equal_scene_MRR` 则对场景等权的S、U再取调和平均，两者分别保存，禁止混用。Top10与Recall10同理。

H1为C4−Z0，H2为C4−S0，H3为C1−Z0；每项保存7场景、2视图的种子均值差值。删除一个场景后的变化范围是描述性敏感性分析，不能称为置信区间。975查询包含同一步骤5次采样，训练种子重复、LOSO训练集重叠且场景已曝光，因此不计算普通IID显著性检验或确认性p值。

## Tradeoff

`--tradeoff` 单独读取已保存的C4 selected-lambda×gamma `{0,0.1,0.2,0.4}` 预测。它展示外层评价中的Seen/Unseen取舍，不参与参数选择、不计算运行后选择定义的AUC。主方法选定参数仍以冻结的内验证选择记录为准。

## 逐样本排序现象

`results/RANK_FAILURE_PHENOMENA.csv` 只包含有Unseen目标的450查询/条件。四种标记不是互斥原因，计数不能相加作为独立错误总数。

- D1：仅S0/P2对存在Unseen Gold的查询标记结构性分类器缺失。
- D2：仅开放融合/校准/描述头C1—C5、C6_B4、C6_B5；Z0能在Top10命中Unseen Gold，当前方法不能，且当前Top10至少包含一个Seen类别。这样至少一个Seen类别确实排在被排除的正确Unseen之前；该标记仍只是已见分数竞争的候选排序现象，不能证明因果。
- D3：当前方法未命中Unseen Gold，Z0同样未命中；只说明冻结语义检索在该截断下也有限，不能断言日志缺证据或攻击机制未发生。
- D4：Mixed查询当前方法命中Seen Gold而未命中Unseen Gold。

所有具体语义与因果解释保留 `UNRESOLVED`。另外记录相对Z0的Unseen恢复/丢失数量和全216最佳Unseen排名差，保留反例与负结果。

## 执行与输出

主评价：`python -B open_vocab_evaluation/evaluate_saved.py`。

曲线评价：`python -B open_vocab_evaluation/evaluate_saved.py --tradeoff`。

`results/EVALUATION_AUDIT.json` 与 `results/TRADEOFF_EVALUATION_AUDIT.json` 记录预测、评价器、旧冻结评价器、划分和分数矩阵SHA256，以及真实交叉复算次数和最大差值。代码中的最小合成边界测试只验证数学实现，未保存为任何实验预测或研究性能。
