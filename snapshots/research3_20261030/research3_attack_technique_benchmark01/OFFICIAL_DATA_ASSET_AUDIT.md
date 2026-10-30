# 官方资产审计（2026-10-27）

确认：已有合法下载的CAM-LDS v2 filtered归档，213,771,977字节，MD5 `cfc14140b2e396a60989b8379eafca1f` 与Zenodo当前API一致。SHA256见清单，与旧ACQUISITION一致。本轮不解压、不读取归档成员正文，不重复下载。旧下载许可限定的21文件范围不被当作本轮任意旧文件读取授权。

新取得：官方仓库提交 `42bbd2cf8409f64a1e6c8fc936c91725e8c558b2` 的查询、标签、历史响应、知识矩阵、README、GPL-3.0许可证和评价/生成脚本。仓库JSON后缀中，查询与响应实际是JSONL，不能用json.load读取整个文件。

官方预制查询来自v1；不能宣称它是v2重建查询。v2包含不同Docker audit事件，见官方README。本轮P0受限子集：975记录、195场景步骤、34个被选择的模拟执行标识、7场景、79父技术（原粒度94ID）。多父标签285/975=29.23%，57/195步骤。母文件990查询/198步；排除场景1的35—37步全部变体共15查询。受限正文不进入解析/模型输入；标签文件只使用metadata键。

无缺失标签、无query/official-label冲突、无空日志输入。清洗后385种不同提示词，590条为重复内容。五次采样绝非五次独立攻击。标签来源资格为AUTHOR_ASSIGNED_TECHNIQUE，未人工逐条认证LOG_EVIDENCE_OBSERVABLE或TECHNIQUE_CONFIRMED_FROM_LOG。

查询允许本地新推理；公开历史响应只用于AUTHOR_PREDICTION_METRIC_RECALCULATION及离线误差分析。没有重跑LLM。数据CC-BY-4.0、代码GPL-3.0；本轮私有研究副本不构成公开再分发许可判定。官方matrix无版本号/描述/弃用状态字段，因此不能认证确切ATT&CK发行版本。

清单包含绝对路径、文件大小、SHA256、固定提交与取得方式。旧CAM目的卡未当作技术GT。
