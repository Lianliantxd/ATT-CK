---
type: results-report
date: 2026-10-29
experiment_line: open-vocab-distinguishable-evidence-audit
round: 1
purpose: evidence-and-error-qualification
status: limited_nonindependent_audit_reference_and_definition_blocked
source_artifacts:
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/reports/analysis-report.md
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/reports/stats-appendix.md
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/results/QUERY_AGGREGATE_COUNTS.json
linked_experiments:
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_failure_mechanism_diagnosis01
linked_results:
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/review/CASE_EVIDENCE_AUDIT.jsonl
---

# 384条Unseen漏召回：证据可辨识性与归因审计 / 2026-10-29

## 执行结论与边界

**384条的有限证据审计与竞争定义检查均已形成结果，完整独立语义裁定仍受阻。** 状态PARTIAL_WITH_REFERENCE_AND_DEFINITION_BLOCKERS。不能将其称为独立盲审、正式Gold或确认性算法错误集。唯一决策：**GO_AFTER_INPUT_OR_LABEL_AUDIT**。

本轮重新读了实际冻结文本和定义，未导入旧AI标签作为结论；但上下文此前已有暴露，仍为INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE。没有新增Agent或模型调用。第一遍封存、候选包装、第二遍封存、基线资格核验的次序与hash分别保留。

本轮确认了一个此前门控中没有逐候选展开的具体限制：**实际涉及的125种竞争技术中，12种缺少可用行为正文，影响379/384查询。** 11种只有名称/战术，另T1574的1000字符全为变体标题，未到行为正文。这是当前冻结文本的实际可用性问题，不是对完整ATT&CK标准的断言，更不能直接证明GTE漏召回的因果主因。

## 覆盖、来源和完成定义

冻结384唯一sample_id，输出384，缺失0、重复0；80逻辑步骤、145种输入文本、54个目标技术、520个查询—目标分配。全部查询保持原顺序，没有合并不同采样或多Gold。逐案比较含3840竞争候选实例、5200个Gold—候选配对尝试。可评价所提供命题的配对3208，其余1992明确保留不可评价/输入不足，不能声称5200个都获得了充分语义结论。

实际阅读54份冻结Gold原文，80步骤内全部737条去重显示行及每个查询的位置映射；这些涵盖2178显示行实例。之后检查125种竞争定义，34种与此前本轮读过的Gold相同、91种新增；查看全部步骤和采样的候选集合映射。阅读辅助表不是合并评价，当前引用严格与本查询求交。其全过程仍共用AI上下文，不是384次独立裁定。

Fact ID沿用源的VISIBLE_LINE定位符，是派生显示行ID，不是独立认证的原生事件。NATIVE_LOG_RECORD仅标冻结副本中的原生日志格式，不证明原始文件真实性；IDS/Wazuh签名是DERIVED_PATTERN，自动化轨迹另列。主体账号、进程、路径、端点及时间仅按可见字段绑定，不把root当攻击者，不把相邻时间当因果；原始完整日志和省略数未知，不自动确认截断或预处理错误。

第一遍有一次候选访问前的措辞修正：将步骤内多视图阅读笔记与单视图直接支持命题分开。v1和历史hash保存，未改字面定义或手写判断，也没有在看竞争候选后回改Gold侧结论。最终以FIRST_PASS_SEAL为准。

## 查询主要诊断（互斥，分母384）

| 主要诊断 | 查询数 |
|---|---:|
| 证据存在且可区分 | 0 |
| 证据相关但有歧义 | 65 |
| 当前可见证据不足 | 256 |
| 目标范围/粒度未解 | 34 |
| 输入或源映射未解 | 0 |
| 仍无法可靠归因 | 29 |

A类0表示本轮没有查询获得完整选定候选子集的区分支持，不表示真实可区分查询数已知为0。E类0也不证明源映射完美，只是没有足够核验依据将某个已完成查询归为该主要问题。F类29不是未审查占位：这些查询有可见必要行为核心，但候选定义或区分资格不能闭合，具体配对原因已保存。未读取的基线逐例结果另行记未执行，不藏在F类中。

目标范围疑问优先保留D；没有必要核心行为的背景/准备或代码缺失归C；有部分相关机制而不能判别归B。所有分类是非独立AI审计，不是真实攻击根因分布；256不能解释为原日志没证据或256个模型错误由预处理造成。

## 十个科研问题的实际答案

1. **可追溯相关行为证据**：96/384查询有直接或部分机制线索的本轮AI判断；不是96个已确认攻击，也不是96个正确预测。
2. **足以支持Gold必要条件**：31/384在本轮明示的“可见必要行为合同”上得到支持，覆盖账户创建、硬件/时间/窗口查询尝试、PTR标识查询、服务停止及配置管理任务执行等。完整Gold语义适用性、攻击者归属和意图的合格参考结论仍**NOT_AVAILABLE**；不能把31当正式充分Gold。
3. **区分Gold与主要竞争技术**：对可评价的已提供命题，有193个配对相对支持Gold，分母为5200配对；没有查询完成整组10候选的充分区分支持。合格独立区分查询数**NOT_AVAILABLE**，不以0代替。193不是193条查询或193个算法错误。
4. **仅宽泛行为描述**：73/384属于“至少有BROAD/PREPARATORY背景，但没有任何直接/部分Gold机制”的操作性AI分类；另65条主要类别为相关但歧义。两者口径不同，不能混成一类准确率。
5. **Gold范围/粒度疑问**：34/384至少一个目标有具体疑问，不是34个已证实错标。完整父技术与子类型的合同仍需核验。
6. **可验证历史排序错误**：本轮取得合格独立人工裁定0；可验证残余错误真实数量**NOT_AVAILABLE**。不能用AI核心支持或193有利配对补齐资格。
7. **已被强基线正确排序的数量**：**NOT_AVAILABLE**。没有满足整组区分及参考门槛的查询，本轮未扩大读取其逐例C4/词法输出；不把未比较解释为无命中。
8. **跨协议无法公平比较**：384/384相对历史native全216 BM25/字符检索存在知识或查询合同差异；属于可核验的比较资格限制，不是384个模型错误的因果解释。
9. **需要独立人工裁定**：384/384。人审队列全量保留，没有联系审查者或把AI重复运行当人审。
10. **是否支持启动方法实验**：不支持。本轮仅完成有限审计、资格统计及决策，没有训练、模型推理或新算法结果。

## 可观察动作、定义解释和竞争判断必须分开

REV_0020/0021的useradd new user及属性是创建状态的直接相关记录；REV_0022等的lspci、REV_0033的date、REV_0256至0259的wmctrl-l是明确请求，不能补出未显示的输出。REV_0173至0175明确Stopped/Deactivated exim4；REV_0181至0185与REV_0201至0205记录Puppet catalog Exec success，但未认证脚本内容和操作者目的。

command-v lsusb只是工具存在性检查；xclip-output请求不证明采集成功；encrypt参数和jpg改名后缀不认证密文或不可用；Firefox存储维护不认证输入/剪贴板捕获；浏览器自动输入密码不等于捕获密码。单一execve失败或connect -115不能反驳整个技术。

Gold范围例子：本地rm与T1485云生命周期正文；本地Puppet CA路径与T1213信息仓库正文；Shorewall ACL改变与T1599 NAT正文；Linux管道与T1218 Rundll32主体正文。这里是冻结父类参考范围不完整的具体问题，不用某一变体条件否定整个父技术，也不临时扩大定义来迎合Gold。

第二遍候选打乱只减少原排序提示，不能消除模型选候选偏差。程序按实际保存shuffle序列序列化比较；AI也查看中性ID定义目录和覆盖索引，因此不声称独立认知顺序始终随机。每例只看Gold+10候选，实际11至17种，未审199至205种；all_216_reviewed全部false。全局读过145种不同目标/竞争定义也不等于每例审完145或216候选。

候选缺正文清单：T1681, T1673, T1680, T1672, T1669, T1574, T1675, T1677, T1667, T1668, T1674, T1671。不得从技术名称、外部记忆或另一个版本填充当前冻结必要条件。379条具有至少一个此类候选；其余5条不意味着已获独立Gold或足够日志证据。

## 条件级与技术级汇总

本轮Gold条件2555实例：DIRECTLY_SUPPORTED240、PARTIALLY_SUPPORTED201、EXPLICITLY_CONTRADICTED0、NOT_ESTABLISHED1990、NOT_OBSERVABLE_IN_CURRENT_VIEW12、NOT_EVALUABLE112。其中必要可见行为条件1905，直接110、部分201、未建立1470、不可观测12、不可评价112；其余650为归属/背景条件，不能都当Gold必要条件。去重逻辑条件263，按技术ID+条件类型+文字计算，不是独立事件。旧2618属于旧条件模式，本轮不为凑相同数量导入旧标签或删查询。

54个Gold技术的逐技术查询、相关机制、核心合同、范围/输入限制、人审及资格均完整存CSV；同查询有多个Gold不能跨技术行相加当独立查询。193个Gold有利配对、57个共同相容、2958个均不足、1964个不可评价、28个输入不足均为AI命题级比较；不计算正式语义Precision/Recall/F1或显著性。没有科学推断图，只有实际计数表与审计数据。

## 历史结果有限对照：资格不是新评价

证据第二遍封存后，核验历史基线文件、版本和文本合同。当前Gold与候选选择满足冻结GTE miss属性，但作者标签不因此成为正确参考。没有完整区分且获合格独立参考的查询，故384行残余审计主类均REFERENCE_INSUFFICIENT，逐例C4/词法结果比较完成量0，不能冒充性能数值0。

历史native全216词法与GTE候选ID一致，但整体知识文本不同（216中仅41份逐字相同）；每条比较都存在知识协议差异，样本当前文本逐字相同仅0/384。对照文件已存在并hash，不代表本轮查看或重新评价其全部预测。CROSS_PROTOCOL_NOT_COMPARABLE为384条的次级资格标记，和REFERENCE_INSUFFICIENT可以同时成立。不能据此说强基线没有恢复任何Gold，也不能把既有32例C4损失重新当本轮发现。

## 唯一科研决策与下一步最低材料

**GO_AFTER_INPUT_OR_LABEL_AUDIT**。

本轮有可追溯行为线索，不能说没有研究候选；但在独立参考之前，必须先核查已经实际发现的冻结知识可用性及父子范围合同：12种竞争条目没有行为正文、379查询整组比较受影响，34查询的目标定义范围有疑问。这个顺序是门控优先级，不是已识别主要失败原因，更不表示补定义必有模型收益。参考资格仍为随后必须满足的硬门槛。

最低材料：固定候选/知识版本与生成来源；对12种条目核查原冻结文档是否本就无正文或标题截断，区分知识覆盖与渲染/裁剪问题；对父/子技术适用范围及作者标签保留独立审计依据；给实际相关/核心行为查询做预测隔离的真人双审和仲裁，确认主体—动作—对象—结果及合理竞争解释。不得在本轮回写历史定义/标签或读取未授权原日志；若需要新知识版本或额外字段，应另行冻结并授权，不用新版本修补本轮成绩。

只有未来具备合格语义参考和明确可区分失败，才重新判断是否值得设计方法实验。当前384始终是按GTE漏召回筛选且已曝光的开发集，不会因人审、重命名或新目录变成独立测试。

## 资源、完整性及停止

新增模型/API/Agent/Embedding/CE调用0，训练0，下载0，GPU0，网络0，服务器0。当前助手的语义阅读属于AI预审，不冒充“未使用AI”；内部Token/CPU峰值未独立计量。只用已有Python标准库与静态解析，没有执行日志中的命令。

实际核验353个旧资产，保留1项此前已披露的旧融合报告hash差异，不修复旧文件。核心输入在第一遍前锁定，其他旧资产广域hash清单在第二遍后建立，不能冒充全任务开始前OS快照；末次验证将对当前快照、核心早期hash和两次封存逐项核对。写操作只针对本轮新目录。

完成交付、机械核验与hash封存后停止；机械通过只证明文件、引用和合同记录一致，不认证语义结论。没有通过新的AI判断填补独立参考，没有启动下一轮模型实验。

## 实际交付文件（绝对路径）

- [DISTINGUISHABLE_EVIDENCE_AUDIT_REPORT.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/DISTINGUISHABLE_EVIDENCE_AUDIT_REPORT.md)
- [inputs/FROZEN_CASE_MANIFEST.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/inputs/FROZEN_CASE_MANIFEST.json)
- [review/CASE_EVIDENCE_AUDIT.jsonl](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/review/CASE_EVIDENCE_AUDIT.jsonl)
- [review/CONDITION_EVIDENCE_MATRIX.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/review/CONDITION_EVIDENCE_MATRIX.csv)
- [review/COMPETING_TECHNIQUE_AUDIT.jsonl](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/review/COMPETING_TECHNIQUE_AUDIT.jsonl)
- [review/CASE_DIAGNOSIS.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/review/CASE_DIAGNOSIS.csv)
- [review/CASE_EVALUATION_ELIGIBILITY.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/review/CASE_EVALUATION_ELIGIBILITY.csv)
- [review/BASELINE_RESIDUAL_ERROR_AUDIT.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/review/BASELINE_RESIDUAL_ERROR_AUDIT.csv)
- [results/QUERY_SUMMARY.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/results/QUERY_SUMMARY.csv)
- [results/GOLD_TECHNIQUE_SUMMARY.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/results/GOLD_TECHNIQUE_SUMMARY.csv)
- [results/CONDITION_SUMMARY.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/results/CONDITION_SUMMARY.csv)
- [protocol/REVIEW_PROTOCOL.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/protocol/REVIEW_PROTOCOL.md)
- [protocol/BLOCKER_REGISTER.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/protocol/BLOCKER_REGISTER.json)
- [protocol/BLINDING_INTEGRITY_REPORT.md](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/protocol/BLINDING_INTEGRITY_REPORT.md)
- [protocol/HUMAN_REVIEW_QUEUE.csv](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/protocol/HUMAN_REVIEW_QUEUE.csv)
- [RUN_MANIFEST.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/RUN_MANIFEST.json)
- [results/FINAL_VALIDATION.json](/Users/tianxd/Documents/mid-term/research3_open_vocab_distinguishable_evidence_audit01/results/FINAL_VALIDATION.json)
