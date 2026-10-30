"""Final results after authentic frozen feature extraction and actual CPU head training."""
import csv,json,re,sys,time
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
from reports.build_domain_report import table
M=['B0','B1','B2','B3','B4','B5','B6','B7','B8','B9','B9_CONST'];A=['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']
def read(n):return list(csv.DictReader((ROOT/n).open()))
def main():
 allrows=read('results/OVERALL_RESULTS.csv');lookup={(r['method'],r['augmentation']):r for r in allrows};grouped=read('GROUPED_VALIDATION_RESULTS.csv');st=read('SEEN_UNSEEN_TECHNIQUE_RESULTS.csv');primary=read('results/FOUR_PRIMARY_DESCRIPTIVE_SUMMARY.csv');cost=read('results/TRAINING_COSTS.csv');neg=json.loads((ROOT/'results/NEGATIVE_MINING_AUDIT.json').read_text());feature=json.loads((ROOT/'embeddings/FEATURE_EXTRACTION_RECEIPT.json').read_text());diff=json.loads((ROOT/'results/B1_REEXTRACTION_DIFFERENCE.json').read_text());folds=json.loads((ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json').read_text())['folds'];audit=json.loads((ROOT/'results/TRAINED_HEADS_INDEPENDENT_AUDIT.json').read_text())
 def metrics(m,a):
  r=lookup[m,a];return f"Top1 {float(r['top1_accuracy'])*100:.2f}%，Top10 {float(r['top10_accuracy'])*100:.2f}%，MRR@10 {float(r['mrr']):.4f}"
 def subset(m,a,cat):
  rr=[r for r in st if r['method']==m and r['augmentation']==a and r['stratum']==cat];return sum(float(r['mrr'])*int(r['n_records']) for r in rr)/sum(int(r['n_records']) for r in rr)
 mt=table([{'方法':r['method'],'视图':'ONE' if r['augmentation']==A[0] else 'MULTI' if r['augmentation']==A[1] else '冻结','种子':r['seeds'],'Top1':f"{float(r['top1_accuracy'])*100:.2f}%",'Top10':f"{float(r['top10_accuracy'])*100:.2f}%",'MRR@10':f"{float(r['mrr']):.4f}",'种子SD':f"{float(r['mrr_seed_SD']):.4f}" if r['seeds']!='1' else 'NA','场景等权MRR':f"{float(r['mrr_equal_scene_mean']):.4f}"} for r in allrows],['方法','视图','种子','Top1','Top10','MRR@10','种子SD','场景等权MRR'])
 ph=table([{'假设':r['hypothesis'],'比较':r['method']+'−'+r['baseline'],'视图':'ONE' if r['augmentation']==A[0] else 'MULTI','查询加权ΔMRR':f"{float(r['MRR_delta_query_weighted']):+.4f}",'场景等权ΔMRR':f"{float(r['MRR_delta_equal_scene_mean']):+.4f}",'场景差SD':f"{float(r['MRR_delta_scene_SD']):.4f}",'场景差范围':f"[{float(r['MRR_delta_scene_min']):+.4f},{float(r['MRR_delta_scene_max']):+.4f}]",'正/负/平':f"{r['positive_scenes']}/{r['negative_scenes']}/{r['tied_scenes']}"} for r in primary],['假设','比较','视图','查询加权ΔMRR','场景等权ΔMRR','场景差SD','场景差范围','正/负/平'])
 seent=table([{'方法':r['method'],'视图':'ONE' if r['augmentation']==A[0] else 'MULTI' if r['augmentation']==A[1] else '冻结','Seen目标MRR':f"{subset(r['method'],r['augmentation'],'SEEN_GOLD_SUBSET'):.4f}",'Unseen目标MRR':f"{subset(r['method'],r['augmentation'],'UNSEEN_GOLD_SUBSET'):.4f}"} for r in allrows],['方法','视图','Seen目标MRR','Unseen目标MRR'])
 ct=table([{'方法':r['method'],'配置':r['configurations'],'参数范围':r['trainable_parameters_min']+'–'+r['trainable_parameters_max'],'更新':r['updates'],'配置CPU秒':f"{float(r['CPU_seconds_sum']):.2f}",'配置wall秒':f"{float(r['wall_seconds_config_sum']):.2f}",'checkpointMB':f"{float(r['checkpoint_bytes_sum'])/1e6:.2f}"} for r in cost],['方法','配置','参数范围','更新','配置CPU秒','配置wall秒','checkpointMB'])
 foldt=table([{'外层场景':f['heldout_scenario'],'内验证场景':f['validation_scenario'],'训练步':f['train_logical_step_count'],'验证步':f['validation_logical_step_count'],'保留步':f['heldout_logical_step_count'],'训练已见类':len(f['train_seen_techniques']),'保留未见类':len(f['heldout_unseen_techniques'])} for f in folds],['外层场景','内验证场景','训练步','验证步','保留步','训练已见类','保留未见类'])
 scene_rows=[]
 for scene in map(str,range(1,8)):
  r={'场景':scene}
  for method in M:
   mode='SHARED' if method in ['B0','B1'] else A[0];rr=[x for x in grouped if x['method']==method and x['augmentation']==mode and x['scenario']==scene and x['evaluation_partition']=='HELDOUT'];r[method]=f"{np.mean([float(x['mrr']) for x in rr]):.4f}"
  scene_rows.append(r)
 scenet=table(scene_rows,list(scene_rows[0]))
 bn=neg['by_method']['B9'];intervention=f"B9实际风险>0并降权的候选占 {bn['train_cooccurrence_risk_positive_rate']*100:.2f}%，平均权重 {bn['mean_weight']:.4f}、最小 {bn['weight_min']:.4f}。因此本方案总体接近B8；这是干预强度事实，不是已证明无增益的唯一原因。"
 limit='全部为PUBLIC_EXPOSED_DEVELOPMENT上的GROUPED_DEVELOPMENT_VALIDATION；7场景曝光、训练折重叠、原始脚本身份UNKNOWN、场景5仅2步骤。种子SD只表优化稳定性，不是独立攻击或泛化CI。'
 scope=f"授权冻结提取实际 {feature['seconds']:.2f}秒，1191条日志/知识文本的非padding Token长度合计 {feature['actual_tokens']:,}（含重复，实际执行有缓存去重），601个唯一文本、115批。GPU训练参数0，Gold读取false；峰值allocated {feature['peak_allocated_bytes']/1048576:.2f}MiB、reserved {feature['peak_reserved_bytes']/1048576:.2f}MiB，项目远端资源核验3653632bytes，低于15分钟/100万Token/200MB上限。"
 copylimit='附加服务器环境清单的scp取回受自动权限审核连接失败及超时阻断；未声称这些远端文件已下载。已成功取回核心NPZ/提取回执，并将成功命令返回的环境/结束资源核验输出如实保存在embeddings/server_manifests/RESOURCE_CHECK_STDOUT_CAPTURE.json，明确标作stdout转录。此限制不涉及模型训练、核心向量或本地审计工件缺失。'
 findings=f'''H1：投影适配相对冻结GTE在ONE的6/7场景正向、1平，MULTI的7/7正向；这是可靠的当前分组开发数值事实，收益主要集中已见类。

H2：标准多正例对比相对投影BCE，查询加权MRR分别+0.0120/+0.0227，但场景方向仅3正3负1平/3正4负；Top10反而分别下降1.54/2.02个百分点。不能称普遍优于监督分类。

H3：语义困难负例相对随机，查询加权MRR+0.0180/+0.0159，场景方向3正4负/4正3负，Top10下降1.06/1.95个百分点；只支持部分平均排序变化，尚非稳定跨场景困难负例贡献。

H4：B9相对同池B8，查询加权MRR−0.0023/+0.0011；场景等权−0.0012/−0.0004，方向2正4负1平/1正5负1平。没有稳定的可靠性增量。B9未超过B7，也未超过B3单视图。

B3单视图是已执行条件中查询加权与场景等权MRR最高的配置（{metrics('B3',A[0])}），普通线性监督是必须保留的强基线。B5 MULTI可略高于B3 MULTI，但不能据此忽略B3 ONE；两个增强协议预先固定，不据最高结果再调整训练。'''
 decision=f'''# GO / NO-GO

主状态：HARD_NEGATIVE_ADAPTATION_EVALUATED。次状态：CONTRASTIVE_MODEL_TRAINED、DOMAIN_ADAPTATION_GAIN_ON_GROUPED_DEV（限本轮轻量监督/投影开发数值）、GROUPED_TRAINING_BENCHMARK_READY、EXTERNAL_TEST_NOT_READY。不再有特征前向授权阻断；LoRA B10仍未授权/未运行。

{findings}

NO-GO：把当前可靠性权重或困难负例方案作为已验证独立算法贡献，停止追加权重/温度/负例数量调参。本轮没有HARD_NEGATIVE_INCREMENTAL_GAIN_SUPPORTED或论文级泛化结论。

GO：保留真实冻结特征、普通GTE线性分类强基线、严格场景分组及负例资格记录。所有训练头都明显损失未见技术排序：B1 Unseen目标MRR .0445，B3/B4/B5为0，B9 ONE约.0104。需要先识别弱补集负项、类别先验和未见语义几何之间的取舍；这些解释是假设，不是已隔离的因果机制。

不直接升级LoRA。当前结果不足以证明主干参数高效训练能解决未见类退化，外部标签资格和脚本依赖尚未解决。本轮不启动LoRA/DAPT/全参训练、数据下载或下一轮损失开发。'''
 write('METHOD_RESEARCH_DECISION.md',decision)
 write('DOMAIN_ADAPTATION_ERROR_ANALYSIS.md',f'''# 真实训练错误与边界

{seent}

Seen/Unseen目标Gold集合按每折训练支持定义，完整216排名不变；525全seen、305全unseen、145mixed，Seen目标670/Unseen450，mixed会在两边出现。子集P/F1将另一子集正确Gold视为当前目标FP，解释上优先MRR/Top10。

B3线性分类仅拟合训练出现类，未见类−1e6，未删除未见查询；其Unseen0符合能力边界。B4/B5虽然可对全部技术描述评分，实际Unseen也为0，说明当前训练并未保留原有未见排序。将训练补集作为弱负项、数据稀疏/领域偏移和已见类优先可能参与此退化，但本轮没有单独验证因果，不能断言日志不包含机制或所有对比学习无效。

所有训练/验证/保留指标、训练r0 gap见ALL_TRAIN_GENERALIZATION_GAPS。训练—保留差距提示过拟合/分布偏移而非唯一证明脚本记忆。固定GTE Top20条件排名、单/多标签、Token分层与来源presence均交付；条件命中不是全体准确率，来源presence不是跨源迁移。

{findings}

全216 Macro-F1@5：冻结B1约.0183；B3 ONE约.0089、B5 ONE约.0091、B7 ONE约.0103、B9 ONE约.0106。MRR升高不代表稀疏类别整体改善；Micro-F1亦独立保留，不选择性只报Top10。''')
 write('DOMAIN_ADAPTATION_ABLATION.md',f'''# 已执行消融与4主要问题

{ph}

{findings}

B6/B7/B8/B9/CONST同32未标注候选、同49152参数、同120updates；B8/B9/CONST逐步候选成员及顺序完全相同。固定.5控制ONE MRR .1712、MULTI .1715，B9 .1753/.1727，仅此不能证明风险建模优于简单降权，且B9没有超过合理B7/B8对照。

{intervention}

B8/B9依赖同折B5的训练模型挖掘，额外基础模型成本真实存在。主优化步数相同不等于完整管线计算相同；B5共用checkpoint避免重复计费，但比较时须将其依赖标明。B5与B6共享实现，区别仅全未标注补集与32随机候选；不能靠命名制造两个算法。

ONE/MULTI均每逻辑步每轮一个view，后者循环5采样，不是5倍独立监督样本。完整两个协议都报告；不同模型的增强效果不一，不选择一个模式后声称普遍增强收益。''')
 write('FALSE_NEGATIVE_RISK_AUDIT.md',f'''# 实际假负例保护与可靠性资格

已实际挖掘210份文件、930240候选记录、29070个32候选池，全部独立核验。每步全部已知Gold父ID排除，正例交集0；父子归并并保留多正例，不将T1056两个子技术当互相负例。无已声明但未归并的等价父ID；训练共现不自动视作等价。

B6随机、B7公共知识最大正例cosine、B8训练r0的同折B5排序均独立重建相等。B9/CONST和B8同池同序，risk与weight重算最大误差0；标签和共现仅来自对应fold unique train steps，无heldout/validation标签读取。标准BCE/CE补集是UNLABELED_CANDIDATE，语义候选是SEMANTIC_HARD_UNLABELED，认证真负例0。

风险>0比例：随机1.88%、语义5.08%、模型混淆10.58%。这些是训练共现风险提示，不是已知假负例比例或语义反证。{intervention}

风险代理只覆盖观测到的训练共现，无法认证未标注候选确实不发生；故不将可靠性权重当事实真值。完整来源、Gold掩码、risk和权重在NEGATIVE_SAMPLE_QUALIFICATION.csv及原始jsonl，独立证据在NEGATIVE_MINING_AUDIT。''')
 write('TRAINING_RESOURCE_REPORT.md',f'''# 实际资源与模型更新

{scope}

{ct}

378个实际训练配置，45360次Adam更新；B3仅线性头，B4–B9/CONST仅两个768×32头，均未更新GTE主干。每配置120epochs/updates、3种子、2视图协议。CPU方法时间合计{sum(float(r['CPU_seconds_sum']) for r in cost):.2f}秒，配置wall合计{sum(float(r['wall_seconds_config_sum']) for r in cost):.2f}秒；这是方法内部计时，B2共用词表和子进程启动/特征读取不完全包括，不能称全管线端到端耗时。内存为进程累计峰值；本机macOS按bytes，不是各方法增量。每配置推理延迟、参数量、权重字节、种子及损失日志保存在receipt。

CPU头消费冻结向量，无Tokenizer训练调用，训练Token记N/A；上面的Token是冻结前向的输入长度计数，不能冒充反向训练Token。GPU0显存15%、CPU2线程、batch8；本地CPU头亦2线程、总控制器5400秒/2GB监测。无GPU训练/Gold上传/新包/模型下载/LLM。

{copylimit}''')
 # Update45answers from the unchanged CPU-only report, preserving independent historical conclusions.
 old=(ROOT/'reports/CPU_ONLY_SNAPSHOT/R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING_RESULTS.md').read_text();qa=re.findall(r'^### (\d+)\. ([^\n]+)\n\n(.*?)(?=\n### |\n## |\Z)',old,re.M|re.S);assert len(qa)==45
 changes={10:'是，B3冻结GTE特征线性分类器42配置已真实训练；'+metrics('B3',A[0])+'（ONE，3种子均值）。',11:'是，B4及B5–B9/CONST的两个768×32投影头均实际更新，每个49152参数；不称GTE主干微调。',12:'B2/B3的W和b、B4–B9/CONST的W_L/W_T实际更新；全部378配置初终hash不同、参数L2变化已独立复算。GTE权重始终冻结且前后SHA一致。',13:'是，B5标准多正例平均log-softmax全216训练完成42配置；不是只取第一个正例。B6同loss但32随机未标注候选，代码共享/差异明确。',14:'是，共378checkpoint、45360更新，336新头及B2旧42均实际保存；独立重载全部216排名和分数一致，最大差0。',15:'是，B6/B7/B8/B9/CONST的210负例文件、930240记录、29070池均真实保存并独立复算。',16:'是，B7只用公共知识和训练正标签，B8只用同fold train训练的B5在train r0评分；B9共现只按unique train steps，不读保留/验证Gold。',17:'没有称其为事实不存在；实际BCE/CE确实把补集用于弱负项，这个闭世界监督假设可能影响未见语义，但当前没有隔离因果。认证反例0。',18:'已实际验证全部Gold屏蔽、父子规范化、32候选唯一、共现risk/weight重算。所有池正例交集0；没有伪造人工互斥证据。',19:'B7对B6查询加权ΔMRR ONE +.0180、MULTI +.0159，但场景方向3正4负/4正3负，Top10下降；未支持稳定跨场景独立贡献。',20:'B8相对B7的ONE/MULTI MRR均更低（.1775/.1716 对 .1877/.1878）；模型混淆未优于公共知识语义候选。',21:'不支持。B9相对同池B8 ONE ΔMRR−.0023、MULTI+.0011；场景等权均为负，没有稳定额外价值。',22:'全部20方法/视图条件见主表，3种子/7折原值均保存。ONE：B1 '+metrics('B1','SHARED')+'；B3 '+metrics('B3',A[0])+'；B5 '+metrics('B5',A[0])+'；B7 '+metrics('B7',A[0])+'；B9 '+metrics('B9',A[0])+'。',23:'在本轮既定条件中B3 ONE查询加权和场景等权MRR最高。普通GTE线性分类器是强基线；不能因B5 MULTI超过B3 MULTI就忽略B3 ONE。',24:'主要增益集中已见技术。B3 ONE Seen目标MRR .2942、Unseen0；开放描述投影B4/B5也Unseen0，未形成未见标签泛化收益。',25:'B1 Unseen目标MRR .0445；B3/B4/B5为0；B7 ONE .00046、B9 ONE .01039，均明显低于冻结GTE。450个Unseen目标查询全部保留，未删候选。',26:'单/多标签每方法每折已实测并交付3472个分层条件；不能由总体涨分推定所有标签/类别改善。主MRR提高的同时，训练头全216 Macro-F1通常低于B1。',27:'训练r0/验证/保留差距已保存于ALL_TRAIN_GENERALIZATION_GAPS，B2已知42/42训练优于保留；这与过拟合/分布偏移一致，确切脚本身份仍UNKNOWN，不能单独证明场景记忆。',28:'没有稳定超过。B3 ONE MRR .2022，高于B5 ONE .1699、B7 ONE .1877、B9 ONE .1753；MULTI排序不同也不足以声称普遍优势。',29:'训练的B3/B4/B5等在当前分组开发总体MRR上超过同特征B1；然而Unseen目标退化，不等于领域语义泛化成立。',30:'大部分训练头在相同RAW上超过B0总体MRR；全表保留Top1/10、Macro-F1与未见负结果，不与历史不同窗口成绩作无条件增益。',31:'B6/B7/B8/B9同32负候选、49152参数、120主更新；B8/B9/CONST同池。B8/B9还需B5依赖模型训练/挖掘，完整管线成本更多，已单列；不把主更新相等当总预算相等。',32:'全部9个受训方法各7折×3固定种子×2视图，378配置。种子SD/逐值完整保存，种子不是独立攻击重复。',33:'有训练—保留差距与未见技术退化，支持过拟合/分布偏移风险；训练收敛/重载一致不证明泛化。全部使用最终120更新，无外层早停或调参。',38:'没有独立跨平台/跨源迁移证据。来源presence分层和外部元数据不是迁移实验，外部实测样本0。',39:'没有GPU参数训练授权。此次新授权仅冻结特征提取和随后本地CPU头训练；该范围已执行，LoRA/GPU训练仍NA。',40:'本地CPU实际完成B2–B9及固定权重控制：378配置、45360更新、54600外层保存预测（含1950冻结基线记录）。',41:'没有。B9未稳定超过同池B8、未超过B7或合理线性基线，不能将标准困难负例或共现权重称独立创新。',42:'目前不建议跳过诊断直接LoRA。先理解未见技术退化、补集弱负项和类别先验的作用，补外部资格；本轮未获GPU训练授权也不自动申请扩张。',43:'支持继续把轻量领域适配作为开发方向，但当前困难负例可靠性机制NO-GO，不作为已建立新算法立项依据；普通监督与未见标签权衡是更实际的问题。',44:'没有。7曝光场景、未知脚本依赖、稀疏标签、外部0样本，不具论文级独立泛化结论。',45:'首先解决训练后已见收益与未见语义退化的取舍，明确未标注补集资格并获取正确单位的独立数据；这些待检验问题不触发本轮继续叠加损失、权重搜索或新训练。'}
 answers='\n\n'.join(f'### {i}. {q}\n\n{changes.get(int(i),a.strip())}' for i,q,a in qa)
 report=f'''---
type: results-report
date: 2026-10-28
experiment_line: domain_adaptive_contrastive_learning
round: 01
purpose: actual-head-training-and-hard-negative-evaluation
status: completed_authorized_cpu_heads
source_artifacts: [reports/analysis-output/analysis-report.md, reports/analysis-output/stats-appendix.md, reports/analysis-output/figure-catalog.md, reports/analysis-output/provenance.json]
linked_experiments: [manifests/TRAINING_PROTOCOL.json, GROUPED_TRAIN_VALIDATION_SPLITS.json]
linked_results: [results/OVERALL_RESULTS.csv, results/FOUR_PRIMARY_DESCRIPTIVE_SUMMARY.csv]
---
# ATT&CK领域适配 / Round 01 / 真实训练与困难负例评价 / 2026-10-28

## 执行结论

主状态 **HARD_NEGATIVE_ADAPTATION_EVALUATED**。已完成378个真实CPU训练配置、45360次Adam更新、全部checkpoint保存和独立重载；B0/B1冻结、B2监督TF-IDF、B3 GTE线性、B4投影BCE、B5标准对比、B6随机、B7语义、B8训练混淆、B9风险权重及CONST固定权重控制全部实测。GTE主干始终冻结，LoRA B10未授权未执行。

**普通GTE线性分类器是当前MRR最强基线；可靠性困难负例未获得稳定独立增益。** ONE视图3种子均值：B1 MRR .0582，B3 .2022，B5 .1699，B7 .1877，B9 .1753。MULTI结果亦完整保留。训练收益主要集中已见技术；Unseen目标MRR由冻结GTE .0445降到B3/B4/B5的0，B9 ONE也仅.0104，不能宣称开放类别语义泛化改善。

独立审计通过：336新增头及42既有模型、全部排序/参数血缘；210负例文件930240记录；1106评价条件、3472分层条件与56主要场景差值。外部TEST仍未就绪，本轮结束后停止，不增加损失/LoRA或下载数据。

## 身份、数据与监督资格

P0=PUBLIC_EXPOSED_DEVELOPMENT，195逻辑步骤、975查询、7场景、34执行标识、216候选、79出现父类；P1/P2仍RELATED_DEVELOPMENT_DATA。作者步骤标签可作监督，但不认证每项机制完整出现在日志中，也不把未标注技术视为已证伪。

多标签口径已解决：原始子ID集合295/975，父ID集合285/975=57/195步骤。6-33和6-34的T1056.004/T1056.001各归一T1056，共10采样差额；先前295作父技术统计是报告错误，本轮纠正并保留旧原文。27类仅1逻辑步骤、13类2步。195监督单位不等于195个独立攻击执行。

输入复用已清洗RAW≤2000 UTF8 bytes，公共K2_16_1知识≤1000 bytes，全部模型相同事实/216候选。B0继承精确匹配输入知识的字符检索；B1用本次真实768维特征矩阵点积重算，保证与训练头同特征。相较旧B1，{diff['changed_top10_order_queries']}条Top10顺序变化、{diff['changed_top10_membership_queries']}条成员变化，MRR .05832275→.05818600、Top10 .20102564→.20000000；旧预测保留inherited/CPU_ONLY_B1_PREDICTIONS.jsonl。FP16不同批次组织是合理数值解释，未隔离验证，不据Gold选择版本。不能与历史不同窗口27.79%/30.26%直接比较。

## 分组与脚本泄漏限制

{foldt}

LOSO外层每场景一次，内验证循环下一场景。5采样同逻辑步骤同划分；1-54/2-5/3-49的规范化完整cron窗口交叠按步骤purge，不把背景日志相同认证为同一攻击脚本。真实跨场景script身份UNKNOWN，scenario只是保守代理；不能声称所有脚本泄漏已消除。折4内验证仅2步，全部采用预登记固定参数/120更新/最终checkpoint，无保留组调参或早停。

## 训练实现与参数

B2是train-r0拟合字符3/4/5gram、min_df2/max2048、smoothed IDF/sublinear TF/L2的OVR logistic；两增强模式共用词表。B3用768维冻结GTE训练同类线性头，二者只拟合训练已见标签，未见类−1e6保留216排名。B2/B3 Adam lr.03、L2 .001。

B4–B9/CONST双独立768×32头、L2归一化、余弦/温度.1，49152参数，Adam lr.005、L2 .001；不是GTE主干微调。B4逐行正/未标注集合平衡sigmoid BCE；B5全216多正例平均负log-softmax。B6与B5同代码，只把未标注补集分母换为32随机候选。B7按冻结知识与训练正技术最大cosine取32；B8按只训练本fold的B5在训练r0预测取32；B9与B8同池并按本fold unique-step共现risk设w=1−.75risk；CONST同池固定w=.5。

ONE固定r0；MULTI循环(epoch+seed)%5。各逻辑步每轮一个view、全步骤batch、120updates、种子17/42/73，不把975当975独立监督对象。训练器只读对应train Gold，验证/保留input与reference隔离；特征提取无Gold。所有参数更新/hash/L2与独立重载评分检查通过，3项有限差分/正例保护测试通过；没有增加超参搜索。

## 全部实际结果

{mt}

所有Top1/5/10、Precision/Recall、Micro/Macro F1@5均在统一表和3472分层结果中；报告主MRR与重要辅助Top10，保留失败与类别平衡退化。下表是预登记ONE视图逐场景MRR，完整MULTI/seed值见GROUPED_VALIDATION_RESULTS：

{scenet}

## 4项主要问题与统计解释

{ph}

{findings}

{limit} 当前不计算确认性p值或975独立样本bootstrap，不重复292项检验。报告查询加权、等权场景、seed mean/SD、7场景差值SD/范围/方向；seed平均不增加独立攻击数。场景5只有2步，单独保留支持量。主指标预先定MRR，Top10下降与Macro-F1退化不能省略。

## 已见、未见与错误归因

{seent}

525全seen、305全unseen、145mixed；目标子集Seen670/Unseen450，mixed可重复进入两边。只限制Gold集合，候选仍216；子集P/F1会把另一子集Gold算成当前目标FP，优先解释MRR/Top10。B3闭合标签能力界限明确；B4/B5可给所有描述打分但实际Unseen0，不能把形式上的可打分能力当开放泛化。

训练—保留gap在ALL_TRAIN_GENERALIZATION_GAPS，B2额外有实际checkpoint训练r0重载诊断。loss下降/来源一致不等于语义泛化。弱补集负项、类别先验、数据稀疏和域偏移可能参与未见退化，但未由本轮单独隔离；不能从错分反推证据不存在。源presence/Token/单多标签分层与固定GTE Top20条件排序均交付，不将其当跨平台迁移或总体准确率。

全216 Macro-F1@5冻结B1约.0183，高于B3 ONE .0089、B5 ONE .0091、B9 ONE .0106；Micro-F1另保留。因此训练不等于所有类别指标改善。

## 困难负例资格与可靠性干预

930240记录、29070池，每方法186048记录/5814池。随机RNG、知识近邻、同fold B5训练r0排序均独立复算一致；B8/B9/CONST成员与顺序相同，risk/weight最大误差0；全部Gold交集0、认证真负例0。不从同义词猜ID，不将共现技术自动合并成等价。

随机/语义/混淆的训练共现risk>0比例分别1.88%/5.08%/10.58%，这些不是已认证假负例率。{intervention} 固定权重控制也真实完成，不能把B9略高于CONST而未超过B7/B8说成独立机制成立。

B8/B9需要B5训练依赖，额外模型/挖掘成本不隐藏；复用同B5避免重复计费不代表整个管线与B7等计算。候选数、主更新/参数相同是受控部分，其他成本另列。

## 图与训练曲线

![全部MRR]({ROOT}/reports/analysis-output/figures/figure04_all_trained_mrr.png)

图4：两固定增强协议的全部MRR，误差条是3种子SD；普通线性监督强于更复杂方法的部分条件，不能通过只挑某模式制造对比学习优势。

![已见未见]({ROOT}/reports/analysis-output/figures/figure05_trained_seen_unseen.png)

图5：ONE预登记协议，训练头的已见收益伴随未见目标退化；混合样本在两个目标子集可重复，不是互斥测试集。

![可靠性差值]({ROOT}/reports/analysis-output/figures/figure06_reliability_scene_deltas.png)

图6：同池B9−B8逐场景seed均值，方向不一致、场景等权均为负；没有稳定额外价值。

![真实训练曲线]({ROOT}/reports/analysis-output/figures/figure07_contrastive_training_loss.png)

图7：seed42的真实训练loss趋势，7重叠训练折描述均值。B5/B7/B9分母和权重不同，loss绝对值不可用来选优；120更新最终checkpoint固定，没有早停。

## 成本、权限与失败记录

{scope}

{ct}

378checkpoint共约{sum(float(r['checkpoint_bytes_sum']) for r in cost)/1e6:.2f}MB，45360更新；CPU方法内部合计{sum(float(r['CPU_seconds_sum']) for r in cost):.2f}秒，配置wall合计{sum(float(r['wall_seconds_config_sum']) for r in cost):.2f}秒，不完整覆盖B2共用向量器/子进程启动/特征读取，不能称整个研究端到端耗时。内存为进程峰值、非每方法增量；每配置推理时间/参数/种子/文件字节完整记录。本地CPU头消费向量，无Tokenizer，反向训练Token记N/A；冻结前向Token另计。

用户仅授权新项目同名venv、只读固定模型/依赖、上传4149bytes冻结代码并取向量；未上传Gold/新日志。没有新包/模型下载、LLM、GPU参数训练、LoRA、DAPT/全参微调。原训练protocol的pending权限字段是授权前登记，不改历史哈希，当前FEATURE_EXTRACTION_AUTHORIZATION与实际回执为准。

{copylimit}

## 外部数据与独立性

OTRF/Security-Datasets固定commit d9d40ef123d2c87d5d3df28c96bcab4f0faccc87，root LICENSE和README许可表述不一致；本地旧计划25050bytes与官方blob25051bytes不同，APT29派生副本已曝光，名称→父ID及日志对应/独立性未齐。不能当全新外部TEST，也未纳入训练。

Splunk/attack_data固定commit 671f9f5b065f03a5502db07c20f1fe3f620d29d9；具体YAML cc9b25e1-efc9-11eb-926b-550bf0943fbb声明T1003.003，归T1003在216候选中。3个日志LFS指针共12905849bytes，仅元数据未下载；标签是dataset-level Bag，不可逐event赋标签，一类Bag也不证明216类泛化。原始链接/许可证与Git blob核验在EXTERNAL_DATASET_QUALIFICATION。外部训练/评价0、指标NA。

## 决策、信念更新与下一步

当前轻量适配确有分组开发MRR收益，但以已见类别为主；“通用表示经训练自然获得更好的领域开放泛化”这一前提不受本轮数据支持。普通GTE线性模型很强，标准对比或困难负例不能只比冻结模型。可靠性同池控制没有稳定增量，当前方案NO-GO作为独立算法贡献。

保留特征、checkpoint、分组协议及普通监督基线；下一阶段若另行立项，优先区分弱负例假设、类别先验和未见语义退化，并补真正独立、标签单位正确的数据。不能凭当前结果自动启动LoRA、更多损失/权重搜索或外部日志下载。本轮授权范围内工作完成后停止。

## 45项逐条回答

{answers}

## 复现与交付索引

新最终汇总results/OVERALL_RESULTS、4主问题FOUR_PRIMARY_DESCRIPTIVE_SUMMARY、全部GROUPED_VALIDATION/SEEN_UNSEEN、54600外层预测及每配置原始输出。378真实checkpoint/receipt、930240负候选原jsonl/CSV、特征/输入哈希、梯度/训练/负例/独立评价审计、外部元数据、资源输出转录与授权历史均保存。最终哈希与状态见results/FINAL_VALIDATION.json、manifests/DELIVERY_SHA256.json。CPU-only阶段保留reports/CPU_ONLY_SNAPSHOT；冻结协议/旧1029资产不改，受限归档/PwnKit35–37/CONV-A01未读。
'''
 write('R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING_RESULTS.md',report)
 ao='reports/analysis-output/'
 write(ao+'analysis-report.md',f'''# 完整训练严格分析

固定问题：H1投影、H2标准对比、H3语义困难、H4可靠性。真实378配置、20方法/模式均值、54600外层保存预测，V1逐行重算。

{mt}

{ph}

{findings}

{seent}

{limit}

## Claim candidates

- 轻量监督/投影提升当前分组MRR。来源全部模型表/4主假设；允许称开发点估计收益，禁止独立泛化/新算法；未见退化和类别先验混杂，keep but limit。
- 语义困难负例稳定改善。MRR均值上升但场景方向不一致、Top10下降，weaken；不宣称跨场景稳定机制。
- 可靠性有独立增量。H4同池ONE负、MULTI微正且场景等权均负，discard当前贡献主张；不推广为所有可靠性思想无效。
- 训练改善未见语义。Unseen退化，discard；解释可能涉及弱补集、先验、域偏移，未隔离因果。
- 普通线性监督是强基线。B3 ONE最高总体/场景MRR，keep；其未见0、不是开放类别解法。

来源含完整原始候选池与权重，未根据新结果重选样本/超参/最终epoch。''')
 write(ao+'stats-appendix.md',f'''# 完整训练统计附录

{ph}

主MRR、重要辅助Top10预登记；3种子固定17/42/73，各条件7fold、195逻辑步骤、975相关查询。先在场景内取seed均值描述差，再列7场景均值/SD/范围/正负方向，不做确认性p或975独立bootstrap。{limit}

查询加权与场景等权两者报告，H4 MULTI在查询权重略正而场景等权负，不能只报有利加权方式。两个增强协议都固定120更新，方法内参数/候选受控；B8/B9的B5依赖训练/挖掘成本额外列明。loss值跨不同分母/权重不直接可比。

Seen/Unseen使用对应fold train标签，混合查询可重复；Gold子集P/F1有目标外Gold被算FP的解释限制，优先MRR/Top10。最小场景2步与未知脚本依赖仍限制一般化。独立审计3472分层、1106完整条件和56主要差值一致；工程一致不认证语义可观察性。''')
 write(ao+'figure-catalog.md','''# 完整训练图解释

figure04_all_trained_mrr.pdf/svg/png：全部20方法/视图条件MRR，冻结单柱，训练双柱mean±3seedSD；误差不表示独立泛化CI。目的：检查普通监督强基线是否被忽略；需结合未见/宏平均指标，不能只挑一个视图最优。

figure05_trained_seen_unseen.pdf/svg/png：ONE协议同216排名Seen/Unseen Gold目标，670/450查询含145mixed重叠。目的：检查训练是否保持未见排序。目标子集非互斥样本，P/F1定义需另说明；图用MRR。

figure06_reliability_scene_deltas.pdf/svg/png：7场景B9−B8，ONE/MULTI均为seed均值，无推断误差条。目的：检查同池风险权重是否有一致增量。多数场景负或平，不选查询加权微正解释为稳定贡献。

figure07_contrastive_training_loss.pdf/svg/png：seed42、ONE协议，B5/B7/B9在7重叠训练折上的loss均值曲线。仅看优化趋势，不比较不同目标loss绝对高低，不把下降当泛化。旧figure01–03为CPU监督阶段历史图，最终结论以04–07及完整表为准。''')
 names=['TRAINING_BASELINE_PREDICTIONS.jsonl','results/OVERALL_RESULTS.csv','GROUPED_TRAIN_VALIDATION_SPLITS.json','data/P0_REFERENCE.jsonl','manifests/TRAINING_PROTOCOL.json','manifests/FEATURE_EXTRACTION_AUTHORIZATION.json','embeddings/FROZEN_GTE_FEATURES.npz','embeddings/FEATURE_EXTRACTION_RECEIPT.json','results/TRAINED_HEADS_INDEPENDENT_AUDIT.json','results/NEGATIVE_MINING_AUDIT.json','results/FINAL_EVALUATION_INDEPENDENT_AUDIT.json','evaluation/evaluate_saved.py']
 dump(ao+'provenance.json',{'sources':[{'path':str(ROOT/n),'sha256':sha(ROOT/n)} for n in names],'primary_metric':'MRR@10','new_GPU_experiments':1,'GPU_experiment_type':'FROZEN_FEATURE_EXTRACTION_NOT_PARAMETER_TRAINING','Gold_GPU_server_upload':False,'actual_CPU_configurations':378,'GTE_backbone_updated':False,'real_contrastive_heads_trained':True,'new_LLM_calls':0,'external_test_samples':0})
 # Historical request remains readable, but current grant is explicit.
 request=ROOT/'GPU_TRAINING_AUTHORIZATION_REQUEST.md';orig=(ROOT/'reports/CPU_ONLY_SNAPSHOT/GPU_TRAINING_AUTHORIZATION_REQUEST.md').read_text();request.write_text('> 当前状态：用户已批准最小冻结特征提取及本地CPU训练，已执行完成。该授权不含GPU参数训练或LoRA。以下保留原请求正文。\n\n'+orig)
 write('README.md','''# R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING01

最终主状态HARD_NEGATIVE_ADAPTATION_EVALUATED。378个真实本地CPU配置、45360更新、54600外层保存预测、930240负候选；B3–B9已执行，不再等待特征授权。LoRA B10/GPU参数训练仍未授权未执行，外部TEST_NOT_READY。

入口R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING_RESULTS.md；最终生成器reports/finalize_trained_report.py。reports/build_domain_report.py是CPU-only阶段历史生成器，不应重跑来覆盖完整报告；该阶段文档保留reports/CPU_ONLY_SNAPSHOT。

固定原始协议中的pending字段是授权前历史，不修改已签入checkpoint的哈希。当前授权见manifests/FEATURE_EXTRACTION_AUTHORIZATION.json，真实features和receipt在embeddings，训练源码与checkpoint独立审计通过。GPU只做冻结前向，Gold始终本地；未下载模型/日志或调用LLM。

同批特征重算B1与旧B1有49条Top10顺序差，旧版本保留inherited/CPU_ONLY_B1_PREDICTIONS，原因仍为未隔离的数值解释；所有训练对照使用本次同特征B1，不据Gold选版本。

普通GTE线性监督最强，可靠性权重无稳定增量、未见目标退化；不称新独立算法或论文级泛化。最终完整性见results/FINAL_VALIDATION.json及manifests/DELIVERY_SHA256.json。''')
 dump('results/RESEARCH_STATUS.json',{'main_status':'HARD_NEGATIVE_ADAPTATION_EVALUATED','secondary':['CONTRASTIVE_MODEL_TRAINED','DOMAIN_ADAPTATION_GAIN_ON_GROUPED_DEV_LIMITED_TO_CURRENT_LIGHTWEIGHT_DEV','GROUPED_TRAINING_BENCHMARK_READY','EXTERNAL_TEST_NOT_READY'],'trained_configurations':378,'optimizer_updates':45360,'GTE_heads_trained':True,'hard_negative_incremental_innovation_supported':False,'new_feature_extraction_authorized':True,'new_GPU_training_authorized':False,'GTE_backbone_updated':False,'LoRA_B10':'NA_NOT_AUTHORIZED_NOT_RUN','new_LLM_calls':0,'external_test_samples':0,'questions_answered':45,'automatic_review_limit':'additional remote control-manifest scp failed; core NPZ and receipt acquired, resource stdout captured'})
 dump('experiments/EXPERIMENT_MATRIX_STATUS.json',{'methods':[{ 'method':m,'status':'FROZEN_SAME_INPUT_BASELINE' if m in ['B0','B1'] else 'ACTUALLY_TRAINED42CONFIGURATIONS','parameter_updates':m not in ['B0','B1']} for m in M]+[{'method':'B10_GTE_LoRA','status':'NA_GPU_TRAINING_NOT_AUTHORIZED','parameter_updates':False}]})
 print('Final trained report,45answers,strict bundle,status andresource scope updated')
if __name__=='__main__':main()
