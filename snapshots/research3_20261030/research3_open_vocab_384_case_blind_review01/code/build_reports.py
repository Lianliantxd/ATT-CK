"""Describe the actual limited review; counts, not model evaluation metrics."""
import csv
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1]
C = json.loads((R / 'results/REVIEW_COUNTS.json').read_text())
rows = [json.loads(s) for s in (R / 'review/QUERY_EVIDENCE_REVIEWS.jsonl').read_text().splitlines()]
byid = {x['review_id']: x for x in rows}


def dump(name, value):
    (R / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


blockers = [
    {'id': 'B1', 'status': 'OPEN', 'scope': 'all384', 'blocker': '独立预测盲化未成立',
     'evidence': '当前助手上下文在此前工作中已接触历史排名/诊断；输入去字段不能消除记忆。',
     'effect': '独立盲审完成数0；全部结果只能是同上下文AI预审。'},
    {'id': 'B2', 'status': 'OPEN', 'scope': 'all384 competitor components',
     'blocker': 'Q2要求Top10比较，与§5审查输入禁止读取预测候选存在合同冲突',
     'evidence': '本轮审查包只输出日志、目标Gold定义及元数据；未向审查者展示Top10。',
     'effect': 'Top10比较完成0、受阻384；可区分竞争技术的数量为null/未评价，不能记为零。'},
    {'id': 'B3', 'status': 'OPEN', 'scope': 'request completeness',
     'blocker': '附件缺少§8.3后半至§13.3',
     'evidence': '第一份附件在“没”字处结束；第二份直接从§13.4开始。',
     'effect': '不能确认缺失章节中特定文件名或额外合同已经满足；按已收到内容尽量完整交付。'},
    {'id': 'B4', 'status': 'OPEN', 'scope': 'all384 adjudication',
     'blocker': '没有独立人工Gold、完整源日志、省略数量或原生Fact ID',
     'evidence': '本轮仅审查既有冻结卡。2178个Fact ID是显示行定位符。',
     'effect': '不得计算正式准确率或因果根因份额；当前未见不代表原始事件未发生。'},
    {'id': 'B5', 'status': 'DISCLOSED_PRE_EXISTING', 'scope': 'legacy integrity',
     'blocker': '融合项目一份旧报告与其历史交付清单哈希不一致',
     'evidence': '详见OLD_ASSET_INTEGRITY_AUDIT.json中的完整路径和两个SHA256；此前已披露该差异。',
     'effect': '本轮不修复，不声称全部历史清单无差异。281个观察文件在本轮快照后未变化；快照在预审后建立。'}]
dump('protocol/BLOCKER_REGISTER.json', blockers)

admission = [
    {'question': '当前日志存在Gold相关直接证据的数量', 'count': 31,
     'unit': '查询，至少一个目标Gold；非互斥',
     'qualification': '顶层直接类别为24；31来自目标级记录，分布于9逻辑步骤。仅相关动作/尝试，不是完整技术或恶意归属认证。'},
    {'question': '可区分Gold与主要Top10竞争技术的数量', 'count': None,
     'unit': '查询', 'qualification': '未评价；比较完成0，受阻384。不能把未知改写为0个可区分。'},
    {'question': '仅支持宽泛行为描述的数量', 'count': 169,
     'unit': '查询，操作定义：顶层部分/背景且没有任何目标直接证据',
     'qualification': '顶层部分或背景共176，其中7个查询另有目标级直接证据，故排除后169。操作性AI分类，非真值。'},
    {'question': '受输入视图或覆盖边界限制的数量', 'count': 384,
     'unit': '查询，非互斥裁定限制',
     'qualification': '均只有冻结视图，完整源日志与省略数未知；其中4个顶层输入不足。这不证明384个错误由视图造成。'},
    {'question': 'Gold粒度/映射仍有具体疑问的数量', 'count': 34,
     'unit': '查询，至少一个目标；非互斥',
     'qualification': '顶层32；不是34个已证实错标，父类正文范围不完整不能用于否定完整父类。'},
    {'question': '需要独立人工裁定的数量', 'count': 384,
     'unit': '查询', 'qualification': '历史信息暴露、Top10未比较且没有独立人工参考；已完成人工裁定0。'},
    {'question': '强词法或冻结GTE可解决但融合错误处理的数量', 'count': None,
     'unit': '查询', 'qualification': '本轮不读取历史排序或重算模型，未评价，不能从本轮证据断言存在或不存在。'},
    {'question': '可由数据/评价合同修正直接解决的数量', 'count': None,
     'unit': '查询', 'qualification': '已识别核验对象与参考范围风险，但未修改合同或重评，尚无已证明能修复预测的数量。'}]
dump('results/MINIMUM_ADMISSION_ANSWERS.json', admission)

with (R / 'results/QUERY_STEP_VIEW_MAP.csv').open('w', newline='') as f:
    fields = ['source_ordinal', 'review_id', 'sample_id', 'logical_step_id', 'scenario_id',
              'execution_id', 'fold_id', 'view_id', 'derived_sample_suffix', 'input_view_hash']
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for i, x in enumerate(rows, 1):
        w.writerow({'source_ordinal': i, **{k: x[k] for k in fields if k in x},
                    'derived_sample_suffix': x['sample_id'].rsplit('-', 1)[-1]})

illustrations = []
for rid in ['REV_0020', 'REV_0022', 'REV_0025', 'REV_0027', 'REV_0033', 'REV_0118',
            'REV_0158', 'REV_0159', 'REV_0168', 'REV_0173', 'REV_0181', 'REV_0211', 'REV_0355']:
    x = byid[rid]
    refs = {f for g in x['gold_reviews'] for f in g['supporting_fact_ids'] + g['context_fact_ids']}
    illustrations.append({'review_id': rid, 'sample_id': x['sample_id'],
                          'overall': x['overall_evidence_assessment'],
                          'gold_reviews': x['gold_reviews'],
                          'visible_facts': [f for f in x['visible_facts'] if f['fact_id'] in refs],
                          'reasoning': x['current_view_reasoning'],
                          'role': 'illustrations after exhaustive384 record review; not a sample substituted for review'})
dump('results/ILLUSTRATIVE_CASES.json', illustrations)

protocol = '''# 本轮实际执行合同 v1

执行范围为已有冻结卡中的384条查询，保持原顺序与全部多Gold；不读取原始归档或受限步骤，不扩大数据范围。
审查输入仅为对应查询的既有文本、目标Unseen Gold冻结定义及来源/覆盖元数据。输入准备程序解析过混合JSON容器，但仅输出白名单字段；审查者没有新增查看预测字段。

实际为同上下文AI预审：当前上下文已接触历史排名和错误分析，PREDICTION_BLINDING_NOT_ENFORCED。没有新建Agent、独立模型或OS级隔离。必需的AI_BLIND_PRE_REVIEW_NOT_GOLD字段是状态标签，不表示盲化已成功。

实际读取方法：先阅读54个冻结定义，再按80个逻辑步骤读取全部737条步骤内去重显示行及其逐查询出现位置；这些覆盖2178个显示行实例、384条查询。逐步骤人工式AI笔记保存在step_judgments.json，引用在序列化时严格与当前查询出现位置求交。没有把多个查询合成一个评价单位；但是条件整理与多视图阅读共用上下文，不能声称独立条件提取或独立逐案裁定。

GOLD_CONDITION_CATALOG.json是对冻结原文的同上下文释义。字面原文不变；may、示例、目的、必要动作和结果分开。子类型条件不得当作父技术全部变体的必要条件。复合条件即使含直接相关动作，也可以只有部分支持；目的和未显示结果保留未知。

Fact ID为本轮生成的显示行定位符，不是原生事件ID。visible_record_count单位是显示文本行；没有把多行审计事件认证为多个独立事件。omitted_record_count统一null。execution_id沿用来源simulation_id别名，不独立认证攻击执行；view_id原字段保留，样本-r后缀只在映射CSV中注明派生关系。

证据状态采用请求规定的六种枚举；没有观察到不是反证，单一syscall失败不是整个技术的反证。静态十六进制解释仅针对可见PROCTITLE/EXECVE编码字段，不执行内容，不把SYSCALL寄存器值当字符串。

Q2与§5输入限制存在冲突：本轮保持审查者不新增读取Top10，因此逐案保存竞争比较未评价。没有推出不存在竞争者、Gold唯一正确或模型必须改排名。

自动验证独立于生成脚本运行，检查序列化、覆盖、引用字面与范围、枚举及旧文件哈希；它不是独立语义专家。没有性能指标、显著性、因果份额或新模型实验。

最终状态PARTIAL_REVIEW_WITH_DOCUMENTED_BLOCKERS；Gold侧有限预审384/384，完整独立盲审/Top10比较未完成。输入附件缺失§8.3后半至§13.3，无法虚构其中的文件名和合同。
'''
(R / 'protocol/EXECUTED_REVIEW_PROTOCOL.md').write_text(protocol)

(R / 'reports/analysis-report.md').write_text('''# 有限证据预审分析

问题：384个已冻结漏召回查询的当前视图是否实际包含目标Gold相关的可观察动作？本轮只回答这个有限问题；竞争排序和独立语义充分性未完成。

完整结果在QUERY_EVIDENCE_REVIEWS.jsonl，所有计数由REVIEW_COUNTS.json及CSV重现。顶层互斥：直接24、部分102、背景74、无相关148、输入不足4、粒度疑问32，其他两类0。目标级非互斥：任一直接31、任一部分95、任一背景94、任一无相关197、任一粒度疑问34、输入不足4。

没有比较算法，无法给出最优模型或模型失败根因。最强事实是“当前冻结文本与既有目标之间的证据资格尚未得到独立裁定”。这削弱了仅从漏召回现象直接跳到“语义表示失败”的推断，也不能反向证明预处理或Gold一定错误。

## Claim Candidates

- Claim：31个查询至少对一个目标呈现直接相关动作/尝试。
  Source evidence：逐目标gold_reviews、当前查询Fact引用，9个逻辑步骤。
  Allowed wording：同上下文AI预审记录到相关动作，完整技术及恶意归属未认证。
  Forbidden stronger wording：31次已确认攻击、模型必须召回、Gold唯一正确。
  Uncertainty：145种文本中的重复视图、没有独立裁定、复合命题中的目的/结果可能仍未知。
  Next check：独立人工核验引用、动作与技术范围及竞争解释。
  Decision：weaken。

- Claim：34个查询至少有一个目标存在具体范围/粒度疑问。
  Source evidence：gold_reviews及逐案冻结正文；例如父技术条目正文只展开特定变体。
  Allowed wording：冻结参考不足以裁定完整父类，需核查映射合同。
  Forbidden stronger wording：34个错标、修正映射必然提高召回。
  Uncertainty：完整父类定义与独立标注依据未提供。
  Next check：人工核验对应冻结知识生成链和原标注粒度。
  Decision：keep。

- Claim：主要失败原因是语义表示、截断或标签错误。
  Source evidence：目前没有足以排除竞争解释的独立证据。
  Allowed wording：这些原因仍未确定。
  Forbidden stronger wording：已找到主因及各原因真实占比。
  Uncertainty：全部384个Top10比较未评价，独立盲审0。
  Next check：先完成证据资格与标签范围人工核验。
  Decision：discard作为已证实结论。
''')
(R / 'reports/stats-appendix.md').write_text('''# 计数与统计边界

本轮只有审查行政计数，没有算法评估。384唯一查询、80逻辑步骤、54个目标技术、520个查询×目标分配、86个多Gold查询、145种输入文本哈希、2178显示行实例。查询不可当作独立攻击；重复文本与同一步骤多视图相关。

顶层类别互斥、分母384；逐目标类别按查询取any后非互斥，不能相加当总查询。目标分配统计分母520，也不可当攻击数量。条件状态分母2618；一个动作可支持多个条件，69个DIRECTLY_SUPPORTED条件不是69个事件。没有对未知或无法比较项填0。

没有合法独立参考，因此准确率、Precision、Recall、F1、效应量、显著性检验、置信区间及多重校正均不适用/未计算。AI置信度LOW/MEDIUM只描述自评确定性，不是校准概率。

Top10比较数0是完成工作量；可区分查询数null是未知。根因确认数量0表示未确证，不能推出该根因现实发生数为0。所有输入均有可见范围边界，这不表示384个漏召回均由输入造成。
''')
(R / 'reports/figure-catalog.md').write_text('''# 图件目录

本轮没有生成科学推断图。完整审查计数用报告表格及REVIEW_COUNTS.json/CSV呈现；没有独立语义真值，也未进行算法对比。避免用柱状图暗示真实根因或技术发生率。

图件状态：NOT_CREATED_NOT_REQUIRED_FOR_THIS_DESCRIPTIVE_AUDIT。没有缺失的已声称生成图文件。
''')

labels_cn = {'DIRECT_EVIDENCE_PRESENT': '直接相关证据', 'PARTIAL_EVIDENCE_PRESENT': '部分证据',
             'BACKGROUND_COMPATIBILITY_ONLY': '背景相容', 'NO_RELEVANT_EVIDENCE_IN_VISIBLE_SCOPE': '当前视图无相关证据',
             'INSUFFICIENT_VISIBLE_INPUT': '输入不足', 'COMPETING_TECHNIQUE_AMBIGUITY': '已比较后竞争歧义',
             'GOLD_SCOPE_OR_GRANULARITY_UNCERTAIN': 'Gold范围/粒度不确定', 'NOT_EVALUABLE': '顶层不可评价'}
table = '\n'.join(f'| {labels_cn[k]} | {v} | {C["nonexclusive_any_gold_assessments"][k]} |'
                  for k, v in C['exclusive_overall_assessments'].items())
admission_text = '\n'.join(f'{i}. {a["question"]}：{a["count"] if a["count"] is not None else "未评价/无法确认"}。{a["qualification"]}' for i, a in enumerate(admission, 1))
main = f'''---
type: results-report
date: 2026-10-28
experiment_line: open-vocab
round: 3
purpose: 384-case-evidence-review
status: partial_with_documented_blockers
source_artifacts:
  - {R}/reports/analysis-report.md
  - {R}/reports/stats-appendix.md
  - {R}/results/REVIEW_COUNTS.json
linked_experiments:
  - {R.parent}/research3_open_vocab_failure_mechanism_diagnosis01
linked_results:
  - {R}/review/QUERY_EVIDENCE_REVIEWS.jsonl
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
{table}

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

{admission_text}

## F. 交付与重现索引

全部新产物只位于{R}，没有覆盖历史实验。主要文件：

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
'''
(R / 'reports/2026-10-28--open-vocab--r03--384-case-evidence-review.md').write_text(main)
(R / 'README.md').write_text(f'''# R3_OPEN_VOCAB_384_CASE_BLIND_EVIDENCE_REVIEW01

状态：PARTIAL_REVIEW_WITH_DOCUMENTED_BLOCKERS。384条Gold侧有限AI预审已保存；独立盲审0、Top10比较0。不是人工Gold或正式算法评估。

主报告：[{R.name} 全量证据预审]({R}/reports/2026-10-28--open-vocab--r03--384-case-evidence-review.md)。

逐案文件：[{R}/review/QUERY_EVIDENCE_REVIEWS.jsonl]({R}/review/QUERY_EVIDENCE_REVIEWS.jsonl)。

核验与运行清单分别为[{R}/results/FINAL_VALIDATION.json]({R}/results/FINAL_VALIDATION.json)和[{R}/RUN_MANIFEST.json]({R}/RUN_MANIFEST.json)；完整交付哈希位于[{R}/manifests/DELIVERY_SHA256.json]({R}/manifests/DELIVERY_SHA256.json)。主决策PRIORITIZE_EVIDENCE_ALIGNMENT_REVIEW，不自动执行后续实验。
''')
print(json.dumps({'reports_generated': True, 'admission_answers': len(admission), 'blockers': len(blockers),
                  'query_step_view_map_rows': len(rows), 'decision': 'PRIORITIZE_EVIDENCE_ALIGNMENT_REVIEW'}, ensure_ascii=False))
