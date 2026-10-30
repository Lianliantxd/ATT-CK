# 融合与校准独立复算

状态：PASS_WITH_SCOPE_LIMITATIONS。独立脚本未导入fusion.core，也未打开外层保留Gold。冻结登记SHA-256为cceb35fc46eaeb5cc4db5973e315ab0a7288cbac5a1d0d1722031944a42289e3，与拟合和预测回执一致。

已重新计算42配置的全部归一化统计、1722组内部验证指标、462个选中条件，选参差异0。归一化只使用TRAIN唯一训练步骤r0；Seen与频率支持直接从每折one_view训练标签重新统计。内部验证先在每一步内平均5次采样，再对步骤平均Seen/Unseen MRR，随后求H；按H、总体MRR和登记顺序选择。未达10步骤与Seen/Unseen各3步骤时使用登记默认值。

| 折 | 内验证步骤 | Seen目标步骤 | Unseen目标步骤 | 允许选参 |
|---|---:|---:|---:|---|
| fold_heldout_1 | 25 | 19 | 11 | True |
| fold_heldout_2 | 45 | 29 | 22 | True |
| fold_heldout_3 | 19 | 16 | 5 | True |
| fold_heldout_4 | 2 | 1 | 2 | False |
| fold_heldout_5 | 46 | 22 | 30 | True |
| fold_heldout_6 | 12 | 11 | 3 | True |
| fold_heldout_7 | 44 | 29 | 23 | True |

选择原因计数：{'FIXED_METHOD': 210, 'INNER_VALIDATION_H_THEN_MRR_THEN_GRID_ORDER': 216, 'REGISTERED_DEFAULT_INSUFFICIENT_VALIDATION_SUPPORT': 36}。全部验证指标最大数值差0；不是利用外层保留Gold重新选择。

11种主条件64350条及4个固定gamma敏感性条件23400条，共18954000个216列分数逐项复算；最大绝对差0，完整216排名差异0。B3缺失类别保持NaN/null及末尾字典序，不进入监督残差；RRF只在Seen列产生监督排名贡献。C3与C4(gamma=0)在168种配置/强度对照中精确相同，明确属于嵌套简单方法。

实际拟合read_paths中的reference只包含7个对应fold validation_reference。逐selected记录的路径、hash、矩阵fold与代码当前fold路径构造一致；预测read_paths没有任何reference或旧split。校准、预测和独立审核均未读取附带heldout标签摘要的旧split JSON。归一化train ID与heldout/validation互斥；参数文件hash在预测启动时与拟合回执一致。代码与read_paths提供应用级可审计证据，不能替代操作系统级访问证明。

本审计仅确认计算、登记一致性与输入隔离，不根据分数宣称模型有效，也不替代独立指标审核。当前实验仍为DEVELOPMENT_ONLY。

## 全会话Gold访问时序限制

主agent向本审核披露：评价agent在主预测完成前的setup阶段读取旧heldout_reference，只用于核对已知975查询、195逻辑步骤和7场景计数；未提前计算本轮融合外层指标、未向拟合器或预测器传递Gold、未因此调整参数。这属于全会话Gold访问的时序偏差，因此不能声称本会话任何进程都未提前访问Gold。

可独立核验的较窄结论是：fit/predict的read_paths与代码未读取外层reference，参数hash在拟合后与预测前一致，本审核重算全部选参和预测精确吻合。评价agent的setup时序来自主agent披露，不伪称操作系统审计所得。详情与证据类型见EVALUATOR_GOLD_ACCESS_TIMING_DISCLOSURE.json。该偏差与已曝光开发集性质共同限制结论，不改变分数和选参复算通过的事实。
