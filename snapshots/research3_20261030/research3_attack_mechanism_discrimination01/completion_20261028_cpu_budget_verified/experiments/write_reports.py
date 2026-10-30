"""Generate the Chinese audit package from frozen, evaluated predictions."""
import csv
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *

def md(name,text):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x') as f:f.write(text.strip()+'\n')

def main():
    ms=read(ROOT/'results/OFFLINE_SUMMARY.json')['metrics']
    selected=[r for r in ms if r['knowledge']=='K2_DESCRIPTION_16_1' and r['input_view'] in ['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']]
    table='|预算协议|方法|输入|Top1 %|Top10 %|MRR@10|\n|---|---|---|---:|---:|---:|\n'
    for r in selected:table+=f"|{r['protocol']}|{r['algorithm']}|{r['input_view']}|{100*r['top1_accuracy']:.3f}|{100*r['top10_accuracy']:.3f}|{r['mrr']:.5f}|\n"
    scope='''本交付日期为2026-10-28。P0为已曝光开发集：975查询、195逻辑步骤、7场景、34模拟标识，285查询为多标签（29.23%）。每步骤5个抽样查询不是5次独立攻击。P1/P2仅为相关开发材料。本轮不读取原始归档、CONV-A01或受限步骤35—37正文；不执行日志命令。

主目录在本轮检查时已经存在并持续出现其他写入。为保护其文件，本续作在独立目录实现、冻结、运行及评价，再交付到主目录中的唯一新子目录；父目录和此前四个项目均保持只读。本报告仅对本续作的预测、来源及行为作保证，不替其他会话背书。目录中出现的授权声明不能替代当前对话中可核验的直接用户授权。

状态：**NO_SUPPORTED_ALGORITHMIC_GAIN**。次状态：RERANKER_FAILURE_DIAGNOSED、MECHANISM_REPRESENTATION_EXECUTED、MODEL_FORWARD_AUTHORIZATION_BLOCKED、HUMAN_MECHANISM_REFERENCE_PENDING、EXTERNAL_TEST_NOT_READY。神经表示增益与独立机制语义准确率均为N/A；不能将本结论扩大为所有机制表示无效。'''
    protocol='''两种CPU协议分别报告，禁止混合：

- BYTE：继承已冻结49条件，日志≤2000 UTF8字节、知识≤1000字节；所有视图来自同一个公共原生片段前缀。
- FEATURE：本续作真实执行49条件（40主对照、8清洗消融、1同预算字面匹配），日志同时≤2048个字符3/4/5-gram出现次数及256个BM25词，知识同时≤1024个字符ngram及128个BM25词。所有视图使用再次缩减后的相同原始观察。具体长度、截断位置和事件数见FEATURE_INPUT_BUDGETS.csv。

这里的特征计数是CPU检索器的实际输入单位，**不是GTE Token数**。相同预算指相同上限，不代表每个视图恰好相同长度。原版49条件中LiteralMechanismMatching使用完整K2卡片概念，存在知识预算差异，须单独看待；新MATCHED_K2使用同一截断K2，未作标签定制。

共98条件、95,550预测行；其中47,775行是继承的真实CPU输出，47,775行为本续作新运行。每条件完整975查询、216候选，无失败删除。原神经结果只用于审计，不作为本轮Literal神经预测。共有144项固定差值分析，完整表保留负结果。所有实验为确定性单次运行，无训练种子重复。

公共前缀的二分选择已验证可行，但字段解析和规范化使预算函数未证明全局单调；不能声称取得全局最大前缀。该限制不会使已验证的预算上限失效，但构成输入选择偏差边界。'''
    md('README.md',f'''# R3机制判别：独立续作与冻结交付

{scope}

入口：R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md；数值：MECHANISM_BASELINE_RESULTS.csv；预测：inherited/CPU_PREDICTIONS.jsonl与results/FEATURE_PREDICTIONS.jsonl、results/FEATURE_CONTROL_PREDICTIONS.jsonl。

## 环境与运行

使用现有Python3.14创建项目独立venv，无pip、无下载或系统变更。算法仅用标准库。src/frozen_extractor.py为实际Literal/Relations提取器；src/frozen_engine.py为字符TFIDF/BM25；experiments/run_feature_control.py与run_feature_ablation_controls.py为本续作实际执行代码。experiments/evaluate.py为冻结预测后的独立评价，只有评价代码读取REFERENCE。

在交付目录运行：

```bash
venvs/R3_ATTACK_MECHANISM_DISCRIMINATION01/bin/python -m unittest discover -s tests
venvs/R3_ATTACK_MECHANISM_DISCRIMINATION01/bin/python experiments/verify_delivery.py
```

为防止覆盖，生成脚本使用exclusive-create；不要在冻结目录中重跑prepare/run/evaluate。若复现实验，复制代码与frozen_inputs至新目录，依次执行prepare（需要原始冻结路径）、run_feature_control、run_feature_ablation_controls、evaluate；或使用已有冻结输入与继承快照跳过prepare。字体/绘图使用已有工具运行时，与算法venv隔离。

{protocol}

本轮服务器上传、GPU/LLM新推理、GitHub推送均为0；合同§25.2要求新服务器权限，§25.4未授予LLM预算。MODEL_FORWARD_AUTHORIZATION_REQUEST.md是具体待批准请求，不是执行回执。主目录另有后续授权文件不由本续作采用或改写。
''')
    md('CROSS_ENCODER_FORENSIC_AUDIT.md','''# Cross-Encoder取证审计

结论：未在冻结源码和保存分数中发现评分方向、索引或候选归一化错误；未重新执行模型，不能给出完整运行时无缺陷证明。

官方[模型卡](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base)使用eval模式、query在前document在后及标量raw logit。更高分代表更相关，方向未按CAM分数事后选择。固定[revision配置](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/f7481e6055501a30fb19d090657df9ec1f79ab2c/config.json)为ModernBertForSequenceClassification，单LABEL_0，8192位置；此次核查是官方格式化页面静态配置，不是新下载权重运行。

20项检查：eval/inference_mode、对应tokenizer及revision、query-doc顺序、文本对格式、单标量维度、方向、无取负、无错误正负类、无非单调变换、降序、batch输出reshape、ID-score绑定、截断、描述保留、固定候选文本、固定候选分数、无重复、父技术归一、候选合法性、评价索引。源码与5850保存行一致。原始sigmoid在精确数学上单调，不改变排序；单logit不应作单元素Softmax。未进行新的单例/批量forward，故批次稳定性尚未独立验证。

独立复算140,015个去重(sample,technique)分数，跨池差0；5850行均按(-score,techniqueID)还原。相同候选文本和分数被缓存复用，因此一致性不能冒充独立批次重测。存在fp16分数并列；新增候选既可能以更高分，也可能通过同分ID次序占位。

pair tokenizer为truncation=False、pair≤8192；上游日志2048实际Token、技术描述1024实际Token，65项描述曾截断。K增加不改变相同pair，故排除“因K改变同pair截断而降级”这一解释；**不能排除上游截断造成普遍信息损失**，不能排除领域适配问题。

来源为旧项目冻结run_neural_gpu.py、运行协议、模型下载回执、NEURAL_INPUTS和完整raw_logits；不更新模型。固定CE revision f7481e6055501a30fb19d090657df9ec1f79ab2c；Embedding e7f32e3c00f91d699e8c43b53106206bcc72bb22。

原Embedding固定窗口E3 Top10=30.26%不是本CE候选的E1前缀。匹配候选输入E1 Top10=28.72%，Top1=3.79%，MRR@10=.10667。不能把E3、旧历史词汇8.62%与本次不同预算CPU表当成同输入因果对照。

详见RERANKER_SCORING_VALIDATION.json、CANDIDATE_SCORE_CONSISTENCY.csv、CANDIDATE_RANK_TRANSITIONS.csv及results/NEURAL_CANDIDATE_DIAGNOSTICS.csv。
''')
    nd=list(csv.DictReader((ROOT/'results/NEURAL_CANDIDATE_DIAGNOSTICS.csv').open()))
    nt='|池|K|Candidate Hit %|Candidate Recall %|Top10 %|未召回|降级|已召回但仍低排|提升|\n|---|---:|---:|---:|---:|---:|---:|---:|---:|\n'
    for r in nd:nt+='|'+ '|'.join([r['pool'],r['K'],f"{100*float(r['candidate_hit']):.2f}",f"{100*float(r['candidate_recall_macro']):.2f}",f"{100*float(r['top10_accuracy']):.2f}",r['CANDIDATE_NOT_RETRIEVED'],r['CANDIDATE_DEMOTED_BY_RERANKER'],r['CANDIDATE_RETRIEVED_BUT_RANKED_LOW'],r['CANDIDATE_PROMOTED_BY_RERANKER']])+'|\n'
    md('RERANKER_FAILURE_DIAGNOSIS.md',f'''# 真实候选池退化诊断

{nt}

Top100中101查询未召回任何Gold；750查询已经召回却未进Top10，其中232为原候选排序前10被降级，518为原先亦未进前10。124查询最终Top10命中。它们分别占975的10.36%、76.92%、12.72%。这些是查询数，不是独立攻击数。

20→100时新高分/并列候选改变前10。历史审计的Gold丢失子集中，替换技术出现次数较多者为T1204(199)、T1601(151)、T1592(144)、T1574(138)、T1567(116)。这些是替换技术出现次数，非199次独立攻击，也不是已证明机制混淆。原排名与重排平均Spearman在Embedding池20/50/100为.06795/.06527/.08452。

已定位现象是候选内排序失配，并未确认所有失配由语义理解不足引起。对于步骤标签与局部日志是否可判别，仍需独立人工参考。无评分方向修复，无新融合调参，无GPU重跑。
''')
    md('MECHANISM_EXTRACTION_VALIDATION.md','''# 机制提取验证

实际代码src/frozen_extractor.py；实现名Attack Mechanism IR。Literal保留原生subject/action/object/state/result/time/provenance/uncertainty；Relations独立开关。

本续作独立回查975合法样本、4368事件、34510字段：33118原生KV、1359字面正则跨度、33 JSON指针；源位置、值、来源哈希无不匹配。997关系中878为相同source+audit时间+serial的SAME_NATIVE_AUDIT_EVENT，119为严格原生时间先后，均非因果边。公开[ausearch说明](https://man7.org/linux/man-pages/man8/ausearch.8.html)支持一audit事件可含多个记录，并不提供攻击因果认证。

3805事件结果UNKNOWN，520原生syscall报告成功、29报告失败、14返回值语义未认证。syscall成功仅是该调用结果，不是攻击目标成功。没有生命周期身份认证；PID保持PROCESS_REFERENCE_UNBOUND_LIFECYCLE；name字段不自动当文件；PATH字段文件角色仍未解析。

16个安全/语义边界单元测试全部通过；没有从uid/euid状态推断提权，没有时间相邻推因果，没有DNS地址认定攻击者。所有已选字段可逆追溯，但**不是所有原始文本均被解释**；自由文本、numeric syscall的架构语义及截断后内容可能丢失。已保留的字段引用存在率100%不等于总体字段召回率或机制语义准确率。模型视图的原生片段与事件数见各输入预算表。GTE Token长度未测。

提取/检索函数无Gold输入。管理员在提取后组包/独立评价读取Gold，不能据此声称整个项目具有OS强制标签隔离。人工机制参考为PENDING，故机制语义准确率N/A。
''')
    md('KNOWLEDGE_COVERAGE_AUDIT.md','''# 知识覆盖与机制卡审计

216父技术候选保持不变；16.1描述覆盖203，缺失13项继续按既有回退，未删除类别。缺失：T1667,T1668,T1669,T1671,T1672,T1673,T1674,T1675,T1677,T1678,T1679,T1680,T1681。候选清单与16.1覆盖并非同一版本全覆盖，必须明确该固定混合覆盖政策。未混入v18检测策略。

216机制卡共1866动作/对象词语提及，其原文跨度全部核查；这是描述中的提及，不是必要条件、实际观察或普遍机制。state/temporal/result必要条件未凭空构造。不由当前样本Gold定制。K0名称、K2描述、K3去标题、卡片、描述+卡片五知识条件全部保留。

卡片改变词频、顺序与截断后内容覆盖；即使某条件更高，也不能将收益归因为严格机制推理。继承字面匹配用完整卡片而主检索用截断文档，预算不等；新MATCHED_K2已给同截断K2对照。知识标题很短，本轮相同上限并非长度完全配对，因此标题消融不能彻底排除信息量混杂。

另继承CARD_WORD_ORDER_INVARIANCE.csv说明BM25词袋无法检测卡片顺序：结构重排对该评分器不构成新推理。完整数值见MECHANISM_KNOWLEDGE_ABLATIONS.csv，不按最优知识选择新主结论。
''')
    md('MECHANISM_ERROR_ANALYSIS.md',f'''# 错误与消融

{protocol}

{table}

BYTE BM25 Literal较RAW Top10上升3.487个百分点，MRR上升约.0061；但FEATURE同对照Top10下降1.846个百分点，字符方法亦退化。小幅字节预算结果不构成稳定算法贡献。

关系模块在K2下多数条件与Literal完全相同。必须补充：BM25原生关系/normalized_action标记不在知识文档词表，得分通道不活跃；char则没有显式结构组合能力。故目前既不能宣称关系独立增益，也不能将零增益概括为关系语义无价值。见results/INHERITED_SCORER_CHANNEL_AUDIT.json。实际feature预算对照有时进一步截断掉关系，不能冒称关系充分暴露。

清洗、去角色、去结果、去动作规范化均已执行，并保存负结果。词汇与字面机制匹配不足以检验GTE机制能力。MATCHED_K2字面匹配Top10=7.077%，MRR=.02227，未超过FEATURE K2 RAW字符11.692%或BM25 11.077%。原完整卡片字面匹配Top10=4.308%，不能跨预算称更差或更优。

30例独立固定后保留，逐例真实top10、官方标签、错误层次见results/DIAGNOSTIC_30_ANALYSIS.jsonl，属于管理员文件，不送盲审。未把每例标为“缺乏机制理解”或“局部证据不充分”：后两种因果归因还没有人工参考。当前不能估计可观测性错误的占比。
''')
    md('MECHANISM_REVIEW_GUIDELINES.md','''# 30例真实人工复核交付说明

状态HUMAN_MECHANISM_REFERENCE_PENDING。现有30包没有实际人工答案。当前Agent不代填Gold，不计人工一致率。

分配给两位互不查看对方答案的复核者，首次只给MECHANISM_BLIND_REVIEW_PACKETS.jsonl和本说明，不能给管理员DIAGNOSTIC_30*、分类结果或本报告。包中的随机编号只由管理员映射回步骤；不能因方法成绩更换例子。材料准备完成不等于完成双人盲审，也不是操作系统权限隔离。

分别审查主体、动作、对象、状态、状态变化、尝试/结果、原生时序、身份绑定，以及可见证据能否支持所述机制条件。每项给SUPPORTED_BY_VISIBLE_EVIDENCE、INSUFFICIENT_VISIBLE_EVIDENCE、EXPLICITLY_CONTRADICTED、NOT_EVALUABLE之一，写原生行/字段依据与范围限制。不能凭攻击剧本或知道Gold补全事件；同PID不能自动连生命周期，uid=0不能推获得权限。结果未知与明确失败分别记录。

双方先独立封存答案，再由第三人处理分歧；保留原始差异。官方步骤标签仍用于技术分类，不被人工可观测性判断取代。人工完成之前，证据支持准确率、语义字段正确率、机制混淆归因比例及人际一致率均N/A。
''')
    external=[
      {'source':'OTRF APT29 compound','raw_logs':'official raw archive links; Day1~367MB Day2~1.6GB; not downloaded','labels':'emulationplans/apt29.xlsx exists; native row/log join not independently completed','unit':'planned procedure/step; current local derived26-step reference insufficient','independence':'different dataset family; script/template overlap not audited','license':'root MIT; README GPL3 inconsistency; per-data terms require checking','216_mapping':'local legacy reference12 in216;9 legacy+UNKNOWN outside','decision':'EXTERNAL_TEST_NOT_READY','next':'read licensed emulation table metadata then label/version join; new raw access authorization if needed','url':'https://github.com/OTRF/Security-Datasets/tree/master/datasets/compound/apt29'},
      {'source':'OTRF atomic Windows execution','raw_logs':'four official ZIP listings verified; no archives opened','labels':'file/task ATTACK mapping not yet verified','unit':'atomic experiment; event mapping pending','independence':'unverified script overlap','license':'root MIT; dataset-specific unresolved','216_mapping':'not executed','decision':'QUALIFICATION_PENDING_NOT_TEST','next':'verify metadata labels and legal local copy before model execution','url':'https://github.com/OTRF/Security-Datasets/tree/master/datasets/atomic/windows/execution/host'},
      {'source':'AttackMate Evaluation Data v4','raw_logs':'official archive listings~36–94MB; not downloaded','labels':'public scenario/playbook annotations','unit':'3 scenarios, playbook/step linkage not verified','independence':'shared AttackMate/AttackBed lineage with CAM-LDS; not clean external test','license':'record terms must be accepted per file; not cleared for new transfer','216_mapping':'not executed','decision':'RELATED_SOURCE_NOT_INDEPENDENT_TEST','next':'do not use as independent generalization score','url':'https://zenodo.org/records/19810174'}]
    csvout('EXTERNAL_REFERENCE_QUALIFICATION.csv',external)
    md('EXTERNAL_ATTACK_TECHNIQUE_DATASET_CANDIDATES.md','''# 有界外部来源核查

核查日期2026-10-28，只查看公开页面/普通元数据，无下载原始数据。

1. [OTRF APT29](https://github.com/OTRF/Security-Datasets/tree/master/datasets/compound/apt29)：作者发布raw通道日志及Day1约367M/Day2约1.6GB归档链接；[emulationplans](https://github.com/OTRF/Security-Datasets/tree/master/datasets/compound/apt29/emulationplans)确有apt29.xlsx。没有完成表格步骤与原始事件绑定，不能仅据目录名认定可评分。[根LICENSE为MIT](https://raw.githubusercontent.com/OTRF/Security-Datasets/master/LICENSE)，而README文字写GPL3，须保留不一致并核查具体数据条款。
2. [OTRF atomic/Windows execution host](https://github.com/OTRF/Security-Datasets/tree/master/datasets/atomic/windows/execution/host)实际存在ZIP目录，旧small路径404不等于数据不存在。当前只核实文件清单，没有建立可信事件/步骤标签映射。
3. [AttackMate v4](https://zenodo.org/records/19810174)有原始日志、三场景及playbook元数据，但CAM-LDS同样使用AttackMate/AttackBed，因此不应当作已独立的新分布。[CAM-LDS论文](https://link.springer.com/article/10.1007/s10207-026-01318-x)与[当前发布](https://zenodo.org/records/18861762)不能取代本轮固定16.1知识。

本机已知Mordor Day1派生26步参考是经规则处理和实体替换的事件卡，不能冒充原始日志；21个技术ID加UNKNOWN中仅12在本216空间，其他9个历史ID与UNKNOWN未自动猜测映射。目录登记的原始路径未找到，但并未声称全机不存在副本。本轮不因该缺口扩大搜索或读取归档。人工审查标记的历史文件不等于本轮独立人工Gold。
''')
    md('EXTERNAL_DATASET_DECISION.md','''# 外部测试准入决定

EXTERNAL_TEST_NOT_READY。OTRF APT29是最具体可继续资格核查的来源：raw日志和emulation table发布入口已核实；尚缺标签版本规范化、原始事件对应、脚本重用检查、可用本地原始副本和实际模型新输入权限。未运行外部分类，没有任何外部准确率。

AttackMate Evaluation Data可作相关来源的补充检查，不可直接当独立泛化；OTRF atomic仍缺标签映射。不能把P1/P2、历史派生卡或目录存在当成合格TEST。未来需要的读取/下载权限须以具体文件与许可另行确认，本轮不自动启动。
''')
    md('METHOD_FORMAL_PROBLEM.md','''# 形式化问题与最小实现

给定合法局部观察O、216父技术集合T、冻结知识K16.1，构造R_L(O)为带来源跨度的字面字段集合；R_R(O)仅增加可由原生字段认证的同audit事件及严格时间关系。所有结构都不读取样本Gold。无法认证主体身份、结果或状态变化时输出UNKNOWN。

知识卡C(t)只保留描述中的动作/对象提及，不定义技术的必要充分条件。核心排序为s(t|O)=retrieval(R(O),K(t))，检索器为固定char3/4/5 TFIDF余弦或BM25；另以动作/对象等权Jaccard作字面匹配。它们是非神经基线，不能称为深层机制推理或创新贡献。Native事件关系不是攻击因果关系。

Gold y仅在冻结预测后的评价中出现。检验Literal相对RAW、Relations相对Literal、清洗/动作/结果/角色消融及知识视图；主指标Top10和MRR@10，辅以Top1/5、P/R@K、Micro/MacroF1@K。预测覆盖全部975查询，候选216不变。

神经方法若日后授权，应固定权重、tokenizer、同公共原生观察和真实token预算，CE使用同旧E1 Top20；新模型输入必须真正forward。当前没有这种结果，不把旧RAW神经输出迁移到Literal。
''')
    md('METHOD_RESEARCH_DECISION.md','''# GO / NO-GO

主状态NO_SUPPORTED_ALGORITHMIC_GAIN。本轮已运行CPU表示/知识/清洗对照，不支持将字面IR与原生关系组合升级为独立论文算法。BYTE的少量BM25提升经FEATURE预算敏感性控制后未保持。Literal与Relations多数相同；BM25标记无知识posting，因此关系语义通道尚未得到有效模型检验，不宜宣布关系语义已被证伪。

神经机制输入尚未forward，故“超过原始GTE/CE”无法回答。人工机制参考待审、外部TEST未就绪，不能给论文级泛化/机制准确率结论。这里的NO-GO针对当前已有证据与本实现，不是机制表示路线的普遍不可能性证明。

下一步建议（观点，未执行）：先完成有限的同输入神经对照与真实人工可观测性参考，再决定是否转向领域对比学习/困难负例适配。现有证据不足以批准堆叠关系或增加Agent/Reflection，也不足以直接开训。未发现需修正的评分方向，无将实现修复冒充创新。
''')
    answers=[
      '未在源码与保存输出发现足以解释退化的评分错误；新运行时验证未做。',
      '一致。官方标量logit更大更相关，未根据开发分数择方向。',
      '一致：140015去重pair跨池差为0；缓存复用，不是批次重跑。',
      'Gold丢失子集替换频繁者T1204、T1601、T1592、T1574、T1567；次数见诊断报告。',
      'Embedding100：101未召回、750已召回但Top10失败、124命中；20/50完整表保留。',
      '排除保存输出索引错误及K改变同pair截断；不能排除上游日志/65描述截断的普遍损失。',
      '是；30逻辑步骤在新预测前冻结，未替换。',
      '是；10降级、6提升、6已召回共同失败、4共同正确、4未召回，全部7场景；非独立TEST。',
      '是，stdlib可执行提取器、4368事件和完整来源跨度。',
      '是，878同原生audit事件与119严格时间先后关系；无因果认证。',
      '34510已选字段逐个核查无源不匹配；不保证未识别原文的完整字段召回。',
      '未发现此类推断，16边界测试通过；独立人工语义审查仍待完成。',
      '原生success只限定syscall；结果未知3805、成功520、失败29、返回语义未认证14。',
      '是，216张、1866原文动作/对象提及。',
      '未新增必要条件；通用规范化仍是工程设计，不是经过人工Gold验证的完备本体。',
      '提取与预测数据流未读Gold，ID模式已屏蔽；组包管理员及独立评价读取Gold；不是OS强制盲测。',
      'K2 Literal字符Top10 BYTE9.128%、FEATURE3.385%，对应RAW14.872%、11.692%。',
      'BYTE BM25 Top10有3.487个百分点提升，FEATURE退化1.846个百分点；未证明稳健增益。',
      '否，新机制GTE/CE推理0次。',
      '是，MODEL_FORWARD_NOT_AUTHORIZED；附件§14F2/25.2要求覆盖本轮的新授权。',
      'N/A，不用旧RAW的Embedding成绩代替。',
      'N/A，不用旧RAW的CE成绩代替。',
      '未证明。BM25关系标记无posting，零差值不构成对关系语义的有效否定。',
      '尚不能作单因果归因；预算敏感性与清洗/去角色/去结果/去规范化已真实运行并全部保留。',
      '若干词汇条件有差异，但卡片改变词频/顺序/覆盖，未排除词汇混杂，不能称深层知识贡献。',
      '同截断K2字面匹配Top10=7.077%，低于FEATURE RAW字符11.692%；未建立强新方法效果。',
      '按查询候选Gold缺失精确登记；20/50/100分别520/313/101。',
      '100池750条已召回却Top10失败；其中232原前10被降级，518原本也未前10。',
      '无法给数量或比例；局部证据充分性缺独立人工参考。',
      '领域失配、截断、机制可观测性、标签单位差异的具体贡献仍未分离。',
      '没有，30例已组包，HUMAN_MECHANISM_REFERENCE_PENDING。',
      '机制支持准确率、语义字段准确率、证据不足归因比例、人际一致率均N/A。',
      '已核实OTRF原始日志与emulationplans发布入口，但完整标签对齐/许可/脚本独立性待核验。',
      '否，EXTERNAL_TEST_NOT_READY；P1/P2不是独立TEST。',
      '没有证实独立算法贡献，NO_SUPPORTED_ALGORITHMIC_GAIN；不夸大为所有机制无效。',
      '建议先完成有限神经输入对照与人工参考，再决定领域适配；本轮停止，不自动训练。']
    qs=Path('/Users/tianxd/.codex/attachments/d948f03b-55e3-40ad-9353-2a61ba9e6f2b/已粘贴的文本.txt').read_text().split('# 二十四、最终报告必须回答的科研问题')[1].split('# 二十五、')[0]
    questions=[l.split('. ',1)[1] for l in qs.splitlines() if l.split('. ',1)[0].isdigit()]
    assert len(questions)==len(answers)==36
    qa='|编号|问题|实际回答|\n|---:|---|---|\n'+''.join(f'|{i}|{q}|{a}|\n' for i,(q,a) in enumerate(zip(questions,answers),1))
    md('R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md',f'''# R3攻击机制判别实际结果

{scope}

## 实验和主要发现

{protocol}

{table}

{nt}

**已确认**：排序实现静态/保存分数审计通过；合法Literal/Relations数据与完整候选CPU预测可运行、可重算；预算敏感性控制没有给出稳定增益。**合理解释但未证实**：领域适配、日志局部可观测性、规范化丢信息可能参与失败。**无法验证**：新的GTE机制效果、独立机制准确率、真正外部泛化。不能用原生字段一致率100%替代这些未测量结果。

## 36项问题逐项回答

{qa}

## 可核验交付

RERANKER_SCORING_VALIDATION.json、MECHANISM_BASELINE_RESULTS.csv、三个预测文件、results/SUPPLEMENTARY_F1_AT_K.csv、results/INDEPENDENT_AUDIT.json、results/SOURCE_VALIDATION.json、results/DIAGNOSTIC_30_ANALYSIS.jsonl、MECHANISM_BLIND_REVIEW_PACKETS.jsonl、EXTERNAL_REFERENCE_QUALIFICATION.csv。图和严格统计限制见analysis/。

P0/P1/P2在内的752继承资产全部hash一致。本续作新增模型/LLM/GPU调用、服务器写入/上传、GitHub推送均为0。人工未完成，不冒充完成；新神经输入未运行，不冒充全任务无阻断完成。根据合同§25.2生成具体授权请求，离线部分已完成；此处不启动下一阶段。
''')
    md('analysis/analysis-report.md',f'''# 冻结开发实验分析

问题：同公共观察、同候选和同检索器时，Literal/原生关系能否超越RAW？完整数值如下。

{table}

BYTE BM25 Literal的Top10差+3.487个百分点，FEATURE差-1.846个百分点；关系无已证实独立增益。95,550行不是独立攻击样本；这是98个确定性条件在同975抽样查询的重复评价。7场景是依赖分块而非经抽样确认独立总体。144项差值、条件bootstrap与Holm校正完整保留，不能挑p值证实泛化。

Claim：本实现未显示稳定机制表示增益。证据：全条件表及两个预算敏感性协议。允许措辞：“在已曝光P0和这些CPU检索器中未证实稳定增益”；禁止：“机制理解无价值”。不确定性：神经尚未跑、BM25关系通道不活跃；决定：保留弱结论。

Claim：候选池扩大时固定pair分数不变而最终排序退化。证据：140015去重保存分数、5850池输出。允许：保存结果层面的候选竞争解释；禁止：已完成跨batch重测或已证明模型缺机制理解。不确定性：缓存、上游截断/域失配；决定：保留。

两张图为实际数值绘制，不含模型未执行成绩。无人工语义结果，无外部测试结论。
''')
    md('analysis/stats-appendix.md','''# 统计附录

每条件975查询/195步骤/7场景/34模拟，285多标签。查询抽样副本非独立攻击；195步骤共享脚本。所有条件确定性单次，训练seed数0。指标由冻结评价器重算，并另外独立复算TopK/MRR与Micro/MacroF1，全部一致；F1@1/5/10附表。

144差值：7场景内配对求和，主点估计为查询加权；场景效应样本SD、7块重抽2000次条件95%区间、128种符号翻转精确p及全144 Holm校正，均见两消融CSV。Random(42)固定；区间索引49/1949。未采用正态近似，7块太少不能证明正态性。符号检验仍需要场景效应对称/交换性，这在攻击剧本中未被证实；bootstrap区间仅条件敏感性，不是独立总体CI。没有正式显著性/优越性声明。若独立性要求严格，推断部分不具外部效度，只使用描述性效果。

不存在seed级SD，不能伪造mean±seedSD。不同协议输入预算不同，BYTE/FEATURE之间仅作稳健性敏感性，不作严格单因素提升归因。新神经Token预算未测，旧神经E1/E3窗口也不可混用。
''')
    md('analysis/figure-catalog.md','''# 图目录

1. figures/figure01_candidate_competition.pdf / .svg / .png。源results/NEURAL_CANDIDATE_DIAGNOSTICS.csv；x=候选20/50/100，y=候选命中率与CE Top10。目的：分离召回和候选内排序。应观察召回升而Top10降；改变的判断是不能继续仅扩大候选池。无误差条，为同975开发查询的描述结果；不是独立攻击统计或机制归因。
2. figures/figure02_budget_sensitivity.pdf / .svg / .png。源MECHANISM_BASELINE_RESULTS.csv；4面板为BYTE/FEATURE×字符/BM25，4输入、统一K2，y=Top10%。目的：检查字面/关系效果是否跨预算保留；观察BYTE BM25小增益在FEATURE不保留。无误差条；各协议有共同观察但跨协议观察长度不同。不能解释为GTE机制实验，也不能因关系通道不活跃宣称关系理论失败。
''')
    dump('results/DELIVERY_STATUS.json',{'primary':'NO_SUPPORTED_ALGORITHMIC_GAIN','offline':'COMPLETED',
        'new_neural':'MODEL_FORWARD_NOT_AUTHORIZED','human':'HUMAN_MECHANISM_REFERENCE_PENDING',
        'external':'EXTERNAL_TEST_NOT_READY','new_GPU_calls':0,'LLM_calls':0,'server_writes':0,'GitHub_pushes':0,
        'parent_concurrent_work':'not modified; isolated continuation only'})
    print('Reports and 36 answers written')

if __name__=='__main__':main()
