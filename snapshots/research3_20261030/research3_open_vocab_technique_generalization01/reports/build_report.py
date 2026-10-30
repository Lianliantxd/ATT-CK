"""Build a Chinese decision report from completed, independently checked outputs."""
import csv,hashlib,json,statistics
from pathlib import Path
R=Path(__file__).resolve().parents[1];ONE='ONE_VIEW_PER_STEP';MULTI='MULTI_VIEW_AUGMENTATION'
METHODS=['Z0','S0','C0','C1','C2','C3','C4','C5','P2','C6_B4','C6_B5']
def read(n):return list(csv.DictReader((R/n).open()))
def load(n):return json.loads((R/n).read_text())
def write(n,t):p=R/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t.strip()+'\n')
def f(x):return 'NA' if str(x) in ['NA','None',''] else f'{float(x):.4f}'
def pct(x):return f'{float(x):.2%}'
def table(headers,rows):return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)+'\n'
def main():
 assert (R/'external_dataset/server_receipts/SERVER_DOWNLOAD_RECEIPT.json').exists(),'Wait for authentic server download receipt'
 for n in ['analysis-report.md','stats-appendix.md','figure-catalog.md','provenance.json']:assert (R/'reports/analysis-output'/n).exists(),n
 assert load('results/FUSION_INDEPENDENT_AUDIT.json')['status'].startswith('PASS')
 assert load('results/EVALUATION_AUDIT.json')['status']=='PASS'
 overall=read('FUSION_RESULTS.csv');m={(r['method'],r['view_id']):r for r in overall};a=lambda method:m[method,ONE]
 strata={(r['method'],r['view_id'],r['stratum']):r for r in read('SEEN_UNSEEN_MIXED_RESULTS.csv')}
 tail={(r['method'],r['view_id'],r['stratum']):r for r in read('LONG_TAIL_TECHNIQUE_RESULTS.csv')}
 scene=read('results/SCENE_RESULTS.csv');primary=read('results/PRIMARY_HYPOTHESIS_SUMMARY.csv');sel=load('calibration/SELECTED_PARAMETERS.json')
 full=table(['方法','视图','总体MRR±种子SD','Top1','Top10','Seen MRR','Unseen MRR','H(MRR)','216类Macro-F1@5'],[[method,'ONE' if view==ONE else 'MULTI',f(m[method,view]['mrr'])+' ± '+f(m[method,view]['mrr_seed_SD']),pct(m[method,view]['top1_accuracy']),pct(m[method,view]['top10_accuracy']),f(m[method,view]['seen_target_mrr']),f(m[method,view]['unseen_target_mrr']),f(m[method,view]['H_MRR']),f(m[method,view]['macro_f1_at_5_all_candidates'])] for view in [ONE,MULTI] for method in METHODS])
 seenret=float(a('C4')['seen_target_mrr'])/float(a('S0')['seen_target_mrr']);unseenret=float(a('C4')['unseen_target_mrr'])/float(a('Z0')['unseen_target_mrr'])
 grouped=table(['方法','ALL_SEEN MRR / Top10','ALL_UNSEEN MRR / Top10','MIXED MRR / Top10'],[[method,*[f(strata[method,ONE,s]['mrr'])+' / '+pct(strata[method,ONE,s]['top10_accuracy']) for s in ['ALL_SEEN','ALL_UNSEEN','MIXED']]] for method in ['Z0','S0','C0','C2','C3','C4','C5']])
 mixed=table(['方法','Mixed任一Gold命中','Seen命中','Unseen命中','两类同时命中'],[[method,*[pct(a(method)[k]) for k in ['mixed_any_hit10','mixed_seen_hit10','mixed_unseen_hit10','mixed_both_hit10']]] for method in ['Z0','S0','C0','C1','C2','C3','C4','C5']])
 longtail=table(['方法','支持桶','目标查询','Gold折×技术对','MRR','Top10','技术等权Recall10'],[[method,b,str(int(float(tail[method,ONE,b]['n_records']))),str(int(float(tail[method,ONE,b]['target_fold_technique_pairs']))),f(tail[method,ONE,b]['mrr']),pct(tail[method,ONE,b]['top10_accuracy']),f(tail[method,ONE,b]['class_macro_recall10'])] for method in ['Z0','S0','C0','C4'] for b in ['SUPPORT_0','SUPPORT_1','SUPPORT_2_4','SUPPORT_GE5']])
 ss=[]
 for sceneid in range(1,8):
  row=[str(sceneid)]
  for method in ['Z0','S0','C0','C2','C3','C4','C5']:
   vals=[float(x['mrr']) for x in scene if x['scenario']==str(sceneid) and x['view_id']==ONE and x['method']==method];row.append(f(statistics.mean(vals)))
  ss.append(row)
 scenetable=table(['外层场景','Z0','S0','C0','C2','C3','C4','C5'],ss)
 eqtable=table(['方法','查询加权MRR','场景等权MRR','查询目标加权H','场景H均值'],[[method,f(a(method)['mrr']),f(a(method)['mrr_equal_scene_mean']),f(a(method)['H_MRR']),f(a(method)['H_MRR_equal_scene_mean'])] for method in METHODS])
 ph=[]
 for r in primary:
  ph.append([r['hypothesis'],'ONE' if r['view_id']==ONE else 'MULTI',r['method']+'−'+r['baseline'],f(r['mrr_delta']),f(r['unseen_target_mrr_delta']),f(r['H_MRR_delta']),r['mrr_positive_scenes']+'/'+r['mrr_negative_scenes']+'/'+r['mrr_tied_scenes'],r['passes_registered_development_criterion']])
 primarytable=table(['假设','视图','比较','ΔMRR','ΔUnseen','ΔH','MRR场景+/−/平','工作性验收'],ph)
 bias=table(['方法','Top1属于Seen','Top10 Seen数量','Seen MRR','Unseen MRR'],[[method,pct(a(method)['top1_seen_rate']),f(a(method)['top10_seen_count_mean']),f(a(method)['seen_target_mrr']),f(a(method)['unseen_target_mrr'])] for method in METHODS])
 calibration=[]
 for i in range(1,8):
  s=next(s for s in sel if s['method']=='C4' and s['seed']==17 and s['view_id']==ONE and s['fold_id']==f'fold_heldout_{i}')
  calibration.append([i,s['validation_steps'],s['seen_target_steps'],s['unseen_target_steps'],s['parameters']['lambda'],s['parameters']['gamma'],'固定默认' if 'DEFAULT' in s['selection_reason'] else '内验证'])
 caltable=table(['外层折','内验证步','Seen目标步','Unseen目标步','λ','γ','来源'],calibration)
 # Failure examples are predeclared category-first and lexical, never human semantic annotations.
 failures=read('results/RANK_FAILURE_PHENOMENA.csv');examples=[]
 for label,key in [('D1','D1_structural_unseen_exclusion'),('D2','D2_seen_score_bias_candidate'),('D3','D3_zero_shot_representation_limit_candidate'),('D4','D4_mixed_label_rank_competition')]:
  rs=[r for r in failures if r['view_id']==ONE and r['seed']=='17' and r['method']==('S0' if label=='D1' else 'C4') and r[key] in ['True','1']]
  if rs:
   r=sorted(rs,key=lambda x:x['sample_id'])[0];examples.append([label,r['method'],r['sample_id'],r['unseen_gold'],r['z0_unseen_best_rank216'],r['unseen_best_rank216'],r['top10_seen_count'],'UNRESOLVED'])
 error_table=table(['现象','模型','查询','Unseen Gold','Z0最佳未见名次','当前名次','Top10 Seen数','语义原因'],examples)
 error='''# 未见排名退化：现象与原因分开

D1：S0/P2没有未见分类器；所有450未见目标查询均结构排除，不是GTE主干遗忘。D2：Z0把未见Gold排入Top10、当前开放评分未命中，且Seen挤在它前面，属于分数竞争候选现象。D3：Z0也未命中该未见目标，说明当前冻结检索有召回边界；不能仅凭标签判定日志缺关键证据。D4：Mixed命中Seen却没命中Unseen。标签可重叠，计数不能相加当独立失败数。

ONE C4有450未见目标查询：34命中、416未命中；其中32在Z0能命中而C4丢失，384连Z0也未命中。相对于Z0，C4没有新增未见Top10命中。B4/B5把Z0可命中的66个未见目标全部丢失：它们能够对216描述评分，仍体现训练头排序偏置；未更新的GTE主干不能被称为遗忘。

Mixed C4有82条命中Seen而未命中Unseen；双命中0。不能由此断言某个攻击机制未发生、当前日志缺少证据或模型发生错误因果推理，所有语义原因保持UNRESOLVED。逐查询含Gold仅出现在后验评价文件，预测文件不含Gold。

以下示例按既定D1–D4类别、seed17 ONE、样本ID字典序取第一例；不是代表性人工Gold：

'''+error_table
 write('OPEN_VOCAB_ERROR_ANALYSIS.md',error)
 write('CLASS_BIAS_ANALYSIS.md','# 已见类别偏置\n\n'+bias+'''
S0/P2全Top10来自Seen是结构决定；C6_B4/B5几乎所有Top10也是Seen，但其216描述分数均可计算。C4把Top1 Seen比例降到68.51%、Top10 Seen数降到6.48，仍未保留Z0的Unseen覆盖。C1将Seen数进一步降低，却未提高Unseen MRR，说明这个有限偏置网格并未解决冻结语义召回问题。

原始GTE cosine、B3 logit、投影cosine/temperature和RRF数值不在同一量纲，不能直接比较数值高低。SCORE_CALIBRATION_DIAGNOSTICS.csv保留每fold/seed/view/method×TRAIN/VALIDATION/HELDOUT×Seen/Unseen的可用数、均值、SD、5/50/95分位及相对Z0平均名次变化。未见B3/P2为NA，不是−1e6或零概率。跨类分数分布用于后验解释，未进入调参。
''')
 decision=f'''# 科研决策

主状态：**OPEN_VOCAB_TRADEOFF_UNRESOLVED**。

次状态：OPEN_VOCAB_BASELINES_EVALUATED；UNSEEN_RANKING_RECOVERED_ON_DEV；EXTERNAL_TEST_NOT_READY；NO_SUPPORTED_NEW_ALGORITHMIC_GAIN。全部DEVELOPMENT_ONLY。

C4较B3恢复Unseen MRR到.023053，但Seen只保留{seenret:.2%}，Unseen只保留Z0的{unseenret:.2%}；未达到预登记Seen≥50%且Unseen≥80%的联合工作阈值。C3的总体/H略高于C4，RRF/频率/旧B3也完整保留。正式模型中Z0的H最高，S0总体MRR最高；没有证据支持把残差公式视作独立新算法。

固定曲线gamma=.4点的H=.053182高于Z0 .049493，说明不是所有简单参数都无法改善H；但该点是在外层诊断中观察到，不能据此改正式模型或称为新的无偏验证成绩。其Unseen仍只保留Z0约72.46%。目前的问题同时包含有限语义召回、类间竞争、薄弱内部参数选择和长尾覆盖，不能归为一个已证实因果机制。

GO：保留本轮完整分数/成熟简单融合为后续强基线，优先补全独立执行来源和非穷尽Bag标签评价接口。NO-GO：本轮算法创新成立、跨来源泛化成立、继续扩大已曝光P0搜索、直接LoRA或新GPU训练。

候选研究问题是如何在不泄漏标签的条件下保持未见语义排名及Mixed双目标覆盖，并在更可靠内部划分上选择校准。它是问题定位，不是新算法贡献证明。后续新数据模型前向与训练需独立明确范围，当前完成后停止。
'''
 write('METHOD_RESEARCH_DECISION.md',decision)
 write('OPEN_VOCAB_METHOD_COMPARISON.md','# 同一输入与候选的完整对照\n\n'+full+'\n'+eqtable+'\n'+decision)
 # Actual external execution status is maintained independently by external worker.
 ext=(R/'EXTERNAL_DATASET_QUALIFICATION.md').read_text()
 external_grant=(R/'external_dataset/SERVER_DOWNLOAD_AUTHORIZATION.json').exists()
 external_section='服务器目标：`tianxiaodan@10.109.119.118:/home/tianxiaodan/code/ATT/R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION01/`。用户指定原始日志保存在服务器，本地仅保留代码、公开元数据与核验回执。实际下载、大小、SHA、解析状态以下面外部准入审计为准。未取得或未运行外部GTE向量/融合前向，EXTERNAL_EVALUATION_PREDICTIONS为0行、结果为N/A；不得用虚拟输入补分。\n\n'+ext
 figures=sorted((R/'reports/analysis-output/figures').glob('*.png'))
 assert len(figures)>=3
 figtext='\n\n'.join(f'![{p.stem}]({p})' for p in figures)
 maintext=f'''---
type: results-report
date: 2026-10-28
experiment_line: open_vocab_technique_generalization
round: 01
purpose: seen-unseen-balance-and-external-qualification
status: OPEN_VOCAB_TRADEOFF_UNRESOLVED
source_artifacts: [reports/analysis-output/analysis-report.md, reports/analysis-output/stats-appendix.md, reports/analysis-output/figure-catalog.md, reports/analysis-output/provenance.json]
linked_experiments: [FUSION_PARAMETER_REGISTRATION.json, GENERALIZED_ZERO_SHOT_PROTOCOL.md]
linked_results: [FUSION_RESULTS.csv, METHOD_RESEARCH_DECISION.md]
---
# ATT&CK开放词表识别 / Round 01 / 已见—未见权衡与外部数据准入 / 2026-10-28

## 执行结论与决策

**简单融合恢复了部分B3结构排除的未见排名，但未实现预登记的Seen/Unseen联合保持目标。** 主状态OPEN_VOCAB_TRADEOFF_UNRESOLVED；本轮已真实完成离线分数融合、类别偏置校准、频率先验、广义零样本与长尾评价。ONE主结果：B3总体MRR .2022，冻结GTE .0582；C4 .1305、Seen .1745、Unseen .0231、H .0407。C4保留B3 Seen {seenret:.2%}、冻结GTE Unseen {unseenret:.2%}，H低于冻结GTE .0495。不能只凭Unseen由0恢复就说兼顾能力已解决。

仅训练频率C0取得MRR .1613，相当于B3数值的79.81%；此比例不是因果解释率。C4没有超过无偏置嵌套C3。所有方法为成熟简单基线，**NO_SUPPORTED_NEW_ALGORITHMIC_GAIN**；不新增训练、GPU/LoRA、模型下载或LLM。外部结果仍N/A，不能证明跨来源泛化。

## 研究对象与复现资格

本轮继承378个真实训练Checkpoint，1938项旧交付哈希逐项通过。42个fold×seed×view矩阵含17454查询分区行×216列，含GTE/B3/B4/B5完整分数；没有从Top10反推分数。53,337条历史预测排名和已存Top10分数重建差异均0。旧378训练配置不重跑，GTE主干保持原权重。B3未见列内部NaN、JSON null与availability=false，不把−1e6用作语义得分。

P0=PUBLIC_EXPOSED_DEVELOPMENT；7场景、195逻辑步骤、975相关查询、216父候选、79出现类。父技术多标签285/975；保留此前已解决统计，不重复标签审核。当前Unseen是相对于某折监督训练的未见，不能保证其从未出现在预训练语料。固定216候选的广义零样本排名也不等于任意新类拒识或开放世界检测。

折1–7 Seen数为56、60、66、75、69、66、56；其余160、156、150、141、147、150、160是候选Unseen。支持数按唯一训练逻辑步计，五采样不增添监督支持。525 ALL_SEEN、305 ALL_UNSEEN、145 MIXED互斥；Seen目标670与Unseen目标450包含同145个混合查询，不能相加为样本总数。原场景划分和purge完全继承；真实脚本依赖仍UNKNOWN。

## 冻结方法、校准与标签隔离

公式见FUSION_METHOD_DEFINITIONS.md。11方法：Z0冻结；S0旧B3；C0频率；C1原余弦减Seen偏置；C2 seen-only RRF；C3训练标准化分数加和；C4再减Seen偏置；C5 GTE加训练频率；P2 B3减频率；C6_B4/B5开放描述诊断。C3是C4 γ=0嵌套对照，不是另一新网络。

协议SHA `cceb35fc46eaeb5cc4db5973e315ab0a7288cbac5a1d0d1722031944a42289e3` 在新融合评价前冻结。RRF k60，λ={{0,.25,.5,1}}；C4 γ={{0,.1,.2,.4}}；C1原始cosine γ={{0,.01,.02,.04}}；先验系数α={{0,.25,.5,1}}。标准化参数仅来自TRAIN r0单一池mean/SD；seen与支持只来自合法训练。B3未见不参与监督rank或残差。

462模型条件的1722候选参数在合法内部验证上评分，最大化Seen/Unseen目标MRR调和均值；平局依次总体MRR、登记顺序。验证至少10步且Seen/Unseen目标各≥3步，否则默认。共210固定方法、216内部选择、36默认条件。折4只有2个验证步骤，使用默认；其他折也只来自一个内部场景，不能声称校准稳定。示例seed17 ONE（全部seed/视图在SELECTED_PARAMETERS）：

{caltable}

参数拟合与预测进程的文件访问白名单及独立源审计未发现外层Gold进入计算，预测器不按Gold类型路由。**流程偏差必须保留：评价agent在主预测完成前两次预检读取旧heldout_reference核对已公开规模；没有计算新融合性能、没有把标签送入拟合/预测或改变登记参数。** 因此不能声称“全会话任何环节均未提前读取Gold”。正式评价在保存全部预测后执行，参数hash未变；这是应用层血缘和访问记录，不是OS沙箱保证。

## 完整总体结果

每项3种子均值；固定方法跨seed重复只是对齐表结构，不是三次独立统计重复。种子SD只描述旧头/校准变化。所有Precision/Recall@1/5/10、Micro-F1及完整Macro-F1位于FUSION_RESULTS.csv；下面保留核心同口径指标。

{full}

在预登记ONE主协议中，S0保持总体及Seen目标MRR最高；Z0保持正式条件中Unseen MRR和H最高（C1的Unseen相等但H稍低）。C4较Z0 Top1增加6.77个百分点、Top10增加9.74个百分点，却降低Unseen MRR及Macro-F1；相较S0则损失Top1/Top10、恢复一些未见与Macro-F1。不存在单一指标的全面胜出。

## 场景等权与异质性

{eqtable}

{scenetable}

不能把总体平均当每场景收益。C4−Z0 MRR在5场景上升、1场景下降、1相等；C4−S0在6场景下降、1相等。完整MULTI/种子逐场景表在results/SCENE_RESULTS.csv；所有失败场景保留，未过滤后重算。

## Seen、Unseen、Mixed与单/多标签

{grouped}

ALL_UNSEEN的C4 MRR .0176低于Z0 .0478；Mixed总体MRR .3557远高于Z0 .0948，但双目标覆盖没有随之改善。单标签C4 MRR .0761、S0 .1832、Z0 .0469；多标签C4 .2624、S0 .2481、Z0 .0855。多标签“任一Gold命中”容易被Seen贡献主导，应同时看目标覆盖：

{mixed}

C4 Mixed的Unseen仅5/145命中，Seen82/145，二者没有重叠；Z0双命中6/145。总体MRR提升不是完整技术集合恢复。目标子集的P/F1会把另一目标集合真标签计为该子集FP，解释Seen/Unseen主要依据MRR、Top10和Recall。

## 长尾、频率与类别覆盖

{longtail}

支持桶按本折训练0、1、2–4、≥5固定。一个查询可以含多个支持桶Gold，所以桶查询数不能相加当975；同一技术跨折支持不同，Gold折×技术对数58/21/37/17也不是独立唯一技术数。每类无Gold时Recall为NA，Macro-F1全216分母仍保留。C4在few-shot和one-shot的MRR有所改善，但one-shot Top10仍低于Z0和S0；高频表现牺牲明显。

频率分析另见CLASS_FREQUENCY_ERROR_ANALYSIS.md。C0高支持目标MRR .5502、S0 .5509，非常接近；低支持和未见几乎无能力。描述性Spearman以种子平均后的fold×技术为单位，无因果或独立显著性解释。C4不是单纯比Frozen更高就算胜出，必须面对此先验和S0强基线。

## 类别偏置与可计算失败现象

{bias}

{error}

## 预登记假设与统计解释

{primarytable}

H1成立仅指开发数据上C4总体优于Z0且U非零；不代表保留Z0开放能力。H2未达到联合工作阈值，不能称“显著兼顾”；H3正式C1的U改善为0。H4因无合格外部模型预测为N/A。阈值Seen≥50% S0与Unseen≥80% Z0是提前冻结的工作判断，不是学科通用标准。

ONE C4−Z0查询加权ΔMRR .07234，删除任一场景的范围[.05993,.08179]；C4−S0 ΔMRR −.07163，范围[−.08542,−.05963]。范围是描述性敏感性，不能写95%CI。共享训练、重复曝光、脚本依赖未明，不能将975查询或3种子当独立攻击做普通p值。未作确认性假设检验，所有7场景方向和种子值保留。

## Seen–Unseen权衡曲线与图像解释

固定C4已选lambda，逐一使用gamma0/.1/.2/.4，全部外层预测保存23400条。ONE曲线gamma=.4的H=.05318高于Z0 .04949，Seen=.15228、Unseen=.03222；但该点只是预登记诊断，不能根据外层表现把它提升为正式提交模型。它的Unseen保持率约72.46%仍低于80%工作线。没有计算或事后选择AUC。有限网格未解决本轮正式选择问题，不证明所有简单校准都不可能有效。

{figtext}

图1用总体/Seen/Unseen三面板并列呈现收益分配，阻止只看总体。图2用固定gamma曲线展示Seen下降与Unseen回升，并区分正式C4和外层诊断点。图3与图4分别显示Mixed与长尾覆盖，强调命中一个常见标签不能代替同时恢复两类Gold。图的具体数据、误差条及解释检查清单见reports/analysis-output/figure-catalog.md。所有图为真实CSV绘制的PDF/SVG/PNG，非示意结果。

## 外部数据实例与取得事实

{external_section}

## 成本、审计与局限

重建126个旧头forward配置（42 B3+42 B4+42 B5），本地CPU矩阵运算，未重新调用GTE编码器。冻结分数重建12.20秒；有限网格拟合2.96秒；主与曲线预测17.74秒；独立主指标评价约20.15秒，tradeoff另计。时长是各脚本wall，不含人工/网络/独立复核的总工时。CPU2线程；训练更新0、新GPU前向0、新模型下载0、LLM0。新增推理输入是既有768向量，Tokenizer输入预算不适用；不能伪报“零token完成新文本推理”。

独立复算1722验证候选四指标差0、462选参差0、87,750条完整216预测与18,954,000分数单元差0；主指标6006项、分层61776项与旧冻结评价器差0。B1/B3/B4/B5历史指标复现通过。审计证明计算与数据流一致，不证明独立泛化。其余局限包括小验证场景、候选集限制、作者标签不等于机制证据、标签缺失不等于真实负例、外部单Bag非穷尽标签、原split历史Gold摘要只能通过白名单剥离而非追溯“未见”。

## 本轮改变的判断与后续动作

{decision}

保留42完整分数、全部选参、正式预测与失败细节作为以后最低比较基线。后续优先补跨来源、跨执行且评价单位清楚的正例；如果继续研究模型保持，须先定义无法由RRF、频率、分数尺度解释的剩余问题。不要扩大已曝光P0超参搜索，不以此轮结果自动启动LoRA。报告写入用户指定本地研究目录，未进行Obsidian回写。

## 逐项科研问题

'''
 answers=[
 ('是否完整继承378份Checkpoint？','是。1938旧文件hash与378份checkpoint载入核查通过；按只读路径继承，没有重训或复制修改权重。'),
 ('是否无需新GPU前向取得216分数？','是。由本地真实768维向量与旧线性/投影头重建42矩阵，所有216候选可复核。'),
 ('冻结GTE预测是否完整重建？','是。沿用同特征float32点积；对应历史完整排序和存储分数差0。'),
 ('B3预测是否完整重建？','是。实际logit来自旧w/b，seen顺序核验；缺失unseen列单独标记，闭集排名完整复现。'),
 ('每折Seen数量？','按1–7折为56、60、66、75、69、66、56，仅合法训练Gold决定。'),
 ('每折Unseen数量？','固定216的补集依次160、156、150、141、147、150、160，不能用该折保留类分布代替。'),
 ('B3未见为0的结构性原因？','已确认没有对应分类器。它不是GTE主干遗忘证据，主干未更新。'),
 ('是否运行RRF？','C2真实运行，监督排名只在seen定义；ONE MRR .0975、U .0123，完整失败保留。'),
 ('是否运行归一化分数融合？','C3真实运行，mean/SD只来自训练r0；ONE MRR .1312、U .0231。'),
 ('是否运行Seen偏置校准？','C1真实运行，ONE U与Z0相同.0445，总体略降；有限已选偏置未带来未见提升。'),
 ('是否运行监督残差评分？','C4真实运行。它是C3加seen偏置的简单成熟基线，不是新知识约束网络。'),
 ('是否运行频率先验？','C0、C5、P2全部运行；C0 .1613 MRR，支持只按唯一训练步骤计。'),
 ('校准参数是否仅内部确定？','是。210固定、216合法内部选择、36支持不足默认；1722候选及拒绝原因可复算。'),
 ('是否存在外层标签泄漏？','未发现进入拟合/预测的外层Gold或真实类型路由；但评价预检提前读旧Gold两次的时序偏差已明确，不能作全会话零访问声明。'),
 ('哪种总体MRR最高？','主ONE S0=.202153；MULTI最高为C6_B5=.187257，高于MULTI S0=.179980。ONE为预登记主评价，不能事后切换视图选赢家。'),
 ('哪种Seen目标MRR最高？','ONE S0=.294178；MULTI C6_B5=.272501，高于该视图S0。'),
 ('哪种Unseen目标MRR最高？','正式条件Z0与C1并列.044465，两视图一致；没有融合超越该值。'),
 ('哪种平衡最好？','正式条件Z0的H=.049493最高。外层曲线gamma=.4的H .053182是诊断观察，不能替换内验证选中的C4。'),
 ('最优融合是否超过冻结GTE？','ONE正式融合中C3总体MRR .131219超过Z0 .058186，但U与Macro-F1均低于Z0；按总体选优属于描述性比较。'),
 ('是否超过B3？','ONE正式融合C2/C3/C4均未超过S0总体MRR；Unseen从0恢复，同时Seen下降。'),
 ('是否改善Top1？','C4相对Z0由1.54%到8.31%；低于S0 14.77%。'),
 ('是否改善Top10？','C4 29.74%高于Z0 20.00%，低于S0 34.26%；不支持全面改进。'),
 ('是否改善Macro-F1？','C4 .013533高于S0 .008929，但低于Z0 .018320。'),
 ('525全Seen样本？','C4 MRR .133933/Top10 33.14%，S0 .269790/45.52%，Z0 .054147/18.48%。'),
 ('305全Unseen样本？','C4 MRR .017619/Top10 9.51%，Z0 .047753/18.69%，S0均0。'),
 ('145 Mixed样本？','C4 MRR .355670/Top10 60.00%，双命中0；Z0双命中4.14%。高任一命中不能代表混合集合恢复。'),
 ('是否总体提高但Unseen下降？','是。C4比Z0总体增加.072338，U下降.021412；C3/C5亦有同类取舍。'),
 ('是否Unseen恢复但Seen大降？',f'是。C4比S0恢复U .023053，Seen仅保留{seenret:.2%}，下降{1-seenret:.2%}。'),
 ('类别频率解释部分监督收益？','频率单独达到B3约79.81%的MRR数值，且高支持类很强；这是充分性对照，不是79.81%因果贡献或方差解释。'),
 ('One-shot效果？','C4目标MRR .033333、Top10 3.33%；S0 .015556/4.44%；Z0 .010635/5.33%。提升首命中位置不等于扩大覆盖。'),
 ('2–4步Few-shot效果？','C4目标MRR .157132/Top10 41.00%，S0 .137544/36.00%，Z0 .088528/29.33%；其余桶损失同时报告。'),
 ('分数分布怎样变化？','S0只有seen合法logit，C4残差只修正seen；归一化及分区分位完整保存。Top10 seen数量由S0 10降至C4 6.48，Z0为3.84。'),
 ('退化主要来自竞争还是语义不足？','不能做因果二选一。C4未见漏掉416查询，其中384 Z0也漏、32 Z0可命中后被C4挤出。两种可计算现象并存，语义原因UNRESOLVED。'),
 ('简单校准是否足够？','本轮正式选择尚未达到联合保持阈值。诊断曲线有更高H点，不能据有限网格宣称所有简单校准都不足，也不能把外层最好点当正式成功。'),
 ('是否有相对简单融合残余错误？','有Mixed双命中、未见召回和one-shot覆盖问题；C4未显示优于C3的独立增益，因此不能把这些错误自动转成新机制有效性证据。'),
 ('是否取得真实外部日志？','是。三个固定日志全部取得并通过SHA256，总12,905,849字节，只存服务器ATT本轮项目目录。它们是一个Bag的三个传感器视图，未做外部模型评价。'),
 ('外部标签评价单位？','一个dataset-level Bag，3种传感器不是3样本；T1003.003归并T1003，仅非穷尽来源正标签，不能逐事件赋Gold或据此完整计算FP/F1。'),
 ('是否与CAM-LDS执行/脚本依赖？','没有足够证据确认独立。来源为Atomic Red Team实例，脚本重用关系仍UNKNOWN，不能把“未发现”改写成“已经排除”。'),
 ('是否取得合格外部评价？','没有主融合外部预测。外部GTE特征/前向未执行，评价保持N/A，即使静态Bag已取得也不升级为E2。'),
 ('是否证明跨来源泛化？','不能。P0开发评价和单类单Bag准入均不足以证明216类跨来源泛化。'),
 ('需要LoRA或参数训练吗？','当前证据不支持立即启动；先处理独立数据与Mixed/未见评价、校准稳定性。无新训练授权也没有执行。'),
 ('是否有独立研究机制？','只有候选问题：语义排名保持、标签竞争和校准稳定性；尚无超越成熟基线的机制增益证据。'),
 ('论文级算法贡献？','没有。RRF、标准化、Seen校准、残差加和是成熟简单方法，本轮价值在强基线和诚实的失败定位。'),
 ('下一步怎样推进？','冻结本轮全部结果，优先建设执行依赖清楚的多技术外部Bag/步骤评价，再提出可检验的残余问题。当前停止，不扩大搜索或自动LoRA。')]
 assert len(answers)==44
 for i,(q,answer) in enumerate(answers,1):maintext+=f'### Q{i}. {q}\n\n{answer}\n\n'
 maintext+='''## 工件与复现索引

- 分数：FULL_216_SCORE_MATRIX_MANIFEST.json、score_matrices/、FROZEN_GTE_SCORES.jsonl、B3_SUPERVISED_SCORES.jsonl。
- 注册与来源：FUSION_PARAMETER_REGISTRATION.json、GENERALIZED_ZERO_SHOT_PROTOCOL.md、calibration/SELECTED_PARAMETERS.json、ALL_PARAMETER_CANDIDATES.csv。
- 正式预测与评价：FUSION_PREDICTIONS.jsonl、FUSION_RESULTS.csv、Seen/Unseen/Mixed、LONG_TAIL、MACRO_F1及PRIOR表。
- 曲线：predictions/TRADEOFF_PREDICTIONS.jsonl、SEEN_UNSEEN_TRADEOFF.csv；不得当选模候选池。
- 审计：results/FUSION_INDEPENDENT_AUDIT.json、EVALUATION_AUDIT.json、TRADEOFF_EVALUATION_AUDIT.json、reports/EVALUATOR_GOLD_ACCESS_TIMING_DISCLOSURE.json、最终FINAL_VALIDATION.json。
- 外部：external_dataset/、EXTERNAL_DATA_INSTANCE_REGISTER.csv与EXTERNAL_DATASET_QUALIFICATION.md；实际日志正文按用户要求只存服务器。
- 单文件复现入口分别为score_matrices/reconstruct_scores.py、calibration/fit_calibrators.py、fusion/predict.py、open_vocab_evaluation/evaluate_saved.py。推理/拟合有防静默覆盖守卫，不应直接在已冻结交付上重跑；复现使用新目录并保留原血缘。
- 最终哈希：manifests/DELIVERY_SHA256.json。
'''
 write('R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION_RESULTS.md',maintext)
 write('reports/2026-10-28--open-vocab-technique--r01--seen-unseen-review.md',maintext)
 write('results/RESEARCH_STATUS.json',json.dumps({'primary_status':'OPEN_VOCAB_TRADEOFF_UNRESOLVED','secondary_statuses':['OPEN_VOCAB_BASELINES_EVALUATED','UNSEEN_RANKING_RECOVERED_ON_DEV','EXTERNAL_TEST_NOT_READY','NO_SUPPORTED_NEW_ALGORITHMIC_GAIN'],'qualification':'DEVELOPMENT_ONLY','registered_H2_passes':False,'training_updates':0,'new_GPU_calls':0,'new_LLM_calls':0,'new_model_downloads':0,'main_prediction_rows':64350,'tradeoff_prediction_rows':23400,'new_algorithms_claimed':False},indent=2))
 write('README.md','''# R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION01

完整中文报告：R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION_RESULTS.md。主状态OPEN_VOCAB_TRADEOFF_UNRESOLVED，DEVELOPMENT_ONLY。11方法×7折×3旧种子×2视图，使用真实冻结分数；没有新训练/GPU/LLM。

旧资产只读继承；本项目的JSONL采用逐查询216元素数组，candidate顺序固定字典序，manifest映射NPZ完整键。B3缺失为null，排名规则明确，不把缺失当负证据。

外部原始日志按用户指定保存在服务器ATT本轮目录，本地仅代码、元数据、统计与回执。无外部真实模型预测时结果NA。流程中评估预检提前读取旧Gold的有限时序偏差已披露，fit/predict隔离独立核验通过。

最终校验和哈希见results/FINAL_VALIDATION.json与manifests/DELIVERY_SHA256.json。无需新依赖，复用已核验NumPy2.3.5/ReportLab CPU环境；未创建无必要新venv或更改系统Python。交付后停止。
''')
 print('REPORT_COMPLETE_44_QUESTIONS',len(maintext))
if __name__=='__main__':main()
