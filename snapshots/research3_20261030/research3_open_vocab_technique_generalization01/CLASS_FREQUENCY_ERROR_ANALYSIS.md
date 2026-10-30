# 类别频率与识别收益

ONE主要协议：C0只按唯一训练步骤支持排序，MRR=0.161331；S0=0.202153，两者数值之比79.81%。该比值不是“解释了多少方差”或因果贡献率。C0不用日志特征就可取得相当比例成绩，说明总体MRR受常见训练标签强烈影响；S0仍比C0高0.040822，不能把全部监督收益归为先验。

C0在SUPPORT_GE5目标的MRR=.550167，S0=.550887；但C0在one-shot为0、few-shot=.001667、unseen=0。频率表现集中于高支持类，不能代表普遍语义识别。C4在few-shot MRR=.157132高于S0的.137544；one-shot MRR=.033333高于S0 .015556，但Top10 .033333低于S0 .044444。不同指标不能互相替代。

C5(zGTE+训练先验)总体MRR=.143734，Unseen=.012296；P2(监督分数减训练先验)MRR=.174875、Unseen=0。它们说明频率修正改变排序，但不是对模型内部“理解”或遗忘的因果诊断。

下列Spearman仅描述每个有Gold的(fold,technique)在种子平均后的支持—性能增量关系。同一技术跨折重复、训练组重叠，不能将这些点当独立数据做p检验。全部32行相关性见results/FREQUENCY_PERFORMANCE_ASSOCIATION.csv；无保留分布进入预测先验，无关联结果用于参数选择。

|方法−对照|目标范围|指标|pair数|Spearman|
|---|---|---|---:|---:|
|S0−Z0|ALL_TARGET_CLASSES|mrr|133|0.4303|
|S0−Z0|ALL_TARGET_CLASSES|recall10|133|0.3918|
|S0−Z0|SEEN_TARGET_CLASSES|mrr|75|0.4212|
|S0−Z0|SEEN_TARGET_CLASSES|recall10|75|0.3736|
|C4−Z0|ALL_TARGET_CLASSES|mrr|133|0.4849|
|C4−Z0|ALL_TARGET_CLASSES|recall10|133|0.4560|
|C4−Z0|SEEN_TARGET_CLASSES|mrr|75|0.3862|
|C4−Z0|SEEN_TARGET_CLASSES|recall10|75|0.3893|
|C4−S0|ALL_TARGET_CLASSES|mrr|133|-0.2772|
|C4−S0|ALL_TARGET_CLASSES|recall10|133|-0.2843|
|C4−S0|SEEN_TARGET_CLASSES|mrr|75|-0.2688|
|C4−S0|SEEN_TARGET_CLASSES|recall10|75|-0.2733|
|C0−Z0|ALL_TARGET_CLASSES|mrr|133|0.3173|
|C0−Z0|ALL_TARGET_CLASSES|recall10|133|0.3119|
|C0−Z0|SEEN_TARGET_CLASSES|mrr|75|0.4916|
|C0−Z0|SEEN_TARGET_CLASSES|recall10|75|0.4907|
