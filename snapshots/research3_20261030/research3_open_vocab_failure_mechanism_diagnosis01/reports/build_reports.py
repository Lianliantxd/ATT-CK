"""Evidence-first diagnosis report; no source predictions are modified."""
import csv,json,statistics,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def read(n):
 with (R/n).open() as f:return list(csv.DictReader(f))
def write(n,t):p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t.strip()+'\n')
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n'
def main():
 audit=json.loads((R/'results/INDEPENDENT_DIAGNOSTIC_AUDIT.json').read_text());assert audit['status']=='PASS' and audit['source_sha256']==sha(R/'diagnostics/independent_audit.py')
 receipt=json.loads((R/'results/DIAGNOSIS_EXECUTION_RECEIPT.json').read_text());evidence=json.loads((R/'results/EVIDENCE_AND_MAPPING_SUMMARY.json').read_text());ar=json.loads((R/'inherited/ASSET_HASH_AUDIT.json').read_text())
 counts=read('INDEPENDENT_HIT_RECOUNT.csv');base=next(x for x in counts if x['seed']=='17' and x['view_id']=='ONE_VIEW_PER_STEP');losses=[x for x in jl(R/'GTE_HIT_C4_LOST_CASES.jsonl') if x['seed']==17 and x['view_id']=='ONE_VIEW_PER_STEP'];assert len(losses)==int(base['lost_hit_queries'])
 counttable=table(['视图','种子','Unseen查询/Gold对','GTE命中/漏掉','C4命中/漏掉','保留/丢失/新增','双方漏掉'],[['ONE' if x['view_id']=='ONE_VIEW_PER_STEP' else 'MULTI',x['seed'],x['unseen_target_queries']+'/'+x['unseen_gold_pairs'],x['gte_hit_queries']+'/'+x['gte_miss_queries'],x['c4_hit_queries']+'/'+x['c4_miss_queries'],x['retained_hit_queries']+'/'+x['lost_hit_queries']+'/'+x['new_hit_queries'],x['both_miss_queries']] for x in counts])
 pairtable=table(['统计单位','分母','GTE命中','GTE漏掉','C4命中','C4漏掉','丢失/新增'],[['查询',450,66,384,34,416,'32 / 0'],['查询×Unseen Gold技术',605,66,539,34,571,'32 / 0']])
 partition=table(['互斥查询分组','数量','占450查询','所能支持的判断'],[['GTE命中且C4保留',34,'7.56%','未见排名保留'],['GTE命中但C4丢失',32,'7.11%','监督修正引起的可定位排名损失'],['GTE已漏掉，但至少一个正确未见类的内部次序≤10',35,'7.78%','跨Seen/Unseen竞争候选；并不保证兼顾Seen可修复'],['所有正确未见类的内部次序均>10',349,'77.56%','保持未见内部次序的Seen调分无法使其命中Top10']])
 scene=read('results/PRIMARY_DIAGNOSIS_BY_SCENE.csv');scenetable=table(['场景','含Unseen查询','GTE漏掉','内部次序>10','仅跨类阻挡候选','融合丢失','Mixed中仅命中Seen'],[[x[k] for k in ['fold_id','unseen_query_count','gte_miss','within_unseen_order_gt10','cross_group_block_only_candidate','gte_hit_c4_lost','c4_mixed_seen_hit_unseen_miss']] for x in scene])
 cf=table(['视图','种子','丢失Gold对','移除Seen监督后恢复','移除Seen偏置后恢复','恢复GTE后命中','γ=0案例','默认参数案例'],[['ONE' if x['view_id']=='ONE_VIEW_PER_STEP' else 'MULTI',*[x[k] for k in ['seed','lost_gold_pairs','remove_supervision_restored','remove_bias_restored','restore_gte_restored','lost_cases_with_gamma_zero','lost_cases_default_parameter']]] for x in read('COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv')])
 cases='# ONE主协议：32个丢失案例的全量程序性归因\n\n固定seed17逐查询/Gold，其他两种子同口径32例完整记录在JSONL和CSV，不把重复种子当新增攻击。每例主标签只解释冻结算式的排名变化，语义/标签原因均UNRESOLVED。\n\n'
 for i,x in enumerate(sorted(losses,key=lambda x:(x['sample_id'],x['candidate_technique_id'])),1):
  comp=sorted(x['crossing_seen_candidates'],key=lambda c:-c['c4_margin_over_gold']);top=comp[0]
  cases+=f'''## {i}. {x['sample_id']} / {x['candidate_technique_id']}

场景{x['scenario_id']}；执行标识`{x['simulation_id']}`；Gold共{x['gold_count']}项，Mixed={x['is_mixed']}。全部已曝光开发材料。GTE原始cosine={x['gte_raw_score']:.9f}、全216名次{x['gte_rank']}；C4 Gold得分={x['c4_score']:.9f}、名次{x['c4_rank']}。这两种原始数值不在同一量纲，不能直接相减解释。

实际公式`zGTE + {x['lambda']}·Iseen·zB3 − {x['gamma']}·Iseen`，参数来源`{x['parameter_source']}`。Gold为Unseen，因此监督与偏置贡献均0，C4 Gold得分等于已保存的zGTE={x['gte_standardized_contribution']:.9f}。Unseen内部名次保持{x['unseen_internal_order_rank']}；它前面的Seen由{x['gte_seen_before_gold']}增至{x['c4_seen_before_gold']}，精确解释全216名次增加{x['rank_change_from_seen_crossings']}。

GTE Top10：`{x['gte_top10']}`。C4 Top10：`{x['c4_top10']}`。新进入Top10及所有Seen跨越候选的逐项原始分数、标准化贡献、监督/偏置修正和名次在GTE_HIT_C4_LOST_CASES.jsonl。本例跨越候选中，`{top['candidate_id']}`的原始GTE={top['gte_raw']:.9f}、B3 logit={top['b3_logit']:.9f}，zGTE={top['gte_normalized']:.9f}、监督修正={top['supervised_delta']:.9f}、偏置={top['bias_delta']:.9f}，合计C4={top['c4_score']:.9f}，超过Gold={top['c4_margin_over_gold']:.9f}，名次{top['gte_rank']}→{top['c4_rank']}。

移除监督项，Gold名次恢复{x['remove_supervision_rank']}；移除偏置项为{x['remove_bias_rank']}；恢复GTE为{x['restore_gte_rank']}。主要程序性标签`{x['primary_attribution']}`，附加标签{x['secondary_attributions']}。没有Gold分数并列；C4不是RRF公式；无证据认证SCORE_SCALE_MISMATCH。分量相对尺度可能影响抬升强度，但不能在没有独立校准证据时认定尺度错误。没有独立事件证据，不能由这一结果判断攻击机制未发生、日志缺失或标签错误。

'''
 write('LOST_CASES_FULL_ANALYSIS.md',cases)
 analysis=f'''# 未见失败机制诊断：严格分析

主问题：冻结GTE和C4未见错误中，哪些是精确可分离的跨类排名竞争，哪些在保持Unseen内部顺序时根本不能由Seen校准修复？本轮仅后验离线诊断；原975查询、216候选、7场景、种子17/42/73、ONE/MULTI均保留。不作训练、模型调用、参数搜索或正式模型成绩替换。

{counttable}

{pairtable}

{partition}

独立标量复算1,263,600候选比较行、5,850查询块、3,630未见Gold行和189个跨种子/视图丢失Gold案例，最大分数差0。原GTE/B3/C4完整排名17550条核验无差异。ONE三个种子命中集合均66→34；MULTI均66→35。不能把450×3或×2当独立样本。

**核心发现**：349/384=90.89%的原GTE漏召回查询，即使只考察排名分解中未见候选的内部先后，也没有正确类位于前十；这不是计算未见候选过滤评价。C4完全保持该内部先后，因此保持现有Unseen得分而只改变Seen的任何修正，无法让这349条在全216候选Top10命中。其成因可能是表示、描述、输入预算或参考—日志不对齐，不能只归为预训练模型能力不足。

32条ONE新增丢失都能通过移除监督修正恢复；γ均0，均由合法内部验证选择，默认参数案例0、Gold精确分数并列0。主标签SEEN_SCORE_BOOST为程序性贡献解释；不认证行为因果。当前无法把它们归为Seen偏置项、RRF、同分规则或已证实的尺度不匹配。

## Claim Candidates

- Claim：当前失败主要不能由只改Seen分数解决。Evidence：349/416 C4漏召回查询具有Unseen内部序>10，严格rank恒等式和独立审计通过。Allowed：当前冻结评分及标签下的排名约束。Forbidden：349条均为模型语义能力不足或日志无证据。Uncertainty：输入/标签语义对齐未认证。Next check：独立事件证据审核。Decision：keep限定结论。
- Claim：ONE的32条原命中损失来自Seen监督修正。Evidence：移除监督32/32恢复，偏置移除0/32，γ=0且无ties。Allowed：算式层面的排名归因。Forbidden：监督学习导致GTE主干遗忘。Uncertainty：为什么错误Seen得到高logit的语义原因未知。Next check：保留案例证据卡审核。Decision：keep。
- Claim：没有发现明显父ID接口错误。Evidence：975查询原子ID归并和候选存在核对0异常，输入—样本—分数hash一致。Allowed：此次接口核验未发现错误。Forbidden：所有步骤Gold与所选日志逐事件完全一致。Next check：独立标注对齐。Decision：keep并限制。

当前最合理的后续顺序：先用独立证据区分输入/标签不对齐与语义排序不足，再决定表示改进；同时把32条可计算损失作为局部排名保真的基线检查。扩大Seen偏置网格无法越过Unseen内部序约束。本轮不执行后续改进。
'''
 stats=f'''# 统计与单位说明

所有计数是当前曝光开发样本的精确描述，未进行普通IID显著性检验、95%CI或事后优选；不存在需要校正的确认性多重p值。5采样属于同一步，3种子是旧监督头重复，7场景共享训练且脚本身份UNKNOWN。区间若报告仅为秩/分数分布分位，不是概率置信区间。

ONE主口径：975查询、195逻辑步骤；含Unseen450查询对应90步骤、605查询×Gold技术对。GTE查询漏召回384，Gold对漏召回539，不能互换分母；恰好两种单位的命中同为66，只因为这些命中查询各仅命中一个未见Gold，不是计数单位等价。

349/384=90.89%、349/416=83.89%、349/450=77.56%分别对应三种不同分母。65/90个含未见Gold的逻辑步骤在五次视图中全部有内部序障碍；74/90至少一个视图有障碍。这些仍不是独立攻击执行数。Gold对口径499/539 GTE漏召回具有内部序>10，其余40；不能用40替代查询口径35。

{cf}

Gold漏召回对的GTE全候选名次中位72、未见内部名次中位44，Gold相对第10名cosine差中位−0.0532113；失去原命中的32对GTE名次中位6.5，边界差中位+0.0078041。所有完整分位见results/SCORE_MARGIN_DESCRIPTIVES.csv。没有据这些分位设新的阈值、选择参数或重新标注样本。

{scenetable}

输入202–1580 UTF8 bytes，现有知识216描述中174项恰1000 bytes；预算或文本构建可能影响内容，但仅凭长度不能确定某查询实际被截断或缺关键证据。本轮没有读取完整上游日志或受限步骤，逐案例截断状态保持UNRESOLVED。
'''
 write('reports/analysis-output/analysis-report.md',analysis);write('reports/analysis-output/stats-appendix.md',stats)
 catalog='''# 科研图目录

1. figure01_unseen_failure_partition.pdf/svg/png：450条主协议未见查询的四个互斥组34/32/35/349，完整覆盖分母。目的：区分已保留、融合破坏、原跨类竞争、未见内部序障碍。应注意349组占大多数；解释限于冻结排名和参考，不是日志语义归因。无误差条，因为显示当前样本精确计数。
2. figure02_component_removal.pdf/svg/png：只在32个丢失Gold案例上的组件移除诊断，原GTE32、C4为0、移除监督32、移除偏置0。目的：定位算式中的损失来源。不是训练消融，不是新模型性能；不能据此选择最终模型。γ全部0是关键限制。无推断误差条。
3. figure03_scene_failure_partition.pdf/svg/png：按7个曝光场景展示同四组计数，纵轴175覆盖最大场景150，顶部明示n。目的：确认总体结构是否仅由一个场景造成；障碍分布跨场景，但样本相关、场景已曝光，不能据此声称外部泛化。小于8的段不直接写段内数字，完整精确值在逐场景CSV。

三张图均来自实际CSV，PDF/SVG/PNG独立保存；根agent对PNG进行视觉核验。首次场景图纵轴上限100导致场景6裁切，已修正到175并重新渲染；正式交付仅修正版。图的修改不改变任何数值诊断。
'''
 write('reports/analysis-output/figure-catalog.md',catalog)
 sources=['DIAGNOSTIC_PROTOCOL.json','INDEPENDENT_HIT_RECOUNT.csv','QUERY_DIAGNOSTICS.csv','UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv','COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv','results/PRIMARY_DIAGNOSIS_BY_SCENE.csv','results/INDEPENDENT_DIAGNOSTIC_AUDIT.json','results/EVIDENCE_AND_MAPPING_SUMMARY.json','reports/make_figures.py']
 figures=sorted((R/'reports/analysis-output/figures').glob('*'));assert len(figures)==9
 dump('reports/analysis-output/provenance.json',{'status':'REAL_FROZEN_SCORE_DIAGNOSIS','source_files':[{'path':n,'sha256':sha(R/n)} for n in sources],'figures':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in figures],'qualification':'DEVELOPMENT_ONLY','new_model_calls':0,'new_training':0,'parameter_search':0,'visual_qa':'root inspected3PNGs; scene6 cap corrected175 and small-segment labels omitted; final scene PNG visually rechecked','request_tail_missing':True})
 # Analysis bundle precedes this wrap-up, per the results-report gate.
 for n in ['analysis-report.md','stats-appendix.md','figure-catalog.md','provenance.json']:assert (R/'reports/analysis-output'/n).exists()
 x=sorted(losses,key=lambda x:(x['sample_id'],x['candidate_technique_id']))[0]
 mainreport=f'''---
type: results-report
date: 2026-10-28
experiment_line: open_vocab_failure_mechanism_diagnosis
round: 01
purpose: frozen-ranking-failure-analysis
status: OFFLINE_DIAGNOSIS_COMPLETED_FOR_RECEIVED_SCOPE
source_artifacts: [reports/analysis-output/analysis-report.md, reports/analysis-output/stats-appendix.md, reports/analysis-output/figure-catalog.md, reports/analysis-output/provenance.json]
linked_experiments: [DIAGNOSTIC_PROTOCOL.json]
linked_results: [INDEPENDENT_HIT_RECOUNT.csv, COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv]
---
# 开放词表失败机制 / Round 01 / 冻结排名与证据归因 / 2026-10-28

## 执行结论与研究判断

本轮发现了可以比上一轮“基础召回较弱”更精确的边界：**GTE漏掉的384条未见目标查询中，349条的所有正确未见技术在Unseen内部顺序也都排不到前十；只调Seen分数无法挽回。另35条是原GTE的跨Seen/Unseen阻挡候选。C4再破坏了32条原命中，且32条均可定位到监督分数修正。** 三者组成C4的416条漏召回，不能笼统归为“校准不够好”，也不能据此直接归为“预训练语义能力不足”。

主终态OFFLINE_DIAGNOSIS_COMPLETED_FOR_RECEIVED_SCOPE；数值诊断已完成、表示/输入/标签的语义根因仍UNRESOLVED。没有训练、模型调用、参数搜索、服务器访问或历史预测修改。当前应优先把基础语义排序问题与输入/标签对齐问题区分清楚，再决定表示改进；Seen监督分数保真是局部但明确的第二问题。没有证据支持本轮直接LoRA或增加复杂网络。

## 请求范围与资产核验

最新附件`a57d2c6c-7146-45ba-a092-6d51c5578ef3`共11303字节，在第六节6.1的单独项目符号处结束；此前两份也截断，不能声称已收到后续章节或交付要求。已完成收到的1–5节、核心GTE漏召回诊断及可审计中文报告；未知附件尾部保持REQUEST_TAIL_NOT_RECEIVED，未凭空补成用户要求。

上一轮211项交付中210项匹配原SHA，主报告一处空格从“和purge”变成“和 purge”，字节33326→33327、SHA变化；与原哈希匹配的日期镜像逐字差异仅空白。差异在inherited/PRIOR_REPORT_WHITESPACE_DIFF.patch中保留，没有修复或改写旧报告/旧manifest。数值矩阵、预测、参数、代码均未变。领域训练项目1938文件与378份Checkpoint全SHA匹配，仅校验字节，不加载运行模型。

42个fold×seed×view完整矩阵、216候选、Gold/输入与样本ID映射核验。每折Seen由唯一训练逻辑步Gold重算，支持向量与训练集一致；ONE/MULTI使用各自旧头与参数，查询输入仍是同一冻结文本视图，不能把MULTI名称当新日志文本。B3未见评分为NO_SUPERVISED_CLASSIFIER，保留closed-output人为末尾名次仅供审计，不能当语义分数。

历史评价agent预检曾提前读取旧Gold核对规模，其披露继续保留；不能声称整个历史会话未接触Gold。本轮Gold用于明确授权的后验诊断，未传入参数选择或预测流程。原C4参数仅合法内部验证/登记默认，文件SHA未变。

## 独立复算与计数单位

{counttable}

{pairtable}

975条是逻辑查询视图，不是975个独立攻击：对应195逻辑步骤、每步5采样。含Unseen450查询对应90步骤和605个query×Gold技术对。查询命中定义为至少一个当前Unseen Gold在全216 Top10；Gold对命中只看该技术。当前两种单位恰好命中同为66/34，不等于两种分母可交换。集合交并差完整保存QUERY_HIT_MISS_SETS.json与GOLD_TECHNIQUE_HIT_MISS_SETS.json，键含fold、seed、view、sample，未跨配置拼接。

所有原排名按分数降序、技术ID字典序同分规则重建。17550条GTE/B3/C4排名和2527200个GTE/C4分数单元无差异；独立第二实现进一步逐行验证1263600候选表行、5850查询块、3630 Gold行与189丢失案例，最大标量差0。基于分数/排名的D1–D4允许重叠，不相加当独立错误数。

## D1：结构性排除与C4公式

B3只为训练已见类别存在合法logit。未见类别无分类器，因此Unseen Top10=0；本轮未运行或改变GTE，不能写“主干遗忘”。C4的真实公式：

`sC4(t)=zGTE(t)+λ·Iseen(t)·zB3(t)−γ·Iseen(t)`。

zGTE、zB3的mean/SD来自原合法训练r0，当前只读取已保存值。没有重新拟合归一化。对任何Unseen候选，监督贡献和偏置贡献均为0；zGTE是原余弦的正仿射变换，所以未见类之间的全部先后次序保持。不同原始cosine与logit数值不能直接相加或比较，分量均在CANDIDATE_COMPARISON.csv.gz中逐位对齐。

## D2：32条丢失的组件归因

{cf}

ONE 32/32的主要程序性标签均为SEEN_SCORE_BOOST：在保留原γ、其他分量和全部216候选时，移除监督修正使正确Gold重新进入Top10。移除偏置0/32恢复，因为这32例原γ全部为0，参数来自合法内部验证，默认参数案例为0。未见Gold没有精确分数并列；实际C4不是RRF，因此无法归因RANK_FUSION_EFFECT。不能因为分数类型不同就认证SCORE_SCALE_MISMATCH；当前只确认标准化后监督分量怎样改变相对排名。

案例`{x['sample_id']}`的Gold `{x['candidate_technique_id']}`：GTE原始分数{x['gte_raw_score']:.9f}，全216排名{x['gte_rank']}；C4 Gold分数{x['c4_score']:.9f}，排名{x['c4_rank']}。Unseen内部名次始终{x['unseen_internal_order_rank']}，Gold之前的Seen从{x['gte_seen_before_gold']}变成{x['c4_seen_before_gold']}，精确贡献{x['rank_change_from_seen_crossings']}个名次。移除监督恢复{x['remove_supervision_rank']}，移除偏置仍{x['remove_bias_rank']}。这解释了算式层面的丢失，不解释为何日志真实机制/标签如此。

全部32例逐例中文说明见LOST_CASES_FULL_ANALYSIS.md；全189个seed/view案例的竞争候选、原始分数、原GTE贡献、监督/偏置修正、变换后分数、排名、参数与来源在GTE_HIT_C4_LOST_CASES.jsonl。没有只挑有利例子替代全量归因。

## D3：基础召回失败的严格分解

对未见Gold g，有精确恒等式：

`rank_all216(g)=1 + 排在g前面的Unseen数量 + 排在g前面的Seen数量`。

C4没有改变Unseen内部顺序，因而`rankC4−rankGTE = Seen_before_C4−Seen_before_GTE`，对全部3630未见Gold行逐项成立。这是排名代数，不是对攻击语义做因果推理。

{partition}

349条查询的最靠前正确Unseen在内部也>10，所以至少已有10个错误Unseen在它前面；即便Seen全部移到后面，该正确类也不可能进入全216 Top10。这里**没有将候选空间过滤后计算新的模型成绩**，也没有Gold路由、阈值选择或“oracle模型”提交。此约束适用于当前固定Unseen顺序的所有Seen调分，不是整个任务不可解的证明。

另35条GTE原漏召回，内部至少一个正确类≤10，是跨组阻挡候选；需要兼顾Seen时未必能同时挽回。C4漏掉的416条恰为349+35+32：前349条超出只调Seen的能力边界，后67条存在排名空间上的局部可调条件，不能把67当作实际已恢复结果。

Gold对口径：605对中499对内部序>10；GTE漏539对，其中另40对在内部前十却没进全216前十。查询口径35和Gold对口径40不能互换。65/90个含未见步骤五个视图均有内部序障碍，74/90至少一个视图有障碍，说明不能只把问题归为偶然采样；但仍不能把90步骤当90独立执行。

{scenetable}

Gold漏召回的全216名次中位72，内部次序中位44，Gold比全候选第10名cosine低的中位差为−.0532113。该差描述当前相对排序，不存在一个被认证的绝对“语义不足分数阈值”。全部539个Gold漏召回记录的原始分数、最近错误候选、边界差、文本/描述长度、Top1/5/10与视图信息均保存，未用这些统计更改模型。

## D4：Mixed覆盖

145条Mixed中，C4有82条只命中Seen而未命中Unseen，双命中为0。Seen候选得分高不意味着该候选一定是正确Seen Gold；需要区分训练类身份与正确标签身份。D2是原未见命中丢失，D4是当前Mixed覆盖，两者可以重叠但不是同一事件集合。现象不能证明某攻击机制没有发生或日志缺证据。

## 数据与标签映射：能排除与不能排除的部分

975查询原始子技术归并到父技术与冻结Gold全部一致，Gold均在216候选内；输入Hash与样本匹配，没有检测到同一冻结文本跨不同逻辑步骤对应不同Gold的精确冲突组。结果是NO_DETECTED_ID_INTERFACE_ERROR，不能写“标签完全正确”。

标签单位为作者步骤，模型看到的是冻结有限日志视图。当前输入202–1580 UTF8 bytes；216项描述中174项恰1000 bytes。构建预算、窗口、描述长度可能影响信息，**仅凭长度不能确认某例实际被截断，更不能确认丢失了技术证据**。384条主协议GTE漏查询各有全量证据卡GTE_MISS_EVIDENCE_CARDS.jsonl，包含本轮已授权的冻结文本、Gold描述与Top10候选描述，具体语义原因均UNRESOLVED，未新造机制Gold。

证据卡原生成阶段把有限视图直接写成“已截断”，在终稿前已用专门资格修正步骤改为“有限视图已确认、实际截断未知”，修正前后SHA和变更范围见EVIDENCE_CARD_QUALIFICATION_RECEIPT。未改文本内容、分数、标签或排名。此区分避免把预算标签当作每例真实证据。

当前不能在“基础表示不足”和“日志窗口/步骤Gold不对齐”之间作最终归因。349条数学边界约束的是当前分数与参考的关系，不证明这些参考在日志中可观测。没有独立事件级证据或完整允许范围的上游核验时，应保持UNRESOLVED。

## 科研图与统计说明

![失败分解]({R}/reports/analysis-output/figures/figure01_unseen_failure_partition.png)

图1把450条分成四个互斥组，作用是区分新增破坏与原始基础障碍，不能把所有384条原失败都归为Seen竞争。

![组件归因]({R}/reports/analysis-output/figures/figure02_component_removal.png)

图2仅比较已丢失32例的组件移除，表示程序性归因，不是新模型正式成绩，也不把恢复GTE排名包装成算法增益。

![场景分解]({R}/reports/analysis-output/figures/figure03_scene_failure_partition.png)

图3保留7个场景及不同分母。共享训练、五采样、旧种子和已曝光场景不支持普通IID推断，所以不提供确认性p值或95%CI。所有计数、逐场景差异、ONE/MULTI与种子均完整保留；当前结论只用于DEVELOPMENT_ONLY诊断。

## 后续优先级与明确停止点

**第一优先：证据对齐核验与基础语义排序问题的区分。** 用现有384张全量证据卡定位哪些输入实际包含技术可观测证据；若缺独立参考则继续标未知。只有确认Gold在输入中可识别后，才把349类内部排序失败归为表示/描述改进问题。当前没有证据支持直接修改数据标签或启动模型训练。

**第二优先：监督融合的未见排名保真。** 32条原命中损失可计算定位，未来方法必须保留这个强基线约束，同时报告Seen代价。不得只靠总体MRR提升掩盖破坏。35条原跨类阻挡候选与32条新增损失应分别研究，不能扩大当前参数网格把开发集最好点当成功。

**不支持：** 把γ偏置项、默认小验证折或同分规则作为32条损失已证实原因；把所有未见错误归为“预训练模型不懂安全”；把SCORE_SCALE_MISMATCH或机制未发生写成事实；把组件移除计数当正式新算法成绩；自动LoRA、服务器前向或新增LLM。

本轮完成收到范围内的诊断后停止。请求尾部仍未收到，不声称覆盖未知章节。报告写在本地指定研究工作区，没有Obsidian或外部Page回写。

## 工件、成本与复现

主要工件：DIAGNOSTIC_PROTOCOL.json、inherited/ASSET_HASH_AUDIT.json、CANDIDATE_COMPARISON.csv.gz（1263600行）、QUERY_DIAGNOSTICS.csv（5850行）、UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv（3630行）、INDEPENDENT_HIT_RECOUNT.csv、两类集合JSON、GTE_HIT_C4_LOST_CASES.jsonl（189例）、LOST_CASES_FULL_ANALYSIS.md（ONE seed17全32例）、GTE_MISS_GOLD_DIAGNOSTICS.csv（3234行）、GTE_MISS_EVIDENCE_CARDS.jsonl（384查询）、COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv、INPUT_LABEL_MAPPING_AUDIT.csv、IDENTICAL_VIEW_DIFFERENT_STEP_AUDIT.csv、严格分析bundle、独立审计与最终哈希清单。

诊断主脚本wall{receipt['seconds']:.2f}秒，峰值RSS{receipt['peak_rss_bytes']}字节；独立最终审核wall{audit['seconds']:.2f}秒。旧Checkpoint只SHA读取，没有模型前向；本轮算术只用保存分数，不重建embedding、不装新包、CPU2线程。Tokenizer输入成本不适用，不能声称对新文本做了零成本模型推理。

复现顺序：verify_inheritance.py → run_diagnosis.py → qualify_evidence_cards.py → summarize_evidence.py → independent_audit.py → make_figures.py → build_reports.py → manifests/final_validate.py。运行前应使用新的派生目录，避免覆盖封存诊断。所有Python用-B，旧目录不生成pycache。
'''
 write('R3_OPEN_VOCAB_FAILURE_MECHANISM_DIAGNOSIS_RESULTS.md',mainreport);write('reports/2026-10-28--open-vocab-failure--r01--ranking-diagnosis.md',mainreport)
 write('FAILURE_MECHANISM_RESEARCH_DECISION.md',mainreport[mainreport.index('## 后续优先级与明确停止点'):mainreport.index('## 工件、成本与复现')])
 dump('results/RESEARCH_STATUS.json',{'status':'OFFLINE_DIAGNOSIS_COMPLETED_FOR_RECEIVED_SCOPE','request_tail_status':'REQUEST_TAIL_NOT_RECEIVED','qualification':'DEVELOPMENT_ONLY','primary_count_partition':{'retained':34,'fusion_lost':32,'original_cross_group_block_candidate':35,'within_unseen_order_obstructed':349},'semantic_root_cause':'UNRESOLVED_BETWEEN_INPUT_LABEL_ALIGNMENT_AND_SEMANTIC_RANKING','new_training':0,'new_model_calls':0,'new_search':0})
 write('README.md','''# R3_OPEN_VOCAB_FAILURE_MECHANISM_DIAGNOSIS01

主报告：R3_OPEN_VOCAB_FAILURE_MECHANISM_DIAGNOSIS_RESULTS.md。已完成收到的前五节及核心基础召回诊断；最新附件在6.1单个项目符号处截断，未编造后续要求。

当前结论：450含Unseen查询=34保留+32融合丢失+35原跨类阻挡候选+349未见内部序障碍。仅是DEVELOPMENT_ONLY离线诊断，不修改原模型/参数/预测。未访问服务器、未训练、未调用新模型、未搜索参数。

候选全表是gzip CSV，以fold+seed+view+sample+technique为键；B3不存在分类器时空分数+明确状态。原GTE分数与C4标准化分数单位不同。反事实文件只作诊断，不能作为模型正式成绩。

旧主报告一个空格导致历史SHA不同，差异已记录且不修复旧文件；其余数值资产通过。所有被引用的旧文件按本轮开始状态保留；最终检查见results/FINAL_VALIDATION.json与manifests/DELIVERY_SHA256.json。

证据卡处理需要运行qualify_evidence_cards.py，将“有限视图”与“实际被截断”区分；真实截断/机制可观测性未独立认证。全量Gold只用于后验诊断。无Obsidian回写。
''')
 print('DIAGNOSIS_REPORTS_COMPLETE',len(losses),len(mainreport))
if __name__=='__main__':main()
