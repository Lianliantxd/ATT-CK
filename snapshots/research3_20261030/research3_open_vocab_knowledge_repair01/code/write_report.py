from pathlib import Path
import json,csv
R=Path(__file__).resolve().parents[1]
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
x=json.loads((R/'results/REPAIR_COUNTS.json').read_text());m=json.loads((R/'RUN_MANIFEST.json').read_text());m.pop('query_or_raw_log_or_gold_payload_read',None);m['query_or_raw_log_or_gold_loaded_for_task_processing']=False;m['hash_only_transport_disclosure']='Preceding deliveryfileswere readasbytes forhashes;some containhistoricalGold/auditinformation. Noquery/rawlog/Goldrecords parsedfornewknowledgeconstruction;notaclaim ofzeroOSbyteaccess.'
save('RUN_MANIFEST.json',m)
contract='''# 新知识版本合同

版本：CAM_LDS_CANDIDATES_STIX16_1_PARENT_FIRST_V1_PARTIAL。
日期：2026-10-29（Asia/Shanghai）。

## 授权与用途

用户在明确提出“下一轮只执行知识修复阶段，不下载、不训练、不调用LLM”后要求继续。本轮仅从已有本地知识源创建独立新版本及差异文件。旧知识、Gold、历史预测和评价器保持不变。没有下载、服务器、GPU、模型调用或训练授权被推断或沿用。

## 候选空间及来源

保留作者matrix按ID首段父化得到的全部216个父候选，ID集合不删减。作者matrix commit为42bbd2cf8409f64a1e6c8fc936c91725e8c558b2，但其ATT&CK发布版本未编码，不能宣称与16.1同版。现有STIX bundle内部collection.x_mitre_version=16.1，文件hash与原有来源回执一致。没有从外部记忆补定义，没有读取查询/原始日志/Gold记录来构造新文本。

## 字段与渲染

1. 规范资产KNOWLEDGE_V1.json包含216项。每项将作者展示元数据与STIX来源父定义分开保存；行为正文只允许来自同external_id的有效父attack-pattern.description原字段。
2. parent_description逐字保留源字符串，包括原有换行、引用、HTML或Markdown；不补写、不摘要、不改必要条件。
3. 父技术渲染为source_parent_name + 一个换行 + parent_description；不附加战术标题，不把子类型正文拼进父正文。PARENT_ONLY_FULL.json没有预算截断。
4. 子技术按external_id排序单独存储。必须有有效subtechnique-of关系指向该父对象，记录源对象ID、索引、版本、hash及关系ID。其存在不意味着适用于某个Gold查询。
5. 13个缺少兼容父定义的候选保留ID，parent_description与渲染文本为null；不能填名称/战术或编造占位正文，不能把null转换成可评分知识，也不能静默排除这13类后仍称完整216候选。
6. 源父名称与作者父名称有差异时双列保留，不强制替换作者标签，不认证不同版本范围等价。
7. PARENT_FIRST_1000B_DIAGNOSTIC.json是显式预算诊断：encode(utf8)[:1000].decode(utf8,errors=ignore)。记录完整字节数、可见字节数和丢弃字节数；可能截在句子中间，不是完整行为条件，也不是已批准模型输入。
8. 所有实际模型Token数NOT_AVAILABLE；字节预算不等于Token预算。本轮不加载tokenizer或模型。

## 版本比较和评价资格

KNOWLEDGE_DIFF.csv逐216候选保存旧、新完整文本及hash、旧父正文位置、预算文本、原始首段来源和字段改变。候选ID未改变，模型可见语义内容与长度改变，因此旧预测不能移植为新知识版本结果。不得比较新旧不同信息预算后直接归因为算法收益。

SOURCE_PARENT_BODY_AVAILABLE只认证当前本地源字段存在、ID相符，并不认证作者标签范围、完整语义Gold或新旧版本等价。当前完整216合同BLOCKED。来源恢复后仍须完成发布版本对齐、范围人工裁定、正式模型输入预算及公平比较合同冻结，才能考虑重跑基线。

## 完整性边界

前一轮36个封存文件按字节核对，其中包括旧标签审计文件，但仅哈希，不解析作为新知识语义输入；不能声称OS字节层完全没有接触其中标签内容。43项实际输入均有首次本轮读取hash快照，结束复核；这不证明整个工作区所有文件未变化。未执行历史脚本。新脚本仅标准库读取知识和生成新项目文件。

机械通过不表示科学资格通过。新知识可用性为部分完成：203个父正文有直接源，13个缺失，2个作者/源父名称差异待版本范围核验。交付后停止，不自动下载、联系他人或开展新实验。
'''
(R/'protocol/KNOWLEDGE_VERSION_CONTRACT.md').write_text(contract)
needs='''# 最小来源恢复需求（未下载、未联系作者）

当前缺失13个父候选：T1667、T1668、T1669、T1671、T1672、T1673、T1674、T1675、T1677、T1678、T1679、T1680、T1681。此前只检查12个竞争定义时，后两种T1678/T1679未进入那个竞争集合；本轮216全量检查才扩大到13个来源缺口，不意味着前一轮379查询统计错误。

## 需要的最小材料

- 作者mitre_matrix.json的生成/导出说明及对应ATT&CK版本或上游commit。已有仓库commit与hash只能固定作者文件，不能自行证明其ATT&CK发布版本。
- 与作者候选空间兼容、可明确版本的父/子定义源。至少覆盖这13种技术，包含external_id、name、description、有效/废弃标记及父子关系；来源应可验证，保存版本/commit、获取回执与文件hash。
- T1176（作者Software Extensions；16.1源Browser Extensions）与T1219（作者Remote Access Tools；16.1源Remote Access Software）的版本范围对应说明。名称差异已由字段对照确认，但不能仅凭名称认定同义或映射错误。

当前未提供这些缺失源的真实本地文件路径，因此路径保持NOT_AVAILABLE。未通过网络确定具体下载版本或文件，不编造URL/hash/文件大小。之后若需下载，应先把固定版本、文件、预期大小/hash和目的地列成具体授权请求；本轮不执行。

## 材料到位后的最小处理顺序

先核验文件来源、版本及ID关系，再生成独立的新版本逐项差异；不能在现有16.1结构中无说明地拼入其它版本13条文本。可选择统一候选知识源版本，或制定有证据的跨版本映射合同，决定前不能把现版提升为全量可用。

完成来源对齐后，34条既有Gold范围疑问仍需独立人工裁定；补知识不自动修正标签，也不形成独立测试集。知识源与标签范围通过后，另外冻结公平输入和预算，再决定是否运行检索、GTE、B3及C4。当前不运行这些步骤。
'''
(R/'SOURCE_RECOVERY_REQUIREMENTS.md').write_text(needs)
required=['KNOWLEDGE_REPAIR_REPORT.md','knowledge/KNOWLEDGE_V1.json','knowledge/PARENT_ONLY_FULL.json','knowledge/PARENT_FIRST_1000B_DIAGNOSTIC.json','CANDIDATE_COVERAGE_AUDIT.csv','KNOWLEDGE_DIFF.csv','TEXT_BUDGET_AUDIT.csv','PARENT_CHILD_MAPPING.csv','MISSING_SOURCE_REQUIREMENTS.csv','SOURCE_RECOVERY_REQUIREMENTS.md','protocol/KNOWLEDGE_VERSION_CONTRACT.md','RUN_MANIFEST.json','results/FINAL_VALIDATION.json']
report='''# ATT&CK知识新版本与修复报告

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

'''
for n in required:report+='- ['+n+']('+str(R/n)+')\n'
(R/'KNOWLEDGE_REPAIR_REPORT.md').write_text(report)
m['required_artifact_paths']=required;save('RUN_MANIFEST.json',m)
print('Substantive report and contract written;required',len(required))
