---
type: results-report
date: 2026-10-28
experiment_line: open-vocab
round: 3
purpose: 384-case-evidence-review
status: partial_with_documented_blockers
source_artifacts:
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_384_case_blind_review01/reports/analysis-report.md
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_384_case_blind_review01/reports/stats-appendix.md
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_384_case_blind_review01/results/REVIEW_COUNTS.json
linked_experiments:
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_failure_mechanism_diagnosis01
linked_results:
  - /Users/tianxd/Documents/mid-term/research3_open_vocab_384_case_blind_review01/review/QUERY_EVIDENCE_REVIEWS.jsonl
---

# Open Vocabulary / Round 3 / 384-case Evidence Review / 2026-10-28

## A. 执行状态与决策背景

**PARTIAL_REVIEW_WITH_DOCUMENTED_BLOCKERS**。384条查询的Gold侧有限AI预审全部形成记录；完整独立盲审及Top10竞争比较没有完成。所有记录标记AI_BLIND_PRE_REVIEW_NOT_GOLD，并明确PREDICTION_BLINDING_NOT_ENFORCED。

本轮要检验的是“漏召回记录里是否有可评价的目标技术证据”，不能把漏召回直接视为语义表示失败。结论是需要先独立核验证据资格与标签范围，目前不能确定Seen/Unseen难以兼顾的主要因果机制。最终流程优先级为PRIORITIZE_EVIDENCE_ALIGNMENT_REVIEW；它不是已证明的主因标签，也不表示任何新方法有效。

当前上下文此前已经接触模型排名/诊断。移除预测字段不消除这种暴露；没有新建Agent或独立模型，也没有证明OS级隔离。Q2要求Top10比较，但§5又限制审查输入、禁止预测候选，因此保留竞争比较受阻。两个附件还缺少§8.3后半至§13.3，不能宣称未知章节中的所有要求均已满足。

## B. 全量覆盖、输入及实际方法

冻结查询384，输出384，唯一输出384，缺失0、重复0。逻辑步骤80，目标技术54，查询×目标Gold分配520，多Gold查询86。这里的54是本审查包的目标Unseen技术集合，不是全部候选空间；不据此评价216类泛化。

384条查询只有145种不同可见文本，2178个显示行实例；71个步骤各5查询、4个步骤各4查询、2个步骤各2查询、3个步骤各3查询。它们不是384次独立攻击。execution_id沿用提供的simulation_id别名，不能据此认证独立攻击执行；view_id原字段保留，样本r后缀的派生映射见QUERY_STEP_VIEW_MAP.csv。

Gold侧未形成记录0；顶层NOT_EVALUABLE为0。这个0不代表所有问题都可评价：384条的Top10比较都未评价，独立预测盲审完成0，独立人工裁定0，2618个条件中842个NOT_EVALUABLE。所有384条仍需人工复核。

输入只来自旧诊断项目冻结证据卡，源SHA256为d1bcc8cbaf993f15f8ba1eca14a1958988f92e1d06a8fe94be485c32e9256f80。准备程序解析混合JSON容器，只输出日志/目标定义/元数据白名单；审查者未新增查看排名或竞争候选。必要历史文件只做哈希核验，没有导入其错误分析内容。

实际先读54个冻结定义，再用80个步骤内去重阅读辅助表读取全部737条不同显示行及其逐查询位置，保留384条身份和视图差异。判断笔记随后按当前查询的字面出现位置落实引用；程序仅负责序列化/求交，不是新模型推理。没有声称54个条件释义或384个判断具有独立上下文。

Fact ID是本轮生成的**显示行来源定位符**，不是原生日志事件ID；visible_record_count单位是显示行。省略事件数全部null，完整日志、事件边界与原生因果溯源未认证。对可见PROCTITLE/EXECVE字段做105项静态十六进制解释，其中10项末尾单半字节无法解码；不执行内容，也不把这种边界直接归因于某个预处理阶段。

## C. 证据对齐计数

| 类别 | 顶层查询数，互斥 | 至少一个目标具有该判断，非互斥 |
|---|---:|---:|
| 直接相关证据 | 24 | 31 |
| 部分证据 | 102 | 95 |
| 背景相容 | 74 | 94 |
| 当前视图无相关证据 | 148 | 197 |
| 输入不足 | 4 | 4 |
| 已比较后竞争歧义 | 0 | 0 |
| Gold范围/粒度不确定 | 32 | 34 |
| 顶层不可评价 | 0 | 0 |

顶层列合计384。目标级any列可以重叠，不能合计；例如同一查询可以直接支持账户创建，但另一个目标的父类参考范围仍不清楚。31条任一目标直接证据覆盖9个逻辑步骤；24与31不是矛盾。32与34的区别同理。

“已比较后竞争歧义0”只说明本轮没有完成这种候选比较并赋该标签，**不能解释成没有竞争歧义**。竞争区分能力的数量应为null/未评价，不是0。顶层无相关148，以及任一目标无相关197，都只针对当前可见范围，不能说这些攻击没有发生。

2618条条件状态：直接支持69、部分支持212、未建立1487、当前视图不可观测8、不可评价842、明确反证0。一个动作可能支持多个条件，这些不是事件数。复合条件已拆分：例如账户创建的状态有直接证据，但“维持访问”目的未建立；窗口枚举请求可直接相关，不认证实际返回列表。

多标签诊断：可观察证据31、部分证据95、背景94、当前视图无相关197、粒度问题34、输入不足4、语义原因未解决384。Gold_LOG_GRANULARITY_MISMATCH用于潜在范围不对齐，**不表示34条已证实错标**。全部384条的OBSERVATION_COVERAGE_LIMITATION是裁定范围限制，不能把它统计成384个已确定输入致错案例。完整重叠矩阵另存CSV。

## D. 主要发现、负结果和限制

明确相关动作确实存在。REV_0020的VISIBLE_LINE_002/003记录useradd new group/new user，支持本地账户创建状态；REV_0022的VISIBLE_LINE_001记录lspci请求；REV_0173的服务停止记录以及REV_0181的Puppet catalog Exec成功记录也有相关动作。它们仍不自动建立攻击者归属、授权边界或Gold相对其他技术的唯一性。

同一步骤的视图差异会改变证据资格。1-25中REV_0022等有lspci，REV_0025只有普通SSH凭据/会话，后者不能借用前者。REV_0027的command -v lsusb只检查工具存在，不是列举USB设备。系统日志时间戳也不能当作主动查询系统时间。

行为准备或共现不能补成完整机制。下载文件不等于执行、窃取令牌、改PAM或建立远控；Firefox profile/glean文件维护不等于按键/剪贴板截获。REV_0158有encrypt参数但没有加密后内容与可用性认证，REV_0159主要是改名，不能把后缀当成加密证据。IDS签名只按派生模式看待，不当作完整原生HTTP载荷。单次syscall success=no不反驳整个技术；connect的-115也不单独认证最终连接结果。

部分冻结参考的父类标题与正文范围不一致。REV_0168可见本地rm/delete，而T1485冻结正文展开云生命周期策略；REV_0211可见Shorewall ACL改变，而T1599正文展开NAT。这要求核查知识生成/父子技术映射合同，不能用这些子类型条件否定全部父类，也不能为匹配日志临时扩大正文。这类查询至少一个目标有疑问共34条。

Top10竞争技术没有进入本轮审查输入。没有进行逐对区分、排除竞争解释或独立语义充分性裁定，因此不能断言模型必须把Gold排在前列，也不能给出“语义表示失败”“标签错误”或“截断致错”的真实份额。根因占比、准确率/Precision/Recall/F1、显著性和算法增益均未计算。AI自评置信度不是校准概率；同一模型、同一上下文可能共同偏差。

**统计验证与图件**：本轮只进行行政计数与覆盖/来源核验，没有合法独立参考和独立样本假设，故未进行假设检验、效应量或置信区间。报告使用计数表，未制作暗示根因分布的科学图；figure-catalog.md明确记录未生成。

**对原判断的修正**：本轮不能支持从“Seen/Unseen仍难兼顾”直接跳到“应再训练语义模型”。已确认的是若干当前视图证据和参考范围存在裁定边界；未确认的是这些边界、表示不足与融合机制分别造成多少失败。只读预审尚未验证修正数据/评价合同能改善多少预测。

## E. 唯一下一步决策与准入答案

**PRIORITIZE_EVIDENCE_ALIGNMENT_REVIEW**。

理由：完整384记录中，31条至少有相关直接动作，197条至少一个目标在当前视图无相关证据，34条有具体范围疑问；所有384条没有独立语义裁定且Top10比较受阻。证据资格与目标范围是当前进入算法研究前的首要流程阻断。这是**同上下文AI预审等级**的优先级建议，不能称为“已证实的主要失败机制”。

次要待核查因素是输入视图/字段覆盖和冻结知识的父子范围；二者与表示/排序原因都未得到因果归属。应由独立人工先核验带直接引用、多Gold与范围疑问的案例，并明确候选比较可读取的合同，完成该项后再决定是否具备新模型实验依据。本轮不执行这些后续工作。

最低准入八问（来自实际记录，保留重叠与未知）：

1. 当前日志存在Gold相关直接证据的数量：31。顶层直接类别为24；31来自目标级记录，分布于9逻辑步骤。仅相关动作/尝试，不是完整技术或恶意归属认证。
2. 可区分Gold与主要Top10竞争技术的数量：未评价/无法确认。未评价；比较完成0，受阻384。不能把未知改写为0个可区分。
3. 仅支持宽泛行为描述的数量：169。顶层部分或背景共176，其中7个查询另有目标级直接证据，故排除后169。操作性AI分类，非真值。
4. 受输入视图或覆盖边界限制的数量：384。均只有冻结视图，完整源日志与省略数未知；其中4个顶层输入不足。这不证明384个错误由视图造成。
5. Gold粒度/映射仍有具体疑问的数量：34。顶层32；不是34个已证实错标，父类正文范围不完整不能用于否定完整父类。
6. 需要独立人工裁定的数量：384。历史信息暴露、Top10未比较且没有独立人工参考；已完成人工裁定0。
7. 强词法或冻结GTE可解决但融合错误处理的数量：未评价/无法确认。本轮不读取历史排序或重算模型，未评价，不能从本轮证据断言存在或不存在。
8. 可由数据/评价合同修正直接解决的数量：未评价/无法确认。已识别核验对象与参考范围风险，但未修改合同或重评，尚无已证明能修复预测的数量。

## F. 交付与重现索引

全部新产物只位于/Users/tianxd/Documents/mid-term/research3_open_vocab_384_case_blind_review01，没有覆盖历史实验。主要文件：

- reports/analysis-report.md、stats-appendix.md、figure-catalog.md：证据等级、计数口径及不适用的统计。
- review/QUERY_EVIDENCE_REVIEWS.jsonl：384条完整逐查询预审。
- review/CONDITION_EVIDENCE_MATRIX.csv：2618条条件状态和引用。
- review/HUMAN_REVIEW_QUEUE.csv：384条人工待核验项，保留冻结顺序。
- inputs/FROZEN_REVIEW_MANIFEST.json、VISIBLE_FACT_REGISTRY.jsonl：冻结顺序与2178个来源定位符。
- review/GOLD_CONDITION_CATALOG.json、step_judgments.json：冻结定义释义及实际笔记。
- results/QUERY_REVIEW_SUMMARY.csv、QUERY_STEP_VIEW_MAP.csv、DIAGNOSTIC_LABEL_OVERLAP.csv、REVIEW_COUNTS.json、MINIMUM_ADMISSION_ANSWERS.json：完整计数与映射。
- protocol/BLINDING_AND_SCOPE_DISCLOSURE.json、BLOCKER_REGISTER.json、EXECUTED_REVIEW_PROTOCOL.md：暴露、冲突、缺失章节与实际方法。
- results/FINAL_VALIDATION.json、VALIDATION_CHECK_DETAILS.json、OLD_ASSET_INTEGRITY_AUDIT.json：独立程序结构/引用核验与旧资产审计；不代表语义裁定。
- RUN_MANIFEST.json、manifests/DELIVERY_SHA256.json：实际命令、资源、失败历史、代码/输入/交付哈希。

复现仅使用已有Python与标准库。脚本prepare_inputs.py负责白名单准备；build_condition_catalog.py保存人工式释义；materialize_reviews.py仅将既有判断序列化并限制引用；decode_visible_hex.py静态解释编码；build_reports.py派生表格/报告；validate_reviews.py独立做结构核验；finalize_delivery.py封存交付哈希。重跑会覆盖本运行自己的派生产物，审阅者如需另一次运行应先复制到新的版本目录，不覆盖本次封存结果。

## G. 资源、完整性与停止

新增程序化模型/API调用0、新增Agent调用0、Embedding/前向0、训练0、GPU任务0、下载0、网络访问0、服务器操作0。当前助手自身语义阅读是本轮AI预审过程，不虚称未使用AI；其内部Token/算力没有独立计量。CPU工具均为已有本地Python标准库，线程/峰值内存未做硬计量，未启动并行训练任务。

旧诊断项目历史清单59项全部匹配；旧融合项目211项中210项匹配，一份报告存在此前已披露的哈希差异：历史期望915ba7a6d9030102cfa367b11505517e36cdc93eee86c4b08f2ddaf759284310，当前950167a78a289e0d5b5c17a80c0b026fffaead653b11c8059fb4a29f3e1d61ee。本轮未修复或改写。另对两目录281个实际文件（856290657字节）保存预审后、交付生成前快照，交付核验时均未变化；这个快照不能冒充全任务开始前快照。其他历史目录没有本轮写操作，未逐文件重做哈希。

自动检查的通过范围是覆盖、序列化与引用合法性；完整独立盲审合同仍为NOT_SATISFIED，不宣称整体PASS。没有相关证据不等于技术未发生，证据存在也不等于Gold唯一正确，当前视图不能代表全部原始日志。所有结果仍是AI_BLIND_PRE_REVIEW_NOT_GOLD。本轮在封存后停止，不自动训练、改排名或启动Agent。
