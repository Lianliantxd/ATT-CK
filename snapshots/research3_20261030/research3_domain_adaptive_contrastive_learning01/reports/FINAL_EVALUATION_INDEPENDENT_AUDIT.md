# 最终评价与数据边界独立复算

审查状态：**PASS_WITH_DOCUMENTED_LIMITATIONS**。

仅读取本地已保存预测和数据协议，以独立标准库实现重算排名、多标签Precision/Recall/F1及汇总；未调用项目评价器实现，未训练、未进行模型前向、未访问服务器。

核实380个预测文件、1106个评价分区条件；外层392条件共54,600条预测。每个方法/种子/增强恰好覆盖975条保留查询，完整216候选未删减。

全部3472个分层条件、56个种子汇总和20个方法/增强汇总完成独立复算；逐样本表及最终导出与源预测一致。4项主假设×2增强×7场景的56行种子均值差均复算一致，没有确认性p值。

注册划分及双份实际文件SHA256一致：`879bac94d85a5106a36345b9d9ce3f85f0b383978d8a6b914bb2cec1374bd96d`。训练、验证、保留分区与合法ID完全对应，训练诊断限r0，已识别共享全窗口不跨角色。

必须保留的解释限制：

- PUBLIC_EXPOSED_DEVELOPMENT; not independent external test
- Exact original script identity UNKNOWN; full-window purge does not establish absence of shared script/partial-log leakage
- Seeds and five samples are repeated observations, not independent attacks
- LOSO training sets overlap;7scenarios support descriptive grouped development only
- Scene5 has2logical steps; inner validation of fold4 is extremely small
- Gold-subset P/F1 counts other-subset true labels outside the current target; subset MRR/Top10 have clearer interpretation
- Author-assigned step labels are not observation-verified mechanism annotations
