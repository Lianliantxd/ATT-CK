import csv,json,hashlib,statistics,sys,subprocess
from pathlib import Path
from collections import defaultdict,Counter
R=Path(__file__).resolve().parents[1]
def load(n):return json.loads((R/n).read_text())
def readcsv(n):return list(csv.DictReader((R/n).open()))
def write(n,s):(R/n).write_text(s.strip()+'\n')
def dump(n,obj):write(n,json.dumps(obj,indent=2,ensure_ascii=False))
def csvout(n,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for r in rows for k in r))
 with (R/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def table(rows,columns):
 return '| '+' | '.join(columns)+' |\n| '+' | '.join('---' for k in columns)+' |\n'+'\n'.join('| '+' | '.join(str(r.get(k,'N/A')) for k in columns)+' |' for r in rows)
def readlines(path):
 with Path(path).open() as f:return [json.loads(x) for x in f]
def display(rows):
 return [{'Method':r['method'],'Protocol':r['protocol'],'View':r['input_view'],'N':r['N_Queries'],'Top1%':f"{100*float(r['top1_accuracy']):.2f}",'Top5%':f"{100*float(r['top5_accuracy']):.2f}",'Top10%':f"{100*float(r['top10_accuracy']):.2f}",'StepMacroTop10%':f"{100*float(r['step_macro_top10_accuracy']):.2f}",'P@5':f"{float(r['precision_at_5']):.4f}",'R@5':f"{float(r['recall_at_5']):.4f}",'MRR':f"{float(r['mrr']):.4f}"} for r in rows]
def show(rows):
 d=display(rows);return table(d,list(d[0])) if d else 'N/A'

def main():
 p0=readcsv('STRONG_BASELINE_RESULTS_P0.csv');p1=readcsv('STRONG_BASELINE_RESULTS_P1.csv');p2=readcsv('STRONG_BASELINE_RESULTS_P2.csv');allrows=p0+p1+p2;coverage=load('knowledge/COVERAGE.json');m1=load('P1_RESAMPLED_DATA_MANIFEST.json');m2=load('P2_V2_DATA_MANIFEST.json');stable=load('datasets/manifests/STABLE_CLEANED.json');refs=readlines(R/'datasets/p0_reference.jsonl');q0=readlines(R/'datasets/p0_prediction.jsonl');historical=readcsv('frozen_p0/OFFICIAL_METRIC_RECALCULATION.csv');gpt=next(r for r in historical if 'gpt-5.5' in r['method'] and r['denominator']=='all eligible queries; missing=zero')
 fusion=[r for r in allrows if r['method'].startswith(('SourceWise','Evidence'))]
 csvout('SOURCE_FUSION_RESULTS.csv',fusion);csvout('SOURCE_FUSION_ABLATION.csv',[r for r in fusion if r['method'].startswith('Evidence')]);csvout('METHOD_DEV_RESULTS.csv',[r for r in fusion if r['method'].startswith('Evidence')]);csvout('METHOD_ABLATION_RESULTS.csv',[r for r in fusion if r['method'].startswith('Evidence')])
 # Main comparisons keep all knowledge/input conditions explicit.
 k2=[r for r in p0 if r['knowledge_view']=='K2_DESCRIPTION_16_1' and r['input_view'] in ['all','native','sourcewise_same_native_content']]
 formal=[r for r in k2 if '_No' not in r['method']]
 best1=max(formal,key=lambda r:float(r['top1_accuracy']));best10=max(formal,key=lambda r:float(r['top10_accuracy']));bestm=max(formal,key=lambda r:float(r['mrr']))
 overallbest=max(p0,key=lambda r:float(r['top10_accuracy']))
 basis='''本轮所有P0结果均为PUBLIC_EXPOSED_DEVELOPMENT；P1和P2与之共享执行，不是独立TEST。GT只在数据配对和评价中读取，不进入预测器。未经授权的场景1步骤35—37全部变体在ZIP成员正文读取前排除；无模型API、无权重下载、无服务器修改。'''
 write('KNOWLEDGE_COVERAGE_REPORT.md',f'''# 固定知识控制

{basis}

216父候选不变。K0为官方父/子技术名称；K1追加原官方战术；K2严格复用旧16.1扩展文档；K3保留战术和STIX描述正文，移除显式标题块，但正文固有技术名称/例子仍保留，不能当作彻底去除所有名称词。K3改变文本量且非语义等长对照。

16.1非作者原ATT&CK确切版本，只有203父候选有描述，13缺口：{', '.join(coverage['missing'])}。K2保留缺口的官方名称/战术；主候选不删。实际Gold79类全落在203内，因此K4无需删任何975查询：控制变的是负候选/语料IDF，不能把其变化归结为更好覆盖Gold。

全部条件在knowledge/*.json按哈希冻结，原文档生成代码baselines/prepare_inputs.py。各条件×4表示已实跑，详见ATTACK_KNOWLEDGE_CONTROL_RESULTS.csv。''')
 write('DESCRIPTION_COVERAGE_AUDIT.md',f'''# 描述覆盖审计

K2描述来自既有MITRE16.1 STIX，原SHA256 `{coverage['sha256']}`。原文档的来源说明不能证明和官方matrix同发行版本；本轮没有用最新版覆盖作者空间。203/216有有效非撤销/非弃用描述；13缺描述仍保留在主协议。缺口清单见KNOWLEDGE_COVERAGE_REPORT.md。

K4仅作为分析条件，不替代主216候选表。所有975 P0 Gold都在共同203覆盖内，所以对照保留相同样本，N/excluded_gold_outside_common_coverage显式报告。候选数变少同时改变IDF和排序干扰项；不能拿203类最好数值当216类正式成绩。''')
 write('TITLE_LEAKAGE_CONTROL.md','''# 标题控制的含义

日志里的官方标签已移除；公开ATT&CK知识文档的技术名称是合法候选知识，不自动是测试GT泄漏。但标题直接词面匹配可能产生收益，不能当成知识推理。

K0/K1/K2/K3分别控制名称、战术、描述与显式标题块。K3只删文档构建时额外添加的标题，保留正文中的自然名称和公开引用。没有为了人为降分把攻击命令、工具名或真实路径删光。它也删除部分标题文本，不能视作严格等字数消融。

知识控制只改变公开文档，输入日志/GT/216候选保持相同；K4另列203候选分析。所有条件为固定参数，无按测试答案增词。''')
 # Source level scores indexed once per representation in the main P0 condition.
 with (R/'SOURCE_LEVEL_TECHNIQUE_SCORES.jsonl').open('w') as out:
  for mode in ['bm25','word']:
   path=R/'experiments'/('fusion_K2_'+mode)/'SOURCE_LEVEL_TECHNIQUE_SCORES.jsonl'
   with path.open() as f:
    for line in f:
     row=json.loads(line);row['knowledge_view']='K2_DESCRIPTION_16_1';row['protocol']='P0';out.write(json.dumps(row)+'\n')
 # Flatten lean Top10 results. Detailed vectors and evidence remain separately auditable.
 receiptfiles=sorted((R/'experiments').glob('*_receipt.json'));receipts=[];flat_count=0
 with (R/'STRONG_BASELINE_PREDICTIONS.jsonl').open('w') as out:
  for p in receiptfiles:
   r=json.loads(p.read_text())
   if 'representation' not in r or (r.get('exit_code')!=0 and not r.get('completion_verified')):continue
   receipts.append(r)
   with Path(r['output']).open() as f:
    for line in f:
     pred=json.loads(line);out.write(json.dumps({k:r[k] for k in ['method','protocol','input_view','knowledge_view','execution_status']}|{'sample_id':pred['sample_id'],'predictions':pred['predictions'],'scores':pred.get('scores',[]),'native_prediction_path':r['output']})+'\n');flat_count+=1
 dump('results/PREDICTION_INDEX_SUMMARY.json',{'conditions':len(receipts),'prediction_rows':flat_count})
 register=[]
 for method in sorted({r['method'] for r in allrows}):
  rr=[r for r in allrows if r['method']==method]
  env='EvidenceLineFusion' if method.startswith('Evidence') else ('SourceWiseBM25' if method.startswith('SourceWiseBM25') else 'SourceWiseTFIDF' if method.startswith('SourceWiseTFIDF') else method)
  envpath=R/'venvs'/env
  if not envpath.exists():envpath=R.parent/'research3_attack_technique_benchmark01/venvs'/('TFIDFTechniqueRetrieval' if method=='TFIDF' else 'BM25TechniqueRetrieval')
  register.append({'algorithm':method,'status':'PROJECT_NEW_INFERENCE' if not method.startswith('SourceWise') else 'ADAPTED_BASELINE','protocols':';'.join(sorted({r['protocol'] for r in rr})),'conditions':len(rr),'environment':str(envpath),'qualification':'deterministic retrieval/fusion, not full external paper reproduction'})
 for method,reason in [('KnowHow','Existing official dictionary adaptation retained from frozen P0; not full model rerun this round'),('TREC','No new certified source/model/NOI/graph-GT/splits'),('APTREC','No new graph-GT/LoRA/official core implementation'),('OCR-APT','Official component code exists; matching input/service unavailable'),('SentenceSemanticEncoder','EMBEDDING_BASELINE_RESOURCE_BLOCKED; weights/tokenizer/license/dependencies incomplete'),('SupervisedClassifier','No credible independent train split; not run')]:
  register.append({'algorithm':method,'status':'OFFICIAL_COMPONENT_ONLY' if method=='KnowHow' else 'NOT_EXECUTED','protocols':'P0 inherited' if method=='KnowHow' else 'N/A','conditions':0,'environment':'existing read-only where available; no empty new environment','qualification':reason})
 csvout('STRONG_BASELINE_REGISTER_V2.csv',register);csvout('BASELINE_REPRODUCTION_STATUS_V2.csv',register)
 environments=[]
 envpaths=sorted((R/'venvs').iterdir())+[R.parent/'research3_attack_technique_benchmark01/venvs'/n for n in ['TFIDFTechniqueRetrieval','BM25TechniqueRetrieval']]
 for p in envpaths:
  exe=p/'bin/python';info=subprocess.run([str(exe),'-B','-c','import sys,json;print(json.dumps({"executable":sys.executable,"prefix":sys.prefix,"base_prefix":sys.base_prefix,"version":sys.version}))'],capture_output=True,text=True,check=True)
  freeze=subprocess.run([str(exe),'-m','pip','freeze'],capture_output=True,text=True,check=True);check=subprocess.run([str(exe),'-m','pip','check'],capture_output=True,text=True)
  environments.append({'name':p.name,'path':str(p),**json.loads(info.stdout),'pip_freeze':freeze.stdout,'pip_check_exit':check.returncode,'pip_check_output':check.stdout,'weights':'none; standard library algorithms only','source_version':'local versioned code hashes in delivery manifest','inference_status':'actual completed predictions; original-process receipts qualifier retained'})
 dump('manifests/ENVIRONMENT_MANIFEST_V2.json',environments)
 runtime=[{k:r.get(k,'N/A') for k in ['method','protocol','input_view','knowledge_view','seconds','exit_code','InferenceTimeQualification','execution_success_basis','output']} for r in receipts]
 csvout('results/RUNTIME_DETAILS.csv',runtime)
 write('BASELINE_RUNTIME_REPORT.md',f'''# 运行与环境

五个新增算法环境：CharacterNgramTFIDF、WordCharacterHybrid、SourceWiseBM25、SourceWiseTFIDF、EvidenceLineFusion；各自Python3.12.14、标准库实现。TFIDF/BM25复用旧独立环境只读运行，未安装包或写旧目录。解释器、前缀、pip freeze/check保存在manifests/ENVIRONMENT_MANIFEST_V2.json。没有预训练嵌入权重可执行，不能把字符表示叫语义模型。

有效推理条件{len(receipts)}项、Top10预测{flat_count}行；数字仅描述覆盖，不代表科研质量。每项命令/真实独立子进程退出码与输出见experiments/*receipt.json；P0六批融合的单独退出码未捕获，标NOT_CAPTURED，依完成run摘要、975输出数、知识/输入hash和逐条可评分完整性认证，未补造退出码。后续批次真实退出码均保存。

SOURCE融合InferenceTime为共享批次耗时（四方法一次执行），不可把各行相加当总耗时。详见results/RUNTIME_DETAILS.csv；原生run.json与stdout保留。耗时不是同运行成本比较。完整v2字符推理约122秒，资源本地CPU有界。

初次P1/P2未清洗输入的输出全部放experiments/INVALID_UNCLEANED_FIRST_RUN，状态INVALID_UNCLEANED_INPUT_DO_NOT_REPORT。它们未用于调参或最终表，修复后全部重建与重跑。没有以不合法初分数选优。

新LLM/API调用0、Token/API费用0、模型下载0、服务器修改0。日志/原攻击脚本从未执行。普通算法代码与经AST单独提取的官方采样函数等价检查不是攻击执行。

重跑按序：prepare_inputs.py、prepare_controls.py；数据安全读取datasets/build_v2.py；run_matrix.py、run_extensions.py、run_fusion_followups.py；register_fusion_runs.py、evaluate_runs.py、compare_protocols.py、method/exact_evidence_traces.py、summarize_delivery.py。P0六批主融合命令见各实验日志及METHOD_FORMAL_DEFINITION，CLI参数同followup。重跑会覆盖本轮派生文件，先复制本目录；不覆盖旧目录。
''')
 stability=readcsv('RESAMPLING_STABILITY_RESULTS.csv');ss=[]
 for prot in ['P0','P1','P1_FIXED']:
  for method in ['BM25','CharacterNgramTFIDF','SourceWiseBM25_RRF','EvidenceLineFusion_bm25']:
   rr=[r for r in stability if r['protocol']==prot and r['method']==method]
   if rr:ss.append({'protocol':prot,'method':method,'logical_steps':len(rr),'mean_top1_pair_agreement':statistics.mean(float(r['top1_pair_agreement']) for r in rr),'mean_top10_jaccard':statistics.mean(float(r['top10_pair_jaccard']) for r in rr),'mean_mrr_variance':statistics.mean(float(r['mrr_population_variance']) for r in rr),'distinct_input_sum':sum(int(r['distinct_inputs']) for r in rr)})
 csvout('results/STABILITY_SUMMARY.csv',ss)
 write('GENERALIZATION_LIMITATIONS.md',f'''# 泛化资格

{basis}

P0重新分组仍是开发诊断。P1同源重新抽样，与模型能力变化不同；变体选择变化也会改变Gold/行为。固定变体控制只控制执行，不控制v1/v2内容和P0标题差异。v2不是独立外部集。P2的385执行-step对195逻辑step不等权，必须同时查看query与Step-macro。

GROUPED_VALIDATION_RESULTS.csv包含每场景/执行的实际步数、类别、未见类、TopK/P/R/MRR/F1与多标签比例；没有用这些标签训练模型。DATASET_DEPENDENCY_GROUPS.csv固定logic-step/execution/scenario/hash组。没有把五replica拆入训练测试。脚本模板独立性未认证，不声称EXTERNAL_TEST。当前EXTERNAL_TEST_NOT_READY。

来源类型细分类的P0/v2映射差异19种path、76文件已另存；audit/non-audit主体一致，算法本身以host-file分组、不按类型给权，因此主融合排序不受类型映射影响，但细来源跨版本分布不可直接因果比较。

仅7场景，不进行975独立样本bootstrap或精确跨场景显著性主张。重采样输出变化为描述性敏感性，未做跨独立攻击的显著性检验。''')
 # Knowledge controls and budget outcomes are explicit, never selected only against weakest BM25.
 samek=[r for r in p0 if r['knowledge_view']=='K2_DESCRIPTION_16_1' and r['input_view'] in ['native','records40','tokens2048']]
 write('reports/BUDGET_CONTROL_REPORT.md',f'''# 等预算对照

每host-source10行不是相同TOTAL预算。P0基准同一975输入供全部方法；native控制只去主机/来源标题而保留全部事件/续行。records40以来源轮转选择最多40条原生记录，tokens2048以来源轮转最多2048个非空白片段，并保存最后一行前缀hash。这里Token为明确regex代理，不是某LLM tokenizer Token；不能推算模型调用成本。

相同view各算法看到同样sources内容，不让新机制多拿日志。P2-Full只表示获准filtered完整步骤，非完整攻击历史。

{show(samek)}
''')
 # Per-technique recall on chosen comparison methods, without calling this causal error classification.
 meta_by_id={r['sample_id']:r for r in refs};techrows=[];per_scenario=[]
 core_receipts=[r for r in receipts if r['protocol']=='P0' and r['knowledge_view']=='K2_DESCRIPTION_16_1' and r['input_view'] in ['all','sourcewise_same_native_content'] and r['method'] in ['BM25','CharacterNgramTFIDF','SourceWiseBM25_RRF','SourceWiseBM25_SourceScoreNormalization','EvidenceLineFusion_bm25']]
 for run in core_receipts:
  pred={r['sample_id']:r['predictions'] for r in readlines(run['output'])}
  for tech in sorted({t.split('.')[0] for r in refs for t in r['ground_truth']}):
   rr=[r for r in refs if tech in {t.split('.')[0] for t in r['ground_truth']}]
   techrows.append({'method':run['method'],'technique':tech,'queries':len(rr),'steps':len({(r['scenario_id'],r['step_id']) for r in rr}),'gold_label_recall_at10':sum(tech in pred[r['sample_id']][:10] for r in rr)/len(rr)})
 csvout('results/PER_TECHNIQUE_COMPARISON.csv',techrows)
 # Paired single-method changes by scenario preserve all failures and opposite directions.
 groups=readcsv('GROUPED_VALIDATION_RESULTS.csv');scene=[r for r in groups if r['protocol']=='P0' and r['knowledge_view']=='K2_DESCRIPTION_16_1' and r['group_type']=='scenario' and r['input_view'] in ['all','native','sourcewise_same_native_content'] and r['method'] in ['BM25','CharacterNgramTFIDF','SourceWiseBM25_RRF','SourceWiseBM25_SourceScoreNormalization','EvidenceLineFusion_bm25']]
 csvout('results/SCENARIO_COMPARISON.csv',scene)
 # Retain method decision regardless of top10-only ablation best.
 write('METHOD_RESEARCH_DECISION.md',f'''# 科研决策

主状态STRONG_BASELINES_EXTENDED；辅状态RESAMPLING_AND_V2_PROTOCOLS_READY、PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS。来源感知简单基线在部分指标有开发收益；完整新候选机制未证明优于合理最强同知识基线，所以新机制NO-GO为当前论文核心。独立泛化未证明。

同216候选/K2下，正式非消融方法最高Top1={best1['method']}({100*float(best1['top1_accuracy']):.2f}%)，最高Top10={best10['method']}({100*float(best10['top10_accuracy']):.2f}%)，最高MRR={bestm['method']}({float(bestm['mrr']):.4f})。候选EvidenceLineFusion在某些Top10条件胜RRF，但Top1/MRR明显下降；NoSourceCalibration是预设消融，不事后升级为主方法。

相同native输入的全文对照已运行，预算40record/2048regex-token亦运行，不能只对原18.05%弱参考说改进。知识K0—K4控制显示变化不等于知识推理；原生格式/来源标题本身改变检索结果。P1/P2的字符表示往往更有竞争力，融合不能跨采样全面稳定压过它。

下一步若研究LLM，先围绕真实错误案例验证执行证据与知识语义脱节、泛词匹配、源内结果状态，不增加无证据Agent。现有错误trace只是候选排序证据，不是独立Gold；没有依据授予新模型调用权限。外部完整TREC/APTREC仍需数据/模型配套，语义嵌入仍资源受阻。

可以进入可复核baseline/数据协议实验整理阶段；尚不能把本候选机制作为已证实创新写入正式性能主张，也不能宣称外部泛化。保留负结果、所有失败与无效初跑记录。
''')
 # Broad main table and explicit answers.
 selected_names=['TFIDF','CharacterNgramTFIDF','WordCharacterHybrid','BM25','SourceWiseBM25_Max','SourceWiseBM25_Mean','SourceWiseBM25_RRF','SourceWiseBM25_SourceScoreNormalization','SourceWiseTFIDF_SourceScoreNormalization','EvidenceLineFusion_bm25','EvidenceLineFusion_word']
 core=[r for r in formal if r['method'] in selected_names]
 p1core=[r for r in p1 if r['protocol']=='P1' and r['method'] in selected_names]
 p2core=[r for r in p2 if r['method'] in selected_names]
 full_best1=max(p0,key=lambda r:float(r['top1_accuracy']));full_best10=max(p0,key=lambda r:float(r['top10_accuracy']));full_bestm=max(p0,key=lambda r:float(r['mrr']))
 answers=[
 '是，21项旧输入/标签/成绩/代码按SHA256冻结，195步975记录，旧目录未修改。',
 '是，官方清洗prompt仍为385不同、590重复；不是975次独立攻击。',
 '取得固定commit官方resample脚本；仅在安全包装器中运行原采样函数做6项等价测试，未执行无权限过滤的原main。',
 'P1主195逻辑步975查询；另有保持P0变体的975条fresh-window控制。',
 'P1主767不同输入、208重复；固定变体控制792不同、183重复。',
 '是，每重复重新选择每source随机连续10行；但底层为v2，P0/P1还混合版本/变体/标题变化，不能归因纯采样。',
 '是，复用已核验213,771,977字节v2 ZIP，无重复下载/覆盖。',
 '是，预先元数据白名单；受限场景1的35—37全部变体不读取，其他不确定成员也不读取。',
 'P2为385个执行-step、195个逻辑step、34模拟；Sampled与Full各385条。',
 '实际来源含audit、authentication、web_access、application、wazuh、suricata、system、other；主体与细映射差异均保存。',
 'v2场景7steps3/6/8/10/13确实观察runc+init；无完整v1日志，不能证明P0未采样到的内容均为版本新增。',
 '主协议216不变；K4仅203候选分析，不混入主成绩。',
 '13缺口保留名称/战术；全79 Gold都覆盖在203内，K4控制改变负候选与IDF而非删除难Gold。',
 '是，3—5字符ngram、仅公开知识拟合IDF，保存975条Top10及P1/P2新预测。',
 '是，host-file分源BM25，公开216全候选源分数保存。',
 '是，host-file分源词级TF-IDF，公开216源分数保存。',
 '是，Max、Mean、RRF、SourceScoreNormalization四项固定规则均跑，另跑候选与三消融。',
 f"全部P0条件（含预算/知识/消融）最高Top1为{full_best1['method']}，{full_best1['knowledge_view']}/{full_best1['input_view']}，{100*float(full_best1['top1_accuracy']):.2f}%；同K2非消融主对照另列，不能混候选空间。",
 f"全部条件最高Top10为{full_best10['method']}，{full_best10['knowledge_view']}/{full_best10['input_view']}，{100*float(full_best10['top10_accuracy']):.2f}%；消融最佳不升级主机制。",
 f"全部条件最高MRR为{full_bestm['method']}，{full_bestm['knowledge_view']}/{full_bestm['input_view']}，{float(full_bestm['mrr']):.4f}；同K2非消融最高见主表。",
 '同view/同K2/216候选确有部分简单融合收益；预算对照见reports/BUDGET_CONTROL_REPORT.md，不能宣称所有指标/协议全面提升。',
 'K3已运行，去显式标题后仍有检索命中，完整候选机制没有全面压过简单对照；正文内自然名称仍存在。',
 'COMMON_COVERAGE_203_RESULTS.csv保存4表示同975样本结果；Gold无需删除，候选数和IDF变化另列。',
 'audit-only与non-audit-only及8源单独运行；空来源单列，见来源表和预算报告，不把空输入当语义失误。',
 '部分指标胜直接拼接；native控制也改善全文BM25，来源融合收益不能全归因于融合模块。',
 '完整候选有Top10改善但Top1/MRR下降；未证明超越RRF及最强简单归一化/字符基线。',
 '有方向相反的场景变化，全部7场景及执行指标保留，不只报有利场景；见SCENARIO_COMPARISON.csv。',
 '排名稳定性确有描述性变化；未做独立攻击显著性推断，不使用“显著”统计结论。',
 '同一确定性算法在不同窗口/变体中变化属于输入敏感性；IDENTICAL_INPUT与DIFFERENT_LOG_SAMPLE分别保存。',
 '本轮没有认证真正未曝光独立测试执行。',
 '完成按scenario/execution的分组开发评价，列类别交集/其他组未见类、步数与多标签比例；不是监督训练测试。',
 '没有，EXTERNAL_TEST_NOT_READY；v2共享原执行不充当外部集。',
 'KnowHow继承公开字典适配，不冒称完整模型；TREC/APTREC无新认证配套资产；OCR-APT仅已有组件资格，未新增完整复现。',
 '是，5新增算法命名独立环境；旧BM25/TFIDF环境只读复用，未造TREC/APTREC空新环境。',
 '没有可完成新日志编码的本地语义嵌入模型。',
 'HF仅ref无权重/tokenizer/license；旧KnowHow有技术向量无日志编码器/主权重，依赖也缺；不下载模型。',
 f"作者GPT5.5历史Top10={100*float(gpt['top10_accuracy']):.2f}%；同216/K2正式非消融基线Top10最高{100*float(best10['top10_accuracy']):.2f}%，差{100*(float(gpt['top10_accuracy'])-float(best10['top10_accuracy'])):.2f}个百分点。不是本项目新调用LLM。",
 '8个固定顺序案例保留命令/告警原生候选行与hash，例如下载文件行为可观察但不自动证明加载/持久化成功。',
 '案例显示候选匹配可由auth/com/is等泛词驱动；“描述语义重叠”仍是需受控验证的解释，不由错预测自动认证。',
 '部分来源/采样控制改变排序，支持敏感性现象；不能据此断言关键日志缺失或标签错。',
 '验证了确定性模块对排名有影响；没有证明完整候选是独立有效的新算法贡献。',
 '同K2/同native预算对照排除新增知识/日志作为某些差异的原因；跨知识/Full/203条件不能据此归因算法。',
 '有候选hit而RRF miss的具体例子，也有反例；整体未胜强对照，不足主张解决简单方法不能解决的问题。',
 '有值得研究的实际错配/候选证据案例，但尚无Agent必要性证据。当前不新增调用，不强建多Agent算法。',
 '可整理baseline与采样协议研究结果；尚不具备以本候选新机制和外部泛化作为正式论文核心结论的证据。'
 ]
 write('R3_TECHNIQUE_STRONG_BASELINES_GENERALIZATION_RESULTS.md',f'''# R3_TECHNIQUE_STRONG_BASELINES_AND_GENERALIZATION02

主状态 **STRONG_BASELINES_EXTENDED**。辅状态 **RESAMPLING_AND_V2_PROTOCOLS_READY**、**PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS**。完整候选机制尚未证明优于合理强基线；独立泛化未证明。

'''+ '\n\n'.join(f'{i}. {text}' for i,text in enumerate(answers,1))+f'''

## P0：固定公开开发输入

195逻辑步×5=975查询，7场景，216父技术，K2知识条件。P0主表为query-weighted，因每步同5条也等于对应step-macro；F1@5等详细指标在CSV。SourceWise的输入是相同native事件，native对照另列用于排除去标题影响。

{show(core)}

作者GPT-5.5历史参照：Top1=40.92%、Top5=60.21%、Top10=66.67%、MRR≈0.4960，仅AUTHOR_HISTORICAL_RECALCULATION。不移植到P1/P2。旧Random/Lexical/KnowHow成绩全部冻结可查，不修改、不冒充本轮重推。

全部20项知识×表示初始对照与预算/来源/消融条件均保留STRONG_BASELINE_RESULTS_P0.csv；不以挑最优K/候选数取代主表。

## P1：真实重复抽样，v2底层

主协议195逻辑步975查询，767不同输入、208重复；固定变体附加控制975/792不同。每replica重新采样，短源可能仍重复。官方连续窗口核心经6项等价验证，文件顺序固定。受限variant池与安全ZIP读取使其不是原main无改运行。

{show(p1core)}

P1_FIXED独立标在同CSV内，绝不与主P1合并。P0/P1变化还混有v1/v2、variant与标题差异；固定变体控制只移除variant变化，不能生成缺失的完整v1对照。

## P2：真实v2步骤日志

白名单1,136个victim文本成员；读取前排除受限步骤与别名/不确定路径，未全解压。385执行-step对195逻辑step、34模拟，Sampled7,339行、Full680,280行。Sampled每源10行，Full仅获准filtered步骤，并非全部原始攻击历史。

{show(p2core)}

P2的query与step-macro可能明显不同，必须保留两列。不同版本共享大量原执行，当前没有外部测试。完整日志未稳定全面胜过采样，信息增量与计算成本不能伪装算法增益。

## 来源、知识、预算与负结果

四种简单来源融合及字符表示已构成比旧词汇参考更充分的对照。K2最高MRR的简单归一化来源BM25优于旧BM25；但对去标题native的收益较小，且字符表示在P1/P2常更强。候选行级区分性/来源校准完整机制没有压过合理最强基线。NoSourceCalibration某Top10较高，不据此事后改主方法。

知识K0—K4均实测。K3删显式标题但不保证正文没有名称；13缺描述候选保留在主216空间，K4仅分析删负候选/改变IDF的影响。输入记录40与2048非空白regex-token的固定预算控制见reports/BUDGET_CONTROL_REPORT.md，所有比较方法共用相同source内容。

{table(ss,['protocol','method','logical_steps','mean_top1_pair_agreement','mean_top10_jaccard','mean_mrr_variance','distinct_input_sum'])}

相同输入确定性一致性与不同样本重叠分别列RESAMPLING_STABILITY_RESULTS.csv。这里只报告描述性变化，不用975查询当独立试验做显著性。7场景/执行分组见GROUPED_VALIDATION_RESULTS.csv；未见技术与依赖未认证问题均保留。

## 泄漏、错误与复现资格

v2原生日志中的audit/告警确实携带标签。初次未清洗试跑已作废隔离，最终全部用逐原行清洗重建输入重跑；修改101,179行、原直接ID101,759处，残余0。行数/索引保留，空行不删除，不改变窗口随机消费。P0旧目录/成绩未修改，21项源hash最终复核。

SOURCE_EVIDENCE_TRACES.jsonl保存实际候选top3行ID/hash、源贡献、公开知识哈希；独立重算62,560条来源trace的预测分数重构误差0。这仍是RANKING_EVIDENCE_CANDIDATE，不是证据Gold。原实验trace还保留代表性单行供检索说明，不能把它当完整逐行分解。8个真实错误案例见METHOD_ERROR_ANALYSIS.md：泛词可驱动误排，行为可观察不等于最终结果已实现。没有自动把未命中判为不可观测/标签错误。

本地语义模型EMBEDDING_BASELINE_RESOURCE_BLOCKED；TREC/APTREC无新认证核心资产，OCR-APT只有已有组件，KnowHow仅旧字典适配资格。具体阻断见reports/EXTERNAL_METHOD_STATUS.md与BASELINE_REPRODUCTION_STATUS_V2.csv。算法环境/完整预测/命令/共享批次耗时及NOT_CAPTURED退出码均如实保存。

## 下一阶段决定

候选机制作为本轮论文核心 **NO-GO**，不以弱BM25对照或单个Top10消融制造创新。下一步需要冻结独立执行/新数据及合格语义模型资源，围绕可审查错误验证行为证据而非泛词相关性；只有真实单轮证据缺口与合理调用授权俱备时才考虑LLM/Agent。当前可发表性尚需独立算法增量、强语义对照及独立泛化证据。

代码在baselines/、method/、datasets/build_v2.py；全部有效预测STRONG_BASELINE_PREDICTIONS.jsonl，原生来源向量SOURCE_LEVEL_TECHNIQUE_SCORES.jsonl，完整输入/版本/授权manifest均保留。旧研究不动，服务器不写，模型调用0。完成后停止。
''')
 write('README.md','''# 本轮交付

入口：R3_TECHNIQUE_STRONG_BASELINES_GENERALIZATION_RESULTS.md。主状态STRONG_BASELINES_EXTENDED。P0已曝光开发、P1重采样与P2 v2共享执行，不是独立Test。完整候选机制未证明超强对照，负结果保留。所有指标来自真实有效预测；初始未清洗试跑隔离，不用于最终表。

复跑顺序与环境见BASELINE_RUNTIME_REPORT.md；数据许可/安全范围见P1/P2 manifest，禁步过滤必须先于读取。读取日志只作文本，不执行其中命令。最终完整性检查见results/DELIVERY_VALIDATION.json。
''')
 dump('results/DECISION_SUMMARY.json',{'primary':'STRONG_BASELINES_EXTENDED','secondary':['RESAMPLING_AND_V2_PROTOCOLS_READY','PARTIAL_COMPLETION_WITH_DOCUMENTED_BLOCKERS'],'new_method_gain_proven':False,'independent_generalization_proven':False,'P0_conditions':len(p0),'P1_conditions':len(p1),'P2_conditions':len(p2),'P0_K2_nonablation_best_top1':best1,'P0_K2_nonablation_best_top10':best10,'P0_K2_nonablation_best_mrr':bestm,'prediction_rows':flat_count,'external_llm_calls':0})
 print('reports and artifacts generated',len(receipts),flat_count)
if __name__=='__main__':main()
