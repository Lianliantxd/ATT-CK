# ATT&CK知识新版本与修复报告

2026-10-29（Asia/Shanghai）；本轮：R3_OPEN_VOCAB_KNOWLEDGE_REPAIR01。

## 结论与实际状态

**PARTIAL_KNOWLEDGE_VERSION_WITH_SOURCE_BLOCKERS**。实际构建独立新版本，保留216候选ID，恢复203种父技术的完整现有源正文，并把453种子技术正文单独存储，453条父子关联均有本地STIX关系记录。13种候选仍无兼容行为来源，明确保留null，不编造定义或静默缩小候选空间。

唯一主决策仍为 **GO_AFTER_SOURCE_RECOVERY**。这是一份可复核的部分知识版本，不能称为216类知识已修复完毕，也不能直接投入新的模型比较。没有训练、推理或性能结果。

## 本轮做了什么

1. 核验上一轮36个封存交付文件hash全部一致。
2. 读取固定作者matrix、现有STIX16.1以及保存的完整/短K2文本；未导入或执行历史提取脚本。
3. 对216父候选逐项检查有效父对象、非空description、父/子原始ID与关系；核验STIX内部collection版本及既有文件hash。
4. 创建父正文与子类型说明分离的新资产；为全部216项保存旧/新文本、hash、字节、来源与改变类型。
5. 单独生成1000字节预算诊断视图，完整文本永久保留；明确记录丢失字节，实际模型Token未知。
6. 登记缺失来源与两项名称/版本范围差异；未修改任何旧标签、知识或预测。

## 实际数量及意义

|项目|数量|解释|
|---|---:|---|
|保留的父候选ID|216|与原候选集合完全相同|
|有直接本地父正文源|203|只认证字段可追溯，不认证作者标签语义正确|
|缺少兼容父正文源|13|候选保留，正文null，未修复|
|独立存储的有效子技术正文|453|未混入父技术正文|
|经STIX关系确认的父子关联|453|不是从名字推断父子关系|
|旧文本中父正文开头完全不可见|73|分母203个有父正文源的候选|
|旧文本未完整保留父正文|164|包含上述73项，不应相加|
|新完整父文本被截断|0|新完整视图无长度裁剪|
|新1000字节诊断视图仍被截断|129|说明仅重排正文顺序不足以解决预算问题|
|作者父名称与16.1源父名称不同|2|差异事实，不自动认定语义映射错误|

旧文本中39项完整保留父正文；新1000字节诊断视图有74项能完整保留渲染的父定义，但不能因此声称这些项已获得独立语义评价资格。所有数字为216知识候选的字段/字符串统计，不是查询准确率或模型收益。

## T1574已经怎样处理

源父名称为Hijack Execution Flow，源父description为801字符；新版本直接逐字保留该父正文，并把13种子技术分开保存。旧版1000字节恰好全为名称与战术的文本仍然保留在KNOWLEDGE_DIFF中，旧文件未动。修复只说明行为正文现在进入新父定义，不说明任何模型会因此排对。

## 为什么是13种缺失，而不是上一轮11种

缺失ID为：T1667、T1668、T1669、T1671、T1672、T1673、T1674、T1675、T1677、T1678、T1679、T1680、T1681。

上一轮只对125种竞争技术中12种不完整条目追根，其中T1574可从已有源恢复，其余11种无匹配对象。本轮检查全部216候选，额外发现T1678、T1679也没有匹配源。检查集合扩大导致来源缺口统计增加；本轮未重算379条查询或旧预测因果影响，不能将13种与旧379查询直接建立新关系。

## 父名称与来源版本差异

- T1176：作者matrix为Software Extensions，STIX16.1为Browser Extensions。
- T1219：作者matrix为Remote Access Tools，STIX16.1为Remote Access Software。

新资产双列保留，不修改作者标签，也不自动认定名称等价或作者出错。作者矩阵固定到仓库commit42bbd2cf8409f64a1e6c8fc936c91725e8c558b2，但确切ATT&CK发布版本未编码；不能宣称新16.1正文与作者候选范围全部同版。原始关系链和版本合同仍需补齐。

## 新版数据合同与使用限制

规范资产包含作者元数据、独立父正文、来源对象与hash、单独子类型说明和资格状态。完整父文本渲染只含源父名称+换行+源父description。缺失项保留null，模型程序不得把null当字符串、名称替代正文、静默删候选或将13项算成负例。

1000字节文件明确为DIAGNOSTIC，不是获准的模型输入。其129项仍裁剪，裁剪可能发生在句中，不认证保留完整机制条件。实际Token数NOT_AVAILABLE，未调用tokenizer。

与旧版相比，知识内容和长度发生改变，因此旧预测不能复用为新结果；将来应在同一新版输入、知识、候选和预算下运行强对照，不能把知识恢复收益归到新算法。203项来源字段可用也不等于独立Gold、完整标签范围正确或测试未曝光。

## 最小剩余阻断与下一步

先恢复作者matrix对应发布/生成来源及13项兼容父/子正文。可以统一到一个经核验的来源版本，或建立有依据的跨版本合同；本轮不擅自选择新版下载。两项名称差异需要范围对照，34条既有范围疑问仍需要独立人工裁定。之后再冻结实际模型输入预算和公平基线协议。

SOURCE_RECOVERY_REQUIREMENTS.md列出最小材料与授权条件。当前无法仅凭现有资产完成216类知识修复，所以停止在部分版本，不训练、不调用模型、不扩大原始日志读取。

## 资源与完整性

新增模型/Agent调用、训练、GPU、下载、网络、服务器、上传与旧文件修改均为0。43个实际读取的既有输入已建立本轮首次读取hash快照并在结束复核；不声称整个工作区所有文件未变。上一轮封存文件仅作hash读取，可能包含历史标签审计字段，本轮未解析作为新知识语义输入；不是OS字节级从未接触标签的声明。旧报告已知hash差异仍由上一轮保留，没有修复或覆盖。

机械验证只认证字段、字符串、ID、来源和文件完整性，科研状态仍部分完成。没有新预测、性能指标、因果结论或人工Gold。交付封存后停止。

## 交付导航

- [KNOWLEDGE_REPAIR_REPORT.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/KNOWLEDGE_REPAIR_REPORT.md)
- [knowledge/KNOWLEDGE_V1.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/knowledge/KNOWLEDGE_V1.json)
- [knowledge/PARENT_ONLY_FULL.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/knowledge/PARENT_ONLY_FULL.json)
- [knowledge/PARENT_FIRST_1000B_DIAGNOSTIC.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/knowledge/PARENT_FIRST_1000B_DIAGNOSTIC.json)
- [CANDIDATE_COVERAGE_AUDIT.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/CANDIDATE_COVERAGE_AUDIT.csv)
- [KNOWLEDGE_DIFF.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/KNOWLEDGE_DIFF.csv)
- [TEXT_BUDGET_AUDIT.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/TEXT_BUDGET_AUDIT.csv)
- [PARENT_CHILD_MAPPING.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/PARENT_CHILD_MAPPING.csv)
- [MISSING_SOURCE_REQUIREMENTS.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/MISSING_SOURCE_REQUIREMENTS.csv)
- [SOURCE_RECOVERY_REQUIREMENTS.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/SOURCE_RECOVERY_REQUIREMENTS.md)
- [protocol/KNOWLEDGE_VERSION_CONTRACT.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/protocol/KNOWLEDGE_VERSION_CONTRACT.md)
- [RUN_MANIFEST.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/RUN_MANIFEST.json)
- [results/FINAL_VALIDATION.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_knowledge_repair01/results/FINAL_VALIDATION.json)
