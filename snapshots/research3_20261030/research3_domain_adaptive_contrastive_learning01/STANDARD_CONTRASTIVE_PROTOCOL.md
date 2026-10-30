# 标准训练协议

固定协议见manifests/TRAINING_PROTOCOL.json。B4使用逐行正/未标注集合平衡的sigmoid BCE；B5使用全216类多正例平均log-softmax，不只取第一个正例；B6与B5代码共享，仅将未标注分母候选从全部改为32个随机候选，不能据命名宣称两个独立创新。GTE主干始终冻结，只更新两个768×32投影头（49152参数）。3固定种子，120等预算更新，无超参搜索/外层标签早停。

训练器只读取本折train Gold，validation与heldout只输入文本；标签由独立评价器在预测固定后读取。7外层场景仅属GROUPED_DEVELOPMENT_VALIDATION；相同逻辑步骤5视图被当增强而非5个独立标签对象。ONE固定r0，MULTI按(epoch+seed)%5，每轮每步骤一view。固定循环种子和相同更新数控制计算与标签曝光。
