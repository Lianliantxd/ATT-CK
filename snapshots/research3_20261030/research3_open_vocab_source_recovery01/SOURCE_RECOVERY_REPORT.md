# ATT&CK来源恢复报告

2026-10-29（Asia/Shanghai）。执行状态：**SOURCE_RECOVERY_COMPLETED_WITH_VERSION_AND_SCOPE_BLOCKERS**。

## 已完成与更正

从已有本地rp3_phase1_local_cache找到Enterprise ATT&CK19.2完整STIX快照，13种原先在16.1不存在的候选正文全部找到，无需网络或下载。本轮创建单一19.2来源的独立V2版本，保留原216候选ID且不截断父正文。

上一轮“13种缺少来源”只对当时检查的16.1文件成立；上一轮没有检查到本地19.2缓存，不能推广成整个工作区无来源。本轮更新这一阻断，并保留旧版及旧报告不变。

## 来源如何核实

缓存JSON的SHA256为dc1639caa5501d720e280cf1cbd8fbe009884a0c9b3e6e9ed9d0c25166c3d8f4。内部collection.x_mitre_version为19.2。原有2026-09-02本地SOURCE.md记录MITRE attack-stix-data官方仓库URL及同一hash，SHA256.txt也一致。压缩副本解压后字节完全相同，三个备份副本也相同。

这是现有来源记录+内部版本+字节一致性证明，不是本轮重新下载认证；官方上游精确gitcommit未恢复。作者matrix虽有仓库commit，但其ATT&CK发布版本仍未知，不声称19.2就是作者原始版本。

## 结果和跨版本差异

|项目|数量|含义|
|---|---:|---|
|保留原父候选ID|216|候选集未删减或替换|
|有同ID完整源正文|216|其中3个是已撤销对象|
|补齐上一版缺失正文|13|含T1672撤销对象的存档正文|
|有效源父对象|213|不是216项都有效|
|已撤销候选|3|T1562、T1656、T1672|
|与作者父名称不同|1|T1211，涉及范围/名称核验|
|与作者战术集合不同|47|源战术与原标签字段分列|
|原203项中正文发生变化|59|不是仅补13条，其它定义也变了|
|原203项中正文相同|144|按完整字符串比较|
|单独存储的子对象|480|包含撤销记录|
|有明确原父subtechnique-of关系的子对象|464|16项没有关系，未认证父子语义|
|父全文被截断|0|不等于Token预算已冻结|

RECOVERED_13_DEFINITIONS.csv逐项保存完整正文、字符/字节、对象ID、源位置、修改时间及状态。SOURCE_VERSION_MIGRATION.csv覆盖全部216项，保存16.1/19.2字段hash、命名、战术、状态及替代关系差异。没有读取日志去选择有利定义。

## 必须单独处理的撤销关系

|原候选|19.2明确revoked-by目标|本轮处理|
|---|---|---|
|T1562|T1685|保留旧ID及存档正文，不应用替换|
|T1656|T1684.001|保留旧ID，父级候选转子技术的粒度问题待裁定|
|T1672|T1684.002|保留旧ID，父级候选转子技术的粒度问题待裁定|

这些是源中实际关系，不是本轮AI推测。但是“被替代”不授权把原Gold自动改成新ID，更不证明旧标签错了。

T1211在作者matrix名为Exploitation for Defense Evasion，19.2名为Exploitation for Stealth。此前16.1相对作者的T1176/T1219名称差异，在19.2已同名；这仍不证明全部语义适用范围相同。4项具体合同问题列入CONTRACT_REVIEW_QUEUE；47项战术变化单独保留全量差异。16个无原父关系的子对象均已撤销，作为档案记录而非已核验的有效父子关系。

## 新知识版本具体是什么

KNOWLEDGE_V2_SOURCE19_2.json中216项都保存19.2同ID的完整源字段，并把作者元数据、源元数据、状态、子类型和替代关系分开。PARENT_ONLY_FULL_V2.json是源父名称+换行+完整description，不加名称/战术前缀，不混入子类型正文，也不裁剪。撤销3项明确标记待合同复核；未把它们伪装成当前有效技术。

上一版16.1知识和所有历史文件未改。这里不是给16.1补13条19.2后假装同版，而是新建单一19.2来源版本，因此59项既有正文改变已明确记录。没有新预测、标签纠错或模型收益。

## 当前科研决策

**GO_AFTER_LABEL_SCOPE_ADJUDICATION**。

“缺失行为正文”这个局部阻断已经解除，下一步优先确定旧216标签如何与19.2存档/有效定义比较，处理3个撤销ID和T1211范围问题，并继续对既有34条范围疑问建立独立人审。尚未具备GO_METHOD_EXPERIMENT资格，不能直接运行模型或称完整输入合同已通过。

保留旧候选与存档正文、或迁移到新有效ID是两种不同评价任务。当前只保存可审查材料，不自动选择会改变标签含义的迁移，不实施新Gold。作者矩阵确切版本未恢复仍是局限；若要求与原版严格同版，就仍需其生成/导出记录。

## 资源、完整性与停止

新增模型/Agent调用、训练、GPU、下载、网络、服务器、上传以及旧文件修改均为0。仅本地知识与已有回执静态处理。完整性范围为本轮登记输入，部分发现读取先于首次跟踪快照，不声称全工作区任务开始前快照。所有新产物只在本轮新目录。

机械验证与科学资格分开记录，最终结果见FINAL_VALIDATION。完成封存后停止，不自动开展标签迁移、模型实验或联系外部审查者。

## 交付导航

- [SOURCE_RECOVERY_REPORT.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/SOURCE_RECOVERY_REPORT.md)
- [knowledge/KNOWLEDGE_V2_SOURCE19_2.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/knowledge/KNOWLEDGE_V2_SOURCE19_2.json)
- [knowledge/PARENT_ONLY_FULL_V2.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/knowledge/PARENT_ONLY_FULL_V2.json)
- [SOURCE_VERSION_MIGRATION.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/SOURCE_VERSION_MIGRATION.csv)
- [RECOVERED_13_DEFINITIONS.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/RECOVERED_13_DEFINITIONS.csv)
- [REVOCATION_CROSSWALK_NOT_APPLIED.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/REVOCATION_CROSSWALK_NOT_APPLIED.csv)
- [CONTRACT_REVIEW_QUEUE.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/CONTRACT_REVIEW_QUEUE.csv)
- [PARENT_CHILD_SOURCE_AUDIT.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/PARENT_CHILD_SOURCE_AUDIT.csv)
- [audit/SOURCE_PROVENANCE_RECEIPT.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/audit/SOURCE_PROVENANCE_RECEIPT.json)
- [protocol/SOURCE_RECOVERY_CONTRACT.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/protocol/SOURCE_RECOVERY_CONTRACT.md)
- [RUN_MANIFEST.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/RUN_MANIFEST.json)
- [results/FINAL_VALIDATION.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_source_recovery01/results/FINAL_VALIDATION.json)
