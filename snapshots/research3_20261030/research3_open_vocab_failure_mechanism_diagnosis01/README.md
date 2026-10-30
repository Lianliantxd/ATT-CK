# R3_OPEN_VOCAB_FAILURE_MECHANISM_DIAGNOSIS01

主报告：R3_OPEN_VOCAB_FAILURE_MECHANISM_DIAGNOSIS_RESULTS.md。已完成收到的前五节及核心基础召回诊断；最新附件在6.1单个项目符号处截断，未编造后续要求。

当前结论：450含Unseen查询=34保留+32融合丢失+35原跨类阻挡候选+349未见内部序障碍。仅是DEVELOPMENT_ONLY离线诊断，不修改原模型/参数/预测。未访问服务器、未训练、未调用新模型、未搜索参数。

候选全表是gzip CSV，以fold+seed+view+sample+technique为键；B3不存在分类器时空分数+明确状态。原GTE分数与C4标准化分数单位不同。反事实文件只作诊断，不能作为模型正式成绩。

旧主报告一个空格导致历史SHA不同，差异已记录且不修复旧文件；其余数值资产通过。所有被引用的旧文件按本轮开始状态保留；最终检查见results/FINAL_VALIDATION.json与manifests/DELIVERY_SHA256.json。

证据卡处理需要运行qualify_evidence_cards.py，将“有限视图”与“实际被截断”区分；真实截断/机制可观测性未独立认证。全量Gold只用于后验诊断。无Obsidian回写。
