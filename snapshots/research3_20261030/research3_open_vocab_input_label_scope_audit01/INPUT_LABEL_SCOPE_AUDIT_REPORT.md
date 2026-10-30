# 输入与标签范围来源审计报告

任务：R3_OPEN_VOCAB_INPUT_LABEL_SCOPE_AUDIT01；日期：2026-10-29（Asia/Shanghai）。

## A. 执行状态

**PARTIAL_WITH_REFERENCE_AND_DEFINITION_BLOCKERS**。完成12/12冻结竞争定义、本地可用来源与21个相关ID的有限转换核验、34/34范围疑问查询及其51个原始作者标签运输链、379/379受影响查询的ID重建。没有重做384条语义审查，没有修复知识、标签或新模型实验。

查明两个可直接核验的局部原因：T1574行为正文被1000UTF8字节前缀完全排除；其余11种在本地16.1描述源不存在匹配父/子对象，候选来自另一个作者matrix，故最终只保留名称和战术。精确作者matrix的ATT&CK发布版本与上游生成来源尚未恢复，11种兼容行为文本仍缺失；独立人审及语义Gold未建立。机械完整性通过不能解除这些科研阻断。

## B. 12个竞争技术定义的核验结果

来源是作者仓库matrix（commit42bbd2cf8409f64a1e6c8fc936c91725e8c558b2）与现有STIX bundle（collection明确x_mitre_version=16.1），不是仅凭文件名认定官方来源。matrix691个原始ID归并为216父候选，只含name/tactics，没有description。STIX已有22905个对象；目标对象按external_references.external_id实际检索，未以ID大小推断含义或年代。

|ID|完整冻结文本字符/字节|当前链内确认原因|证据|受影响查询|兼容正文可恢复性|
|---|---:|---|---|---:|---|
|T1681|40/40|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|103|需恢复兼容且有版本的源文本|
|T1673|35/35|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|168|需恢复兼容且有版本的源文本|
|T1680|33/33|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|105|需恢复兼容且有版本的源文本|
|T1672|30/30|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|70|需恢复兼容且有版本的源文本|
|T1669|29/29|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|17|需恢复兼容且有版本的源文本|
|T1574|1000/1000|TEXT_TRUNCATION_CONFIRMED|L2|130|现有完整K2/STIX可用于新版本方案|
|T1675|37/37|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|310|需恢复兼容且有版本的源文本|
|T1677|37/37|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|228|需恢复兼容且有版本的源文本|
|T1667|20/20|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|10|需恢复兼容且有版本的源文本|
|T1668|29/29|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|15|需恢复兼容且有版本的源文本|
|T1674|25/25|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|5|需恢复兼容且有版本的源文本|
|T1671|41/41|DESCRIPTION_NOT_IN_CURRENT_SOURCE|L1当前源缺口|10|需恢复兼容且有版本的源文本|

逐项原文、hash、名称/战术、父/子ID、来源路径、脚本及修复资格见TECHNIQUE_DEFINITION_AUDIT.csv；原始字段对象与位置见audit/SELECTED_SOURCE_FIELD_EVIDENCE.json。12种当前均不具备所需行为比较资格。

### T1574的直接核验与措辞更正

冻结文本是1000字符、1000UTF8字节；它与保存完整K2的前1000字节完全相同，也恰好等于matrix为该父ID拼接的名称/战术前缀。完整K2为26335字节（26327字符），第一个描述正文从第1048字符开始，父技术自身正文从第19641字符开始（均零基字符偏移）。保存代码明确DOC_CAP=1000且clip=text.encode()[:cap].decode(utf8,errors=ignore)，有限纯表达式可复现同一输出。

**并非全部都是子技术标题**：其中还包括父技术Hijack Execution Flow标题；准确说法是“全部为父/子名称与战术，没有行为正文”。未发现标题字段与description字段交换的证据。原始STIX有14个有效父/子对象及各自描述，matrix有13个相关ID；父化拼接顺序及前缀预算造成完整行为排除。这里确认的是局部转换缺陷/合同后果，不能认定错误ID或序列化损坏。

### 其余11种的确认范围

对每个ID都实际检索了整个本地STIX中父/子对象，包括被撤销/废弃对象检查；均无对应ID。matrix的对应条目只有名称和战术；完整K2与短冻结文本相等，故这11种没有因1000字节规则进一步丢失已有正文。它们的当前链内原因是DESCRIPTION_NOT_IN_CURRENT_SOURCE，不能写成EXTRACTION_OMISSION或TEXT_TRUNCATION_CONFIRMED。

已确认作者候选集合与16.1描述源存在ID覆盖差异；matrix确切ATT&CK发布版本未编码，所以精确发布版本冲突数量仍NOT_AVAILABLE。不能声称官方定义不存在，也不能从名称补正文。为何没有提供兼容描述源、matrix如何产生仍未查明。

## C. 34条Gold范围疑问的核验结果

从CASE_EVIDENCE_AUDIT的SCOPE分配重建34个sample_id，与CASE_DIAGNOSIS的范围主类集合完全一致，涉及8个逻辑步骤。旧汇总要求的review/GOLD_TECHNIQUE_SUMMARY.csv并不存在；实际位于results/GOLD_TECHNIQUE_SUMMARY.csv，已登记两处路径和替代关系。

|被标范围疑问的目标父ID|查询数|来源链确认的输入事实|标签判断|
|---|---:|---|---|
|T1218|12|前缀行为段来自T1218.011；父正文偏移5960，在预算外|不能据此认定作者父标签错|
|T1569|5|前缀行为段来自T1569.001；父正文偏移1095，在预算外|服务行为与当前日志关系需独立裁定|
|T1485|5|前缀行为段来自T1485.001；父正文偏移1181，在预算外|删除调用不自动证明破坏性语义/结果|
|T1213|7|先展开T1213.002等；父正文偏移4157，在预算外|本地路径与信息仓库标签的范围需裁定|
|T1599|5|前缀行为段来自T1599.001；父正文偏移1877，在预算外|边界策略与具体子类型适用性需裁定|

34查询包含51项作者父标签，46项是此前目标UnseenGold，34项被旧AI标为SCOPE；三者不能互换。所有51项均找到作者metadata键、原始ID、保存raw_ground_truth、显式父化规则、冻结候选ID及对应文本，并逐项保留。查询有多个Gold时未合并为一项判断；未被标SCOPE的共存标签仅核查机械映射，不新增语义结论。

**在这51条已检查运输链中发现的机械ID映射错误为0**：作者metadata键与raw_reference相等，父ID与明确split('.')规则相等，候选ID存在。这个零有明确检查范围，不意味着Gold正确。34项SCOPE的父正文未进入冻结前缀已得到转换证据支持，但这是定义覆盖问题，不能直接叫作34个父子ID映射错误。作者标签真实适用范围、意图及当前视图证据充分性仍NOT_AVAILABLE，34条均进入独立人工队列。

GOLD_SCOPE_AUDIT.csv逐行列出原始标签、来源、支持/限制、机械映射与未裁定状态；PARENT_CHILD_MAPPING_AUDIT.csv给出完整ID链、STIX关系字段和来源指针；HUMAN_ADJUDICATION_QUEUE.csv仅列34项实际SCOPE目标，不伪造审查者或裁定。

## D. 提取与转换链审计

检查了以下实际链条，脚本只静态阅读，无旧模块导入或执行：

1. author labels.metadata → benchmark/run_benchmark.py标签选择 →保存原标签；evaluate_techniques.py验证ID并父化。
2. author mitre_matrix name+tactics → benchmark/run_benchmark.py按原顺序聚合到216父候选。
3. STIX16.1有效attack-pattern外部ID →同一脚本按父ID追加name+description，遵循STIX对象顺序，不优先父正文。
4. extended_knowledge_documents →P0冻结副本→baseline K2；保存JSON内容相等。
5. mechanism_ir/build_inputs.py对K2调用UTF8前缀1000字节，写KNOWLEDGE_TEXTS。
6. domain data/prepare_grouped_data.py只读复制K2及父化标签，原标签保存在P0_REFERENCE.raw_ground_truth。
7. 上轮prepare_competitors/prepare_first_pass复制冻结文本与ID，候选文本按domain K2作相等断言。

对12个竞争ID及34查询涉及的9种作者父ID，共21种相关ID核验保存输入输出。纯字符串拼接与UTF8切片的结果全部与保存文档一致，记录在audit/BOUNDED_TRANSFORMATION_PROOF.json。未重新生成/替换216候选知识，未执行大数据提取。

该证据能确认本地转换如何形成冻结文本；不能恢复matrix上游官方导出、版本历史或作者原标签意图。文档顺序导致首先看到某个子类型不代表该子类型应覆盖全部父类。没有证据证明代码读取错字段、ID覆盖、编码损坏或最终渲染额外丢失；这些“未发现”限于实际检查链。

## E. 379条受影响查询的影响范围

从封存候选ID逐一连接12个缺陷技术与当前定义，重建379/379条，未确认0条；去重后仍为379条，涉及79个逻辑步骤。

|统计单位与集合|数量|
|---|---:|
|去重受影响查询sample_id|379|
|缺陷竞争技术实例(sample_id,competitor)|1171|
|受影响旧目标UnseenGold分配(sample_id,gold)|515|
|缺陷竞争配对(sample_id,gold,competitor)|1700|
|受两个及以上定义缺陷影响的查询|327|
|与34条Gold范围疑问的交集|34|
|与256条旧“当前视图不足”主诊断的交集|251|
|上述三组的三重交集|0|

三重交集0来自旧主诊断的互斥分类，不说明范围疑问查询没有观察不足。受1/2/3/4/5/6个缺陷影响的查询分别为52/60/128/87/45/7，合计379。各技术影响非互斥，不能直接相加当查询数。515不是全部作者Gold分配；1700也不是5200全部配对，更不是错误数量。具体键集合及交集在audit/IMPACT_ID_SETS.json，逐查询连接在AFFECTED_QUERY_MAP.csv，各技术非互斥影响在DEFINITION_IMPACT_SUMMARY.csv。

379条均有直接“比较输入包含缺陷定义”的证据，所以影响资格为CONFIRMED_DIRECT_IMPACT_ON_COMPARISON_INPUT；379条实际模型错误原因仍未知。本轮没有性能因果实验，不能把任何数填成因缺陷造成的已确认排序错误数。

## F. 已确认的事实与未解决的问题

已确认：12份冻结比较文本无可用行为正文；T1574发生有代码与输入输出证明的正文排除；11种匹配行为对象不在当前STIX源；34条疑问目标父正文均不在冻结前缀；51项检查ID运输链符合当前父化规则；379查询及其影响键可以复现。

未解决：matrix原始生成来源和确切ATT&CK发布版本；11种兼容描述文本的恢复；父/子范围应该如何成为本任务的评价合同；作者父标签与当前日志证据的适用关系；独立人工参考与测试；任何历史性能错误的原因。

没有把语义不一致判成机械映射错，没有把缺失证据当反证，也没有通过读取额外日志或更改定义消除疑问。此前AI说明仍是历史线索，未升级为Gold。

## G. 可修复性与最小材料需求

T1574完整正文已在现有合法资产中，可制定新版本的父/子分段与信息预算方案；本轮只登记REPAIRABLE_FROM_EXISTING_FROZEN_ASSETS，不实施。五种范围疑问的父文本也存在，但标签适用性需要REQUIRES_HUMAN_ADJUDICATION，不能仅靠补文本裁定。

其余11种需要兼容版本的父/子原始描述、版本与hash回执、与作者候选matrix的对齐合同。现有材料没有给出这些缺失文件的真实路径，因此明确记录“兼容源文件未提供，路径NOT_AVAILABLE”，不编造路径。最小上游材料还包括作者matrix生成/导出规则与release信息、标签意图说明；独立参考需未曝光审查者、逐条件证据、分歧及仲裁记录。

未来如获准修复，必须创建独立新版本，保留旧知识和Gold，保存全候选新旧差异、父子映射差异、字段增删及输入hash，重核受影响案例并标明历史结果不可直接比较。不存在“技术可修复即已授权修改”的推断。

## H. 唯一科研决策

**GO_AFTER_SOURCE_RECOVERY**。

T1574局部转换原因已明确且现有源可用于修复计划；但其余11种缺少兼容行为来源，作者matrix的确切发布/生成链未恢复。全候选比较合同仍无法补齐，所以按来源链优先规则，主决策是先恢复最小来源。34条标签范围独立裁定和语义参考是后续仍不可跳过的阻断。该主决策不授权下载、修复旧知识、修改标签或重跑模型，也不是NO_GO问题已经永久不可研究。

## I. 统计与方法限制

本轮是对已曝光、按旧排序筛选的开发案例作来源和ID审计；不是新的独立样本。查询、逻辑步骤、Gold分配、候选实例和配对分开计数，不做准确率、显著性、置信区间或算法收益推断。未检查全部216候选的语义适用性，也未建立完整攻击意图真值。源文本恢复仅改变输入合同，不会自动证明GTE、C4、Seen/Unseen收益。

字段未知时保持null/NOT_AVAILABLE。confirmed_source_version_mismatches无法给精确发布差异数；另报11个当前源ID覆盖缺口。confirmed_mapping_errors=0仅限51个已实际检查的机械运输链；unresolved_mapping_cases=34表示范围适用性仍待人工裁定。unresolved_definition_causes=11只指上游兼容源缺失与版本由来的解释未恢复，不否定其在本地16.1不存在对象这一已确认直接原因。

## J. 资源、资产完整性和停止状态

新增模型、Agent、训练、GPU、网络、服务器、下载、上传及旧文件修改均为0；只运行本地标准库静态审计和去重程序。没有执行历史参数网格或改动标签、评价器及checkpoint。机械验证细节见results/FINAL_VALIDATION.json；历史资产结束hash核验范围以登记清单为准。

初步发现/schema读取先于部分资产首次跟踪快照，因此不声称全工作区有任务开始前快照。已保留旧generalization结果报告原有hash差异，不修复、不宣称所有历史manifest无差异。作者labels.json为混合容器，解析时存在非metadata字段读取和早期schema展示，已在协议披露；未执行命令或用它补日志事实，没有工具字节级隔离。没有读取原始llm_queries或受限日志正文。

最终机械状态为PASS_MECHANICAL_AUDIT_WITH_DOCUMENTED_BLOCKERS；科研执行状态仍为PARTIAL_WITH_REFERENCE_AND_DEFINITION_BLOCKERS。完成交付封存后停止，不自动启动下一轮。

## K. 交付导航

- [INPUT_LABEL_SCOPE_AUDIT_REPORT.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/INPUT_LABEL_SCOPE_AUDIT_REPORT.md)
- [ASSET_SOURCE_INVENTORY.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/ASSET_SOURCE_INVENTORY.csv)
- [TECHNIQUE_DEFINITION_AUDIT.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/TECHNIQUE_DEFINITION_AUDIT.csv)
- [GOLD_SCOPE_AUDIT.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/GOLD_SCOPE_AUDIT.csv)
- [EXTRACTION_PIPELINE_AUDIT.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/EXTRACTION_PIPELINE_AUDIT.csv)
- [PARENT_CHILD_MAPPING_AUDIT.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/PARENT_CHILD_MAPPING_AUDIT.csv)
- [AFFECTED_QUERY_MAP.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/AFFECTED_QUERY_MAP.csv)
- [DEFINITION_IMPACT_SUMMARY.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/DEFINITION_IMPACT_SUMMARY.csv)
- [REPAIRABILITY_REGISTER.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/REPAIRABILITY_REGISTER.csv)
- [HUMAN_ADJUDICATION_QUEUE.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/HUMAN_ADJUDICATION_QUEUE.csv)
- [protocol/INPUT_LABEL_AUDIT_PROTOCOL.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/protocol/INPUT_LABEL_AUDIT_PROTOCOL.md)
- [protocol/BLOCKER_REGISTER.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/protocol/BLOCKER_REGISTER.json)
- [protocol/SCOPE_AND_PROVENANCE_LIMITATIONS.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/protocol/SCOPE_AND_PROVENANCE_LIMITATIONS.md)
- [RUN_MANIFEST.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/RUN_MANIFEST.json)
- [results/FINAL_VALIDATION.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_input_label_scope_audit01/results/FINAL_VALIDATION.json)

附加证据：audit/BOUNDED_TRANSFORMATION_PROOF.json、audit/SELECTED_SOURCE_FIELD_EVIDENCE.json、audit/SELECTED_AUTHOR_LABEL_METADATA.json、audit/IMPACT_ID_SETS.json、audit/SOURCE_HASH_COMPARISONS.json、audit/DELIVERY_SHA256.json。全部位于本轮目录。
