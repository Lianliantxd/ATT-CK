"""Evidence-first report of executed grouped training; unrun models remain N/A."""
import csv,json,re,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def rows(n):return list(csv.DictReader((ROOT/n).open()))
def table(rr,cols):return '| '+' | '.join(cols)+' |\n| '+' | '.join('---' for _ in cols)+' |\n'+'\n'.join('| '+' | '.join(str(r.get(k,'NA')) for k in cols)+' |' for r in rr)
def main():
 results=rows('results/OVERALL_RESULTS.csv');lookup={(r['method'],r['augmentation']):r for r in results};folds=json.loads((ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json').read_text())['folds'];cost=rows('results/TRAINING_COSTS.csv');strata=rows('SEEN_UNSEEN_TECHNIQUE_RESULTS.csv');g=rows('GROUPED_VALIDATION_RESULTS.csv');gaps=rows('results/B2_TRAIN_GENERALIZATION_GAP.csv');has_heads=any(r['method']=='B5' for r in results)
 def summary(m,a):
  x=lookup[m,a];return f"Top1={float(x['top1_accuracy'])*100:.2f}%，Top10={float(x['top10_accuracy'])*100:.2f}%，MRR@10={float(x['mrr']):.4f}，等权场景MRR={float(x['mrr_equal_scene_mean']):.4f}"
 def subset(m,a,category):
  rr=[r for r in strata if r['method']==m and r['augmentation']==a and r['stratum']==category];den=sum(int(r['n_records']) for r in rr);return sum(float(r['mrr'])*int(r['n_records']) for r in rr)/den if den else None
 main_table=table([{'方法':x['method'],'采样':x['augmentation'],'种子':x['seeds'],'Top1':f"{float(x['top1_accuracy'])*100:.2f}%",'Top10':f"{float(x['top10_accuracy'])*100:.2f}%",'MRR@10':f"{float(x['mrr']):.4f}",'MRR种子SD':f"{float(x['mrr_seed_SD']):.5f}" if x['seeds']!='1' else 'NA冻结','场景等权MRR':f"{float(x['mrr_equal_scene_mean']):.4f}"} for x in results],['方法','采样','种子','Top1','Top10','MRR@10','MRR种子SD','场景等权MRR'])
 foldtable=table([{'保留场景':f['heldout_scenario'],'内验证场景':f['validation_scenario'],'训练步骤':f['train_logical_step_count'],'验证步骤':f['validation_logical_step_count'],'保留步骤':f['heldout_logical_step_count'],'训练出现类':len(f['train_seen_techniques']),'保留未见类':len(f['heldout_unseen_techniques'])} for f in folds],['保留场景','内验证场景','训练步骤','验证步骤','保留步骤','训练出现类','保留未见类'])
 per_scene=[]
 for scene in map(str,range(1,8)):
  out={'场景':scene}
  for m,a in [('B0','SHARED'),('B1','SHARED'),('B2','ONE_VIEW_PER_STEP'),('B2','MULTI_VIEW_AUGMENTATION')]:out[m+'_'+('ONE' if a=='ONE_VIEW_PER_STEP' else 'MULTI' if a=='MULTI_VIEW_AUGMENTATION' else 'FROZEN')]=f"{np.mean([float(r['mrr']) for r in g if r['method']==m and r['augmentation']==a and r['scenario']==scene and r['evaluation_partition']=='HELDOUT']):.4f}"
  per_scene.append(out)
 scenetable=table(per_scene,list(per_scene[0]));seentable=table([{'方法':m,'采样':a,'Seen目标MRR':f"{subset(m,a,'SEEN_GOLD_SUBSET'):.4f}",'Unseen目标MRR':f"{subset(m,a,'UNSEEN_GOLD_SUBSET'):.4f}"} for m,a in [('B0','SHARED'),('B1','SHARED'),('B2','ONE_VIEW_PER_STEP'),('B2','MULTI_VIEW_AUGMENTATION')]],['方法','采样','Seen目标MRR','Unseen目标MRR'])
 delta_one=float(lookup['B2','ONE_VIEW_PER_STEP']['mrr'])-float(lookup['B1','SHARED']['mrr']);delta_multi=float(lookup['B2','MULTI_VIEW_AUGMENTATION']['mrr'])-float(lookup['B1','SHARED']['mrr'])
 main_state='SUPERVISED_BASELINES_TRAINED' if not has_heads else 'HARD_NEGATIVE_ADAPTATION_EVALUATED';blocked='B3–B9尚未执行：本地和旧项目未保存真实768维GTE日志/技术向量；216维候选相似度不是向量。新冻结前向、服务器新项目写入仍待明确授权，未上传Gold、未启动GPU训练。' if not has_heads else 'B3–B9已执行，需结合实际逐折结果解释。'
 write('METHOD_RESEARCH_DECISION.md',f'''# 科研GO/NO-GO

主状态：{main_state}。次状态：GROUPED_TRAINING_BENCHMARK_READY、TRAINING_RESOURCE_AUTHORIZATION_BLOCKED、EXTERNAL_TEST_NOT_READY。

普通监督TF-IDF在曝光LOSO开发评价中有数值收益：单视图相对同输入冻结GTE MRR差{delta_one:+.4f}，多视图差{delta_multi:+.4f}。只有42个B2配置真实训练，不能把它们称为GTE投影、对比学习或困难负例模型。未见父技术无法靠封闭分类器有效识别，42/42配置训练优于保留，需考虑有限类记忆、过拟合/分布偏移；这些证据不能单独证明脚本记忆。

{blocked}

NO-GO：当前没有证据支持可靠性困难负例算法创新，也没有足够证据判断B9相对B7/B8的效果；未运行不等于无效。禁止使用CONTRASTIVE_MODEL_TRAINED或NO_SUPPORTED_DOMAIN_ADAPTATION_GAIN概括未执行的主要机制。

条件GO：具体最小向量提取请求已经冻结，可在独立明确授权后取得真实GTE特征，再按既定预算在本地CPU运行B3–B9。LoRA/GPU训练和Gold上传需额外独立授权，目前无必要仅凭B2增益直接启动LoRA。保持4主要假设、不追加参数搜索。本轮不自动下载外部日志，不启动DAPT/全参训练。''')
 write('DOMAIN_ADAPTATION_ERROR_ANALYSIS.md',f'''# 已执行方法的错误与限制

{main_table}

B2普通监督训练改善已见标签排名，但Unseen目标MRR为0；未见类别仍保留全216排名，只赋-1e6固定低分，未删除样本。错误主要可确认到训练类别支持不足/封闭标签能力边界，不能从步骤标签反推日志机制缺失或技术不存在。

{seentable}

全seen525查询、全unseen305、mixed145；Seen目标子集670、Unseen450，145混合查询出现在两边。只限制Gold集合，候选不变。子集MRR/Top10是相应目标检索能力；子集P/F1会将另一子集Gold视作当前目标的FP，不应直接解释为通常的seen/unseen分类F1。

42/42 B2配置有训练—保留差距，详见B2_TRAIN_GENERALIZATION_GAP。ONE等权折×种子训练MRR约.7167而heldout约.0838；MULTI约.6733对.0782。train为r0、heldout含5相关采样，不能把差距唯一归因为场景或脚本记忆。源类型分层仅表示当前日志含该来源，不是只用该源或跨平台迁移实验；未认证跨源泛化。

困难候选诊断在所有方法相同的冻结GTE Top20中重排，仅对候选含Gold的查询评价；这是条件分析而非全体新Top10。训练内负例挖掘未运行前不生成事后Gold负例。''')
 write('DOMAIN_ADAPTATION_ABLATION.md',f'''# 已执行消融与待执行机制

B2固定r0与5视图循环增强均120updates、每逻辑步每轮一view、相同词表/IDF、相同参数量和3种子。单视图{summary('B2','ONE_VIEW_PER_STEP')}；多视图{summary('B2','MULTI_VIEW_AUGMENTATION')}。两者差异不是5倍独立监督样本或更多优化更新；本轮多视图没有优于单视图。其原因尚未由单一对比隔离。

B4vsB1、B5vsB4、B7vsB6、B9vsB8为4预注册主要MRR问题，不重复292项探索检验。当前资源阻断项为N/A。B6/B7/B8同32未标注候选，B9复用B8池并有固定.5权重控制；这些是已编写且梯度检查的实验代码，尚非训练结果。

B8/B9未来还需B5训练checkpoint，额外挖掘/基础训练总成本不可隐瞒；只匹配主优化步骤不代表总计算相等。可靠性共现必须只来自本折unique train steps，不允许全P0标签共现。''')
 ao='reports/analysis-output/'
 write(ao+'analysis-report.md',f'''# 严格分析：已执行监督基线

主要问题：对同RAW输入、K2知识、216候选、保守场景分组，真实训练的普通监督模型是否比冻结检索强？对比学习/困难负例4主要问题因缺真实向量与新前向授权暂不能检验。

{main_table}

{scenetable}

{seentable}

每个受训条件7场景、3种子、975查询、195逻辑步骤。主指标MRR@10，重要辅助Top10，均用冻结V1独立从保存预测计算。种子平均不增加独立场景数；总体按查询加权与等权场景两者都报告，防止场景5仅2步骤产生误导。

## Claim candidates

- Claim：B2优于同输入冻结GTE的开发点估计。来源OVERALL_RESULTS与分折表；允许限定“曝光场景分组开发，普通监督基线有数值增益”；禁止“新语义算法/独立泛化成立”；脚本身份UNKNOWN，7依赖场景，需外部资格；keep but limit。
- Claim：多视图增强更好。真实B2不支持；禁止靠训练样本变多预设收益；discard。
- Claim：B2学会未见技术。Unseen目标MRR0，不支持；保留全216与未见查询；discard。
- Claim：训练—保留差距提示风险。来源42checkpoint重载，允许“与过拟合/分布偏移一致”，禁止“唯一证明脚本记忆”；weaken。
- Claim：可靠性困难负例有独立价值。当前没有真实B3–B9结果，不能评价或借B2替代；defer resource authorization。
''')
 write(ao+'stats-appendix.md','''# 统计附录

预先固定H1投影vs冻结、H2标准对比vs普通投影、H3语义vs随机负例、H4可靠性vs模型困难负例；主指标MRR@10，Top10辅助。每个场景内5采样归属同195逻辑步骤；3种子只表计算稳定性，不是独立攻击重复。7场景已经曝光、外层训练折重叠、确切脚本身份未知，当前不进行确认性p值或975样本独立bootstrap，也不重做292检验。

已执行B2报告每折/每种子原值、种子均值与SD、场景等权与查询加权，以及效应方向/范围。模型确定性冻结基线不捏造seed SD。场景5只有2步骤，内验证折4也仅2步骤；固定120更新，无验证选最优checkpoint，不做保留组调参。

Seen/Unseen以本折实际训练父标签定义；混合标签查询进入两个目标Gold子集，候选始终216。子集P/F1的目标定义与普通多标签分类不同，优先解释MRR/Top10。原始ID多标签295与父ID多标签285不可混用。工程边界/重载正确不证明机制可观察性或外部泛化。''')
 write(ao+'figure-catalog.md','''# 实际图及解释

figure01_scenario_mrr.pdf/svg/png：B0/B1/B2单/多视图逐保留场景MRR，种子均值、描述柱，无置信区间。场景差异与训练已见类别不同，不能把7柱当独立外部重复。需要结合场景支持量和seen/unseen表解释。

figure02_seen_unseen.pdf/svg/png：同216排名上Seen/Unseen Gold目标子集MRR。混合145查询可在两组出现，不能把两组视为互斥样本。B2封闭分类器未见类低分，图说明能力边界，不是删除未见类后的好成绩。

figure03_training_loss.pdf/svg/png：seed42、7个重叠训练折平均的B2实际loss随120更新变化；只显示优化是否收敛，不是泛化曲线或7次独立实验。训练loss的类权重和折标签集不同，均值仅作工程描述。''')
 provenance=['TRAINING_BASELINE_PREDICTIONS.jsonl','GROUPED_TRAIN_VALIDATION_SPLITS.json','data/P0_REFERENCE.jsonl','manifests/TRAINING_PROTOCOL.json','evaluation/evaluate_saved.py','results/B2_TRAIN_GENERALIZATION_GAP.csv']
 dump(ao+'provenance.json',{'sources':[{'path':str(ROOT/n),'sha256':sha(ROOT/n)} for n in provenance],'primary_metric':'MRR@10','no_external_test':True,'new_GPU_operations':0,'new_LLM_calls':0,'real_trained_model':'B2_TFIDF_OVR_LOGISTIC','trained_configurations':42,'GTE_trainable_head_experiments_executed':False})
 qa=[
 '是。冻结P0的975查询/195逻辑步骤保留，输入只复用已清洗RAW，全部外层查询恰好评价一次，原目录与评价器未改。',
 '已解决：原始子技术ID集合295，父技术规范化集合285=57/195步骤。6-33和6-34各有T1056.004/T1056.001，归并为同一T1056，合计差10查询。此前295作父技术统计是报告口径错误。',
 '可用监督单位195逻辑步骤，而非975独立执行；每折实际train步骤见表。它们仍依赖7场景及共享执行/未知脚本，不能称195个统计独立攻击。',
 '真实79父类；每场景技术支持见data/SCENARIO_TECHNIQUE_SUPPORT.csv，每模拟执行见SIMULATION_TECHNIQUE_SUPPORT。各折支持量在主表。',
 '27类仅1逻辑步骤，13类2步；其余完整支持分布在MULTILABEL_DISTRIBUTION及data统计。稀疏度会导致大量保留技术未见。',
 '完成7折LOSO，内验证循环下一场景；冻结后未根据新结果换场景或调参。',
 '同一步骤5采样同划分，无跨边界完整RAW重复；对规范化全窗口交叠保守purge。真实脚本/命令模板身份UNKNOWN，不能宣称完全消除一切脚本泄漏。',
 '是，216父技术始终保留；监督分类器未见类置低分，不删除未见Gold或候选。',
 '是，B2 OVR logistic，NumPy真梯度训练，42配置、5040次Adam更新。',
 '否，真实768维GTE向量没有持久化，需新冻结前向授权。旧216候选scores不能作为h_L。',
 '尚未实际训练GTE投影；数学代码和有限差分验证通过不等于模型训练。',
 '实际更新B2每折W与b；TF-IDF词表/IDF仅训练r0拟合。GTE主干和投影未更新，全部B2权重初/终hash不同且重载一致。',
 '未完成实际GTE对比训练，真实向量/授权仍阻断，不能使用CONTRASTIVE_MODEL_TRAINED。',
 'B2的42checkpoint已保存并实际重载，最大score差0；GTE对比checkpoint不存在。',
 '未实际运行GTE困难负例挖掘，采样实现与全正例保护代码已准备；NEGATIVE_SAMPLE_QUALIFICATION明确NOT_MINED而非伪造候选。',
 '已准备的训练器只读取每fold train标签，B8挖掘只用该训练文件拟合的B5预测；尚未执行，不能宣称有实测挖掘结果。',
 '没有把补集称认证不存在。标准B2监督loss确实使用未标注补集作为弱负项，这个闭世界训练假设与事实不存在分开。',
 '父ID规范化、完整多正例掩码、已知等价归并、训练步骤共现风险已实现；对比梯度单测通过，但实际GTE负例保护实验尚未执行。',
 '差异方案固定为随机32对公开知识近邻32，同主优化预算；真实GTE采样/结果尚NA，不能给出性能差异。',
 '尚无法判断，B8未训练。未来需绑定合法B5训练checkpoint、同训练标签/特征/协议/源码哈希，不读保留组GT。',
 '尚无法判断，B9及固定.5权重控制未训练；公式和风险共现不是独立增益证据。',
 '实际指标见主表：'+summary('B0','SHARED')+'；'+summary('B1','SHARED')+'；B2单视图 '+summary('B2','ONE_VIEW_PER_STEP')+'；B2多视图 '+summary('B2','MULTI_VIEW_AUGMENTATION')+'。',
 '在已执行B0/B1/B2中，B2单视图的查询加权和场景等权MRR最高；这是描述排序，不是把保留组用于选未来算法/超参。',
 'B2收益来自其可学已见父类的排名；未见目标MRR0，不能称开放类别提升。混合目标子集见表。',
 '完整Unseen Gold子集450查询（含mixed145），B2 MRR0；B0/B1真实结果在SEEN_UNSEEN_TECHNIQUE_RESULTS，未删除未见类。',
 'B0/SHARED：单标签MRR 0.0479、Top10 12.75%；多标签MRR 0.0606、Top10 20.00%。 B1/SHARED：单标签MRR 0.0471、Top10 17.39%；多标签MRR 0.0855、Top10 26.67%。 B2/ONE_VIEW_PER_STEP：单标签MRR 0.0906、Top10 26.23%；多标签MRR 0.1435、Top10 38.25%。 B2/MULTI_VIEW_AUGMENTATION：单标签MRR 0.0855、Top10 24.83%；多标签MRR 0.1263、Top10 34.74%。 GTE对比模型尚NA。',
 '42/42 B2配置有大训练—保留差距，与过拟合/分布偏移一致；不足以单独证明场景或脚本记忆，原始脚本身份仍未知。',
 '困难负例模型没有实际训练，不能宣称超过普通监督B2；B2是当前必须击败的真实基线。',
 '普通监督B2在当前匹配输入/知识/216空间的开发点估计超过冻结GTE；GTE投影/对比方法尚无法评价。',
 '普通监督B2在当前匹配RAW条件超过B0；不能对历史不同窗口/预算27.79%直接相减。',
 'B2单/多视图各120updates、每步每轮一个view、同词表/参数/3种子，增强不是5倍更新或独立样本。未执行B7–B9，不能声称已排除其预算混杂。',
 'B2完成3固定种子17/42/73；报告逐种子、均值/SD。种子只表优化稳定性，不增加独立攻击数。',
 '有明显训练—保留差距，train-r0与heldout统计单位不同但方向一致；详见B2_OVERFIT_DIAGNOSTIC。无外层早停或追加网格搜索。',
 '没有，仍EXTERNAL_TEST_NOT_READY。P0曝光，P1/P2相关；不能重命名为独立TEST。',
 'OTRF当前官方root LICENSE与README许可表述不一致，本地旧计划字节不匹配官方blob且派生副本已曝光；标签名称到父ID/原生日志尚未齐备，不准入新训练或TEST。',
 '已核Splunk具体YAML mitre_technique是数据集元数据，只能给Bag标注；不能赋给其中每个日志事件。',
 '没有当前可直接评价的外部参考。Splunk T1003.003具体条目有3个LFS日志指针共12905849bytes，日志尚未授权下载，且单类Bag不能证明216类泛化。',
 '没有，source-presence分层不是跨平台/跨源干预，外部模型预测0，不能声称迁移证据。',
 '没有新的GPU训练授权。已提出更小的冻结特征前向请求，它即便获准也不等于LoRA/GPU训练或Gold上传授权。',
 '已完成B2的7折×3种子×2采样42个本地CPU训练配置；B0/B1复用严格匹配输入/知识的真实冻结预测，未伪造新前向。',
 '没有。主要B7/B8/B9尚未执行，不能支持也不能否定可靠性机制；现阶段只建立了强监督基线与分组评价资产。',
 '目前不足以直接启动LoRA。先按已冻结请求取得真实向量完成轻量B3–B9，再判断是否值得单独申请结构兼容的LoRA训练。',
 '可继续已限定的轻量验证，但不能因训练代码和B2涨分就正式认定困难负例算法成立；需先击败普通监督/标准对比并检查未见类。',
 '没有。7曝光场景、未知脚本依赖、小样本稀疏、无合格外部TEST，均不支持论文级独立泛化。',
 '先区分监督类别先验与真正日志—技术语义对齐：取得真实冻结向量，执行固定4主要假设和未见技术评估；避免扩大损失/权重搜索。外部只推进已核具体资源和合适标签单位。'
 ]
 text=Path('/Users/tianxd/.codex/attachments/4a2b4978-4673-4d33-86e9-c7a519adff1d/已粘贴的文本.txt').read_text();section=text.split('# 二十五、')[1].split('# 二十六、')[0];qs=re.findall(r'^\d+\. (.+)$',section,re.M);assert len(qs)==len(qa)==45;answers='\n\n'.join(f'### {i}. {q}\n\n{a}' for i,(q,a) in enumerate(zip(qs,qa),1))
 report=f'''---
type: results-report
date: 2026-10-28
experiment_line: domain_adaptive_contrastive_learning
round: 01
purpose: grouped-training-and-resource-qualification
status: supervised_completed_contrastive_resource_blocked
source_artifacts: [reports/analysis-output/analysis-report.md, reports/analysis-output/stats-appendix.md, reports/analysis-output/figure-catalog.md, reports/analysis-output/provenance.json]
linked_experiments: [manifests/TRAINING_PROTOCOL.json, GROUPED_TRAIN_VALIDATION_SPLITS.json]
linked_results: [GROUPED_VALIDATION_RESULTS.csv, results/OVERALL_RESULTS.csv]
---
# ATT&CK领域适配 / Round 01 / 分组训练与资源资格 / 2026-10-28

## 执行结论

主状态 **{main_state}**。已完成合法分组、标签统计纠正、42个B2真实监督训练与5040次更新，全部保存checkpoint并重载一致；5850条受训外层预测，加1950条匹配输入的真实冻结基线预测，逐条评价。当前只有普通监督线性训练完成，**GTE投影/标准对比/困难负例不能视为已训练**。

B2单视图MRR {float(lookup['B2','ONE_VIEW_PER_STEP']['mrr']):.4f}、多视图{float(lookup['B2','MULTI_VIEW_AUGMENTATION']['mrr']):.4f}，超过同输入冻结GTE的{float(lookup['B1','SHARED']['mrr']):.4f}，但封闭分类器Unseen目标MRR0，且训练—保留差距显著。它说明监督类别信息很有竞争力，不能据此证明对比学习创新或开放类别泛化。

{blocked} 已按附件§12.2/§22.1/§22.6准备具体代码、哈希和15分钟/200MB最小向量提取请求。旧授权未扩大。独立外部TEST仍未就绪。

## 身份、数据与标签修正

P0=PUBLIC_EXPOSED_DEVELOPMENT，P1/P2=RELATED_DEVELOPMENT_DATA。975查询、195逻辑步骤、7场景、34执行标识、216候选、79实际父类不变。官方作者步骤标签可用于监督，但不等于逐行OBSERVATION_VERIFIED_MECHANISM。多个正标签均以集合保留，不取第一个。

多标签差异已经精确定位：295/975为原始子技术集合，父技术集合285/975=57/195；6-33、6-34的T1056.004与T1056.001归一T1056，5采样×2步差10查询。上一轮295作父技术统计是口径错误，保留原文、在新报告纠正，不修改历史预测/评价器。79类中27仅1步、13仅2步，类别稀疏真实存在。

所有输入复用上一轮已清洗RAW2000字节、知识K2_16_1前缀1000字节，无新增事实。B0/B1旧预测与本轮每条文本/知识哈希完全相同，因此可按折复用冻结推理，不从候选scores还原向量。不与历史不同窗口/预算的27.79%/30.26%直接比较。

## 场景、脚本与分组协议

{foldtable}

相同逻辑步骤5采样始终同划分；循环内验证仅作分离诊断，不选择超参或checkpoint。折4内验证仅2步，故固定120updates。训练只读对应fold train Gold，保留和验证输入/参考分开，评价器在保存预测后读取标签。

没有跨场景完全相同RAW；1-54、2-5、3-49出现去时间/PID后完整窗口一致的cron观察，按整个步骤跨边界purge。它可能是共有背景日志，不认证同一攻击脚本。真实攻击script identity仍UNKNOWN，scenario只作保守代理，不能宣称完全消除跨脚本依赖。LOSO仍属GROUPED_DEVELOPMENT_VALIDATION，不是新独立TEST。

## 模型、真实更新与公平控制

B0冻结字符检索，B1冻结GTE CLS+L2旧实测，均参数0更新。B2为训练集r0拟合字符3/4/5gram、min_df2、最多2048维、sublinear TF和平滑IDF的多标签OVR logistic。只训练本折出现类，未见类分数-1e6且留在全216排名。B2词表/IDF在两增强模式共用，避免把词表扩展当增强收益。

3种子17/42/73，Adam lr.03、L2 .001、120全逻辑步batch更新。ONE固定r0，MULTI每轮(epoch+seed)%5，每逻辑步每轮一view，标签和优化步数相同；5视图不是5次独立监督攻击。所有42权重初/终hash不同、loss/梯度有限、checkpoint实际重载预测差0。各算法独立命名venv，NumPy只读复用，无新包/系统Python修改。

B3–B9代码已实现多正例与可靠性权重，并通过有限差分梯度测试；这仅是实现验证。没有真实向量时不生成替代向量或训练成绩。B5/B6共享loss，区别仅全补集与32随机候选；B7/B8为语义/训练模型未标注困难候选，B9同池风险权重另设固定.5控制；全正例屏蔽、父ID归并、训练内共现，不制造EVIDENCE_CERTIFIED_NEGATIVE。

## 主要实际结果

{main_table}

全部V1指标（Top1/5/10、Precision/Recall、Micro/Macro F1@5）和分折/分种子原值在CSV。MRR是主指标，Top10重要辅助。B2单视图最好只是已执行方法描述，未用其保留成绩改变未来训练规则。

{scenetable}

{seentable}

Seen/Unseen Gold子集保留完整216预测；全seen525、全unseen305、mixed145。目标子集分别670与450查询，mixed可重复出现；子集P/F1会把另一子集Gold算目标FP，因此优先解释MRR/Top10。不同长度和日志来源分层、相同冻结GTE Top20的条件排序均已交付，不能把source-presence当成跨源迁移或把条件候选命中当总体成绩。

## 统计与稳定性

预登记4主要MRR假设：B4vsB1、B5vsB4、B7vsB6、B9vsB8。未执行项NA。当前不重做292项检验，也不将975条相关查询或3种子当独立攻击。报告查询加权、等权场景、种子均值/SD、每折原值和方向。7曝光且脚本依赖不明、训练折重叠，不进行确认性p值或过强泛化CI。

## 图与训练诊断

![逐场景MRR]({ROOT}/reports/analysis-output/figures/figure01_scenario_mrr.png)

图1对照冻结与普通监督，在场景间表现不均；需结合支持标签和小场景解释，不能用总体最高值替代独立测试。

![已见未见目标]({ROOT}/reports/analysis-output/figures/figure02_seen_unseen.png)

图2显示封闭监督分类器的未见技术边界。两个Gold子集并非完全互斥样本，不把图当两个独立测试集。

![实际训练曲线]({ROOT}/reports/analysis-output/figures/figure03_training_loss.png)

图3是seed42跨折训练loss描述，loss下降不证明泛化。42/42配置训练优于保留；单视图等权折训练MRR约.7167、内验证.0830、保留.0838，多视图.6733/.0706/.0782。训练r0与保留5相关采样不同，风险与过拟合/分布偏移一致，不能单独证明脚本记忆。

## 成本、失败与权限

42个B2 checkpoint约40.65MB，5040更新，配置CPU合计约13.04秒、wall13.86秒，最大进程RSS约109.54MB；共享词表/特征构建不在配置计时内，整体预处理耗时未单独计量，不能把13.86秒称全管线总耗时。完整参数量、文件字节、种子、推理延迟在MODEL_TRAINING_RECEIPTS及TRAINING_RESOURCE_REPORT。CPU词法/向量头无神经Tokenizer，训练Token记N/A而非虚构0。

本轮没有任何服务器操作、GPU前向/训练、Gold上传、新模型下载或LLM调用。此前服务器前向权限没有扩展；这不是停止所有机器学习训练的理由，因此B2已真实执行。最小冻结特征请求包含目标新项目/同名venv、只读模型依赖、975×768与216×768向量、无Gold、GPU0显存15%/CPU2线程/batch8/900秒/100万Token/新增200MB上限、代码SHA。只有新明确授权后才可执行。LoRA/GPU参数训练仍另需审批。

## 外部资源资格

OTRF官方固定commit和本地已有APT29派生资产已核查；root LICENSE与README许可文字冲突，本地旧计划25050bytes不等于官方blob25051bytes，且旧派生数据已曝光。原生日志/计划/标签映射/独立性未齐，不准入外部训练或TEST。

Splunk已核具体YAML id cc9b25e1-efc9-11eb-926b-550bf0943fbb，T1003.003归T1003在216候选中；3个日志LFS指针合计12905849bytes，尚未下载日志。标签是dataset-level Bag，不能赋给每条event；一个类别不足以证明216技术泛化。所有官方元数据/Git blob校验、固定commit与具体链接见EXTERNAL_DATASET_QUALIFICATION。外部评价与新增监督样本均0，指标NA。

## 科研判断、信念更新与下一步

当前GO：保留严格分组、真实普通监督基线和具体向量提取请求。普通监督的开发收益使“对比学习必须击败合理监督基线”更加重要；未见类别与训练差距使“训练后自然会获得语义泛化”的前提不成立。

当前不能判断困难负例或可靠性机制优劣：主方法没有实际训练，不能把代码通过或B2提升当其贡献，也不能把未执行当负结果。按既定新授权请求取得真实向量后才可在本地CPU完成B3–B9；LoRA暂不应跳过此层直接启动。外部先推进具体小范围资源和正确Bag任务单位，不自动拉大型库或下载日志。本报告完成已许可部分，保留资源阻断，等待明确资源答复后续执行，不自动训练下一轮。

## 45项逐条回答

{answers}

## 复现与交付索引

数据/标签资格、7fold清单和manifest；B2训练器、42npz、参数更新/重载receipt；真实冻结B0/B1继承receipt；全部外层预测与V1评价；分场景、种子、seen/unseen、长度、source presence、训练差距；未执行GTE模型状态；梯度测试与独立代码/数据审查；外部官方元数据和授权请求均保存。最终完整性见results/FINAL_VALIDATION.json与manifests/DELIVERY_SHA256.json。旧1029项继承资产保持不变；不读取受限归档、PwnKit35–37正文或CONV-A01。
'''
 write('R3_DOMAIN_ADAPTIVE_CONTRASTIVE_LEARNING_RESULTS.md',report)
 dump('results/RESEARCH_STATUS.json',{'main_status':main_state,'secondary':['GROUPED_TRAINING_BENCHMARK_READY','TRAINING_RESOURCE_AUTHORIZATION_BLOCKED','EXTERNAL_TEST_NOT_READY'],'B2_trained_configurations':42,'GTE_heads_trained':False,'hard_negative_effect':'NOT_EVALUATED','new_GPU_training_authorized':False,'new_feature_extraction_authorized':False,'new_LLM_calls':0,'external_test_samples':0,'questions_answered':45})
 print('45answers, actual supervised report and strict analysis bundle written')
if __name__=='__main__':main()
