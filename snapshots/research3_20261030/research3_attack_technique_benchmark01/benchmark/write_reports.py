import csv,json,hashlib,statistics,subprocess,sys,re
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(n):return json.loads((R/n).read_text())
def rows(n):return list(csv.DictReader((R/n).open()))
def write(n,s):(R/n).write_text(s.strip()+'\n')
def dump(n,s):write(n,json.dumps(s,indent=2,ensure_ascii=False))
def csvwrite(n,rs):
 with (R/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def table(rs,keys):
 return '| '+' | '.join(keys)+' |\n| '+' | '.join(['---']*len(keys))+' |\n'+'\n'.join('| '+' | '.join(str(r.get(k,'N/A')) for k in keys)+' |' for r in rs)
s=load('results/SUMMARY.json');qs=[json.loads(x) for x in (R/'STEP_LEVEL_DATASET.jsonl').read_text().splitlines()];b=rows('BASELINE_RESULTS_P0.csv');hist=rows('OFFICIAL_METRIC_RECALCULATION.csv');pc=rows('OFFICIAL_PREDICTION_COUNTS.csv');dev=rows('METHOD_ABLATION_RESULTS.csv');ka=load('ATTACK_KNOWLEDGE_VERSION.json');leak=rows('datasets/manifests/input_leakage.csv')
metrics=['top1_accuracy','top5_accuracy','top10_accuracy','precision_at_5','recall_at_5','mrr']
randomrows=[x for x in b if x['method'].startswith('Random')]
ran={'method':'Random (5 registered seeds mean)',**{k:statistics.mean(float(x[k]) for x in randomrows) for k in metrics}}
main=[ran]+[x for x in b if x['input_view']=='strict']
main+=[{**x,'method':x['method']+' [author historical]'} for x in hist if x['denominator']=='all eligible queries; missing=zero']
display=[]
for x in main:
 display.append({'Method':x['method'],'Top-1 %':f"{100*float(x['top1_accuracy']):.2f}",'Top-5 %':f"{100*float(x['top5_accuracy']):.2f}",'Top-10 %':f"{100*float(x['top10_accuracy']):.2f}",'P@5':f"{float(x['precision_at_5']):.4f}",'R@5':f"{float(x['recall_at_5']):.4f}",'MRR':f"{float(x['mrr']):.4f}"})
scoretable=table(display,list(display[0]))
archive=R.parent/'rp3_existing_data/cam_lds_zenodo_v2/manifestations_filtered.zip'
md5=hashlib.md5(archive.read_bytes()).hexdigest()
write('OFFICIAL_DATA_ASSET_AUDIT.md',f'''# 官方资产审计（2026-10-27）

确认：已有合法下载的CAM-LDS v2 filtered归档，213,771,977字节，MD5 `{md5}` 与Zenodo当前API一致。SHA256见清单，与旧ACQUISITION一致。本轮不解压、不读取归档成员正文，不重复下载。旧下载许可限定的21文件范围不被当作本轮任意旧文件读取授权。

新取得：官方仓库提交 `{ka['official_commit']}` 的查询、标签、历史响应、知识矩阵、README、GPL-3.0许可证和评价/生成脚本。仓库JSON后缀中，查询与响应实际是JSONL，不能用json.load读取整个文件。

官方预制查询来自v1；不能宣称它是v2重建查询。v2包含不同Docker audit事件，见官方README。本轮P0受限子集：{s['eligible_queries']}记录、{s['unique_scenario_steps']}场景步骤、{s['selected_simulations']}个被选择的模拟执行标识、7场景、{s['parent_gold_classes']}父技术（原粒度{s['raw_gold_classes']}ID）。多父标签{s['multi_label_records']}/975={s['multi_label_records']/975:.2%}，57/195步骤。母文件990查询/198步；排除场景1的35—37步全部变体共15查询。受限正文不进入解析/模型输入；标签文件只使用metadata键。

无缺失标签、无query/official-label冲突、无空日志输入。清洗后385种不同提示词，590条为重复内容。五次采样绝非五次独立攻击。标签来源资格为AUTHOR_ASSIGNED_TECHNIQUE，未人工逐条认证LOG_EVIDENCE_OBSERVABLE或TECHNIQUE_CONFIRMED_FROM_LOG。

查询允许本地新推理；公开历史响应只用于AUTHOR_PREDICTION_METRIC_RECALCULATION及离线误差分析。没有重跑LLM。数据CC-BY-4.0、代码GPL-3.0；本轮私有研究副本不构成公开再分发许可判定。官方matrix无版本号/描述/弃用状态字段，因此不能认证确切ATT&CK发行版本。

清单包含绝对路径、文件大小、SHA256、固定提交与取得方式。旧CAM目的卡未当作技术GT。''')
write('DATA_ACQUISITION_LOG.md',f'''# 取得日志

2026-10-27（Asia/Shanghai）。先rg审计已有文件，发现v2 filtered本地归档，复用并核验MD5/SHA256；没有下载原始大归档/PCAP/模型。

网络最初在沙箱内DNS不可用；获准的网络读取取得公开GitHub API元数据与固定提交原文件。约45MB轻量仓库资产（主要是35MB历史预测），不是攻击程序运行。URL格式：https://raw.githubusercontent.com/ait-aecid/attack-manifestations-interpretation/{ka['official_commit']}/<filename>。

Zenodo API：https://zenodo.org/api/records/18861762；论文全文HTML：https://link.springer.com/article/10.1007/s10207-026-01318-x 。保存原HTML及抽取文本，实际阅读方法、实验设置、指标、结果、局限及官方README更正。未以摘要代替全文。

本地已有MITRE16.1描述与KnowHow字典只用于另列扩展知识条件，来源与哈希见ATTACK_KNOWLEDGE_VERSION.json和KNOWHOW_ADAPTATION.json。不得把16.1补充内容说成作者同版知识。

服务器只进行SSH只读连接检查：沙箱第一次禁止联网，允许网络后BatchMode认证返回Permission denied(publickey,password)，未发远程命令；未使用密码或改变服务器。当前数据和实验均在本地就绪，因此该连接失败不阻止本轮。无密码写入文件、无服务器安装/下载/实验。

外部检索：TREC作者PDF可读；APTREC出版社页面403，使用已有正式全文与审计；KnowHow既有官方源码与字典可用。所有新模型调用0。''')
write('LABEL_NORMALIZATION_RULES.md','''# 标签规范化

Gold保留原子技术集合，再归并父技术，去重；预测按原顺序归并父技术并去重，截取Top10。T1059.004→T1059。合法格式为大写化后完整匹配T四位数字或T四位数字.三位数字。Gold缺失/非法会使评分失败，不会静默删除。

主检索候选空间只用官方matrix的216父技术，不从测试频数或历史幻觉扩展。官方兼容历史模式复刻作者split('.')及原顺序去重规则，包括保留未验证的字符串，用于精确对照。严格模式将非法或不在候选空间的预测作为__INVALID__占据排名，不能因删掉错误项抬高后续预测。

官方matrix691项包含父技术和子技术，缺revoked/deprecated元数据；保持作者空间，不自行删除。扩展STIX知识排除被标记废弃/撤销的描述条目，不改变216候选。父级与子级结果不混算；当前没有报告子级模型性能。''')
protocol='''# ATT&CK技术评价协议V1

冻结文件manifests/PRE_REGISTRATION.json在首轮评分前写入。本轮为P0_RESTRICTED_195，非完整P0：场景1的35—37步全部变体正文被排除，保留195步×5=975记录。官方预制v1查询使用官方get_llm_responses.py的八条正则清洗，去掉固定指令前缀，仅提供日志body、主机/来源标题。历史prompt逐条hash与清洗后查询配对，所有4868响应匹配；重复hash用出现顺序，无法恢复缺失响应对应的同文本replica时不影响输入/GT指标。

基本单位是有官方标签的攻击步骤采样记录。主表为975记录等权平均，每步恰5条，相当于先步内平均再步间平均。模拟/场景不是独立均匀抽样，不能以975作为独立攻击次数。分组显著性本轮未计算。

Top1/5/10：前K命中任一Gold。P@K：去重的命中数/K，短预测仍以K为分母。R@K：命中数/Gold父技术数。MRR@10：第一个命中排名倒数，未中为0。F1@5预注册，micro对975集合计数累积，macro对全部216候选（无支持且无预测为0）；另列仅Gold出现79类宏平均。无阈值搜索、无事后选择最佳K。

格式错误/空/缺失预测均保留分母，记为空预测，另列失败计数。Gold缺失直接中止并记录数据错误。作者历史主对照保留官方已有响应分母，同时补充全975缺失=0分母。Ministral缺7响应，不能悄悄过滤。

P1独立：本轮只在场景7的12步60条官方采样上比较来源/标题/解码视图，名P1_OFFICIAL_SAMPLED_VIEW_ABLATION_NOT_V2_FULL_LOGS。不是v2全步骤数据，也不是与作者完全同输入的P0。

官方matrix为216父ID；名称+子技术名+战术是基础知识，MITRE16.1描述是额外知识扩展（203父技术能补齐，13父技术无描述）。LLM历史输入不含这套显式检索文档，不能将知识输入条件视为完全相同。所有新算法CPU离线、外部模型调用0。
'''
write('ATTACK_TECHNIQUE_EVALUATION_PROTOCOL_V1.md',protocol)
dump('METRIC_SPECIFICATION.json',{'protocol':'P0_RESTRICTED_195','ks':[1,5,10],'mrr_max_rank':10,'precision_denominator':'fixed K','gold':'set of official normalized parent IDs','ranking':'normalize parents then stable dedupe','invalid_strict':'retain invalid rank slots','historical_compatibility':'author exact normalization','missing_prediction':'empty list; score zero; keep denominator','missing_gold':'raise error','f1_k':5,'macro_universe':216,'gold_present_macro_universe':79,'aggregation':'sampling records equally weighted; 5 per eligible step','inference_unit':'step sampling replica','independent_statistical_unit':'execution or stricter scenario/template component; no significance claimed'})
write('METRIC_UNIT_TEST_REPORT.md','''# 评价器单元测试

12/12 PASS，见results/unit_tests.log。覆盖单标签、多标签部分命中、全错、父技术归一化、重复预测、非法ID、候选空间外ID、短列表、空预测、缺失Gold报错、同一步骤多replica、不同step同文本。测试用构造标签仅为逻辑控制，未用作研究性能数据。

另外5个历史模型的实际指标与未改官方脚本逐项比较，最大误差1.14e-15（浮点求和次序）。历史响应匹配需要作者真实清洗规则；该差异已修复，未修改结果表凑分。正式运行命令和退出码见results/OFFICIAL_RUN.json。''')
write('OFFICIAL_VS_LOCAL_EVALUATOR_CHECK.md','''# 官方与独立评价器核验

未改get_statistics.py成功执行，命令/退出码见results/OFFICIAL_RUN.json，输出见results/official_stdout.txt及官方CSV。历史模型输入为排除受限步骤后的4868条，标签来自官方metadata键。random-trials显式设5，仅控制官方附加随机比较，不影响五模型的确定性评价行；不冒充README默认1000次随机试验。

独立evaluate_techniques.py在official_compat模式对五模型的Top1/5/10、P@1/5/10、R@1/5/10及MRR全部一致，最大绝对差约1.14e-15，见results/evaluator_deltas.json。扩展F1@5非官方脚本输出。官方weighted_MRR未列为本项目主指标；保持官方原CSV，不自行宣称该辅助项已独立验证。

README全量数字只存PAPER_REPORTED_RESULTS.csv。完整4943响应/198步未重算，因为必须排除受限正文；本轮不能宣称原论文完整复现。按975全分母的Ministral行另列，不能强行与其官方968有效响应行一致。

官方稳定性代码还有可能的问题：run_id按scenario_variant计数而stability按scenario-step聚合；rank_stdev某些组重复append，且实现用样本标准差。未修补/宣称稳定性完全复现，本轮仅验证分类指标。''')
raw_ids=sum(int(x['raw_direct_ids']) for x in leak);changed=sum(x['official_clean_changed']=='True' for x in leak)
write('LABEL_LEAKAGE_AUDIT.md',f'''# 输入泄漏审计

原始llm_queries正文中检测到{raw_ids}次T四位数字串，{changed}条查询经作者清洗后改变。历史响应存储的prompt是清洗后的文本：因此直接拿query原文做基线会与LLM历史输入不一致，并可能泄漏audit key答案。本轮严格照get_llm_responses.py八条正则复刻，所有可用历史prompt逐条配对成功。

Clean Official View和Strict No-Label View都不含ground_truth/metadata/scenario/variant/step/cmd/AttackMate字段，固定指令前缀移除。严格视图补删显式技术ID及mitre/technique/tactic字段。本次两视图完全相同（strict_changed=0；正则T-ID残余0）。命令、路径、程序名、端口、系统调用、Web请求仍保留。

预测器独立进程只接受{{sample_id,text}}；sample_id原样返回，不用于排名；worker不打开标签、历史响应或测试映射。公开候选文档来源与版本冻结，ID用于索引不拼进检索正文。KnowHow使用公开字典，不读测试GT。评价由父进程单独配回Reference View。

Metadata-only诊断只用simulation_id和step_id经同一BM25名称检索，Top1=0.5128%、Top10=5.6410%。这一个弱诊断不能证明不存在更复杂捷径；若允许用官方label_key查表会得到答案，该行为明确禁止。

本轮已做结构与显式标签字段审计；未对全部自然语言嵌入答案逐人工复审，不能认证完全无隐性提示词泄漏。仓库公开历史模型也可能有预训练污染，无法据现有材料排除。''')
dump('INPUT_VIEW_MANIFEST.json',{'official':{'path':str(R/'datasets/prediction_view_official.jsonl'),'rules':'exact eight regexes in get_llm_responses.py, remove common task preamble','source_dataset_version':'v1 official persisted queries'},'strict':{'path':str(R/'datasets/prediction_view_strict.jsonl'),'rules':'official + residual direct ID/annotation removal','changed_records':0},'reference':{'path':str(R/'datasets/reference_view.jsonl'),'predictor_access':False},'metadata_diagnostic':'simulation_id + step_id lexical BM25; no label lookup','forbidden':'scenario1 step35-37 all variants skipped before JSON parsing prompt bodies'})
# Execution/template and content dependencies
prompt_groups=defaultdict(set)
for q in qs:prompt_groups[q['source_hash']].add(q['scenario_id']+'-'+q['step_id'])
across=sum(len(g)>1 for g in prompt_groups.values())
simcounts=Counter(q['scenario_id'] for q in qs)
write('EXECUTION_GROUP_LEAKAGE_AUDIT.md',f'''# 执行分组审计

975样本来自195个场景步骤，7场景、34被抽选模拟执行ID。385个不同清洗prompt，590个重复项，跨scenario-step完全相同prompt簇{across}个。源内容哈希、simulation/variant/step/replica均保留。各场景记录数：{dict(simcounts)}。

P0无训练，TF-IDF仅fit公开知识文档，不fit测试日志；训练先验/日志实例检索不适用。绝不随机拆散五replica训练/测试。

METHOD_DEV固定场景7，METHOD_TEST为场景1—6，仅基准描述评分；没有用这些测试错误调新方法。全部公开P0基线分数已曝光，后续不能称它们是永未见测试集。精确hash不是模板泄漏的充分检查；实体变化/共享命令模板仍未全面聚类，因此S1/S2监督泛化尚未认证。''')
write('GENERALIZATION_PROTOCOL.md','''# 泛化协议

S0已运行：官方公开查询受限195步零样本描述检索，无监督训练数据。S1独立执行分组与S2场景分组具备字段基础，但不能自动声称合法few-shot拆分。先对同step replicas、相同prompt、相同攻击脚本/模板与命令实体归一化哈希做连通合并，再按依赖组划分，报告训练/测试类交并集和未见技术数。

本轮不创建训练集，因此TrainingOnlyTechniquePrior与LogInstanceRetrieval为N/A，而非用全体测试Gold训练。开发机制只使用预先固定场景7；其12步60条高度相关，不能做60个独立试验的显著性推断。下一轮泛化验证必须重新冻结独立执行/新场景或新数据；当前全P0分数是公开描述性基准。

P1现有仅采样输入视图消融。更完整v2步骤日志、raw/filtered、前序上下文、子技术评价暂未运行；需要读取合规成员并冻结与v1差异，不得用未来步骤信息冒充在线推断。''')
register=[]
for name,status,scope in [('RandomRanking','RAN','5 registered seeds'),('LexicalTechniqueMatching','RAN','official names and extension'),('TFIDFTechniqueRetrieval','RAN','official names and extension'),('BM25TechniqueRetrieval','RAN','official names, extension, scenario7 ablations'),('KnowHow','ADAPTATION_RAN','public dictionary substring ranking; not full KnowHow'),('TREC','BLOCKED','missing certified model source/NOI/graph GT/splits'),('APTREC','BLOCKED','missing graphs/labels/splits/official implementation/LoRA'),('TrainingOnlyTechniquePrior','N/A','no legal training split'),('LogInstanceRetrieval','N/A','no legal independent train/test split')]:
 register.append({'method':name,'status':status,'scope':scope,'environment':str(R/'venvs'/name) if (R/'venvs'/name).exists() else 'N/A'})
csvwrite('STRONG_BASELINE_REGISTER.csv',register)
envs=[]
for env in sorted((R/'venvs').iterdir()):
 py=env/'bin/python'
 info=subprocess.run([str(py),'-c','import sys,json;print(json.dumps({"executable":sys.executable,"prefix":sys.prefix,"base_prefix":sys.base_prefix,"version":sys.version}))'],capture_output=True,text=True,check=True)
 freeze=subprocess.run([str(py),'-m','pip','freeze'],capture_output=True,text=True,check=True)
 check=subprocess.run([str(py),'-m','pip','check'],capture_output=True,text=True)
 envs.append({'algorithm':env.name,**json.loads(info.stdout),'pip_freeze':freeze.stdout,'pip_check_exit':check.returncode,'pip_check_output':check.stdout,'status':'execution environment ready; does not mean missing models are installed'})
dump('manifests/ENVIRONMENT_MANIFEST.json',envs)
rt=rows('results/runtimes.csv')
write('BASELINE_RUNTIME_REPORT.md',f'''# 运行与复现

全部新推理在本地独立算法命名虚拟环境中执行，Python3.12.14、标准库CPU实现、无额外算法依赖。每个预测进程只读prediction_view与公开知识，输出独立experiment JSONL。每次命令、耗时、退出码、stdout/stderr见experiments/*receipt.json；环境实测sys.executable/prefix、pip freeze/check见manifests/ENVIRONMENT_MANIFEST.json。TREC/APTREC只有隔离空环境，不冒充已配置原模型。

{table(rt,['method','view','knowledge','seconds','n'])}

方法总运行时间见results/SUMMARY.json，不含下载、人工核查和报告。实际Token/API成本=0，外部模型调用0，模型权重下载0，服务器写入0。源码中的get_llm_responses.py只做静态阅读，从未import/执行。

重跑：在本目录执行`venvs/Benchmark/bin/python benchmark/test_metrics.py`、`venvs/Benchmark/bin/python benchmark/run_benchmark.py`、`venvs/Benchmark/bin/python method/run_dev.py`、`venvs/Benchmark/bin/python benchmark/write_reports.py`。命令会覆盖本轮生成结果；先复制目录保留当前交付。用户旧研究目录不在写入范围。''')
write('TREC_REPRODUCTION_STATUS.md','''# TREC复现状态

本轮重新访问作者17页PDF https://nesa.zju.edu.cn/download/TREC.pdf ，确认原始任务是溯源子图、恶意节点/子图采样、Siamese few-shot识别。DOI10.1145/3658644.3690221，CCS2024。它不能接任意文本就称原方法。

已存在的本地审计：../provenance_baserepro_11/reports/TREC_FULL_AUDIT_SUMMARY.json；../provenance_baserepro_11/delivery/TREC/results/REPRO_REPORT.md。旧审计完成298 JSON成员、48,987,382事件、43技术目录；这是历史数据审计，不是本轮重读全量或模型运行。技术目录是脚本类别元数据，不能当成已认证473图样本/NOI/图边界/划分。

本轮新增TREC专属本地标准库环境，未安装替代GNN，无原模型推理。缺认证官方方法源码/模型、论文图标签/NOI边界、few-shot代表集与划分、CAM输入到对应图及标签的有效转换。P0成绩N/A，状态PARTIAL_REPRODUCTION_WITH_BLOCKERS。未发作者邮件。''')
write('APTREC_REPRODUCTION_STATUS.md','''# APTREC复现状态

DOI10.1016/j.comnet.2026.112146；出版社当前页面403，未绕过。使用已有正式20页全文与已保存审计：../provenance_baserepro_11/reports/APTREC_REPRODUCTION_REQUIREMENTS.md、../provenance_baserepro_11/sources/APTREC_FULLTEXT.txt。已有全文SHA2567748491f8c9106791c311edba76e47e88d5db473b84853a86b616fb438a2e030。

已知原方法以子图和LLM微调/多通道仲裁识别技战术，第19页数据按请求提供。现有Prompt图不等于完整可执行模板；缺原图集/GT/划分、认证实现、确切基础模型与LoRA权重、1862规则文件。保留旧审计指出的图表汇总口径与学习率/仲裁规则差异待澄清，不据此断言论文错误性质。

本轮仅建隔离APTREC环境，未下载权重、未调用模型/微调，原性能与CAM适配指标均N/A。不从摘要编写替代方法冒充APTREC。状态PARTIAL_REPRODUCTION_WITH_BLOCKERS。''')
know=next(x for x in b if x['method']=='KnowHowDictionaryAdaptation')
write('KNOWHOW_TECHNIQUE_ADAPTATION_REPORT.md',f'''# KnowHow知识字典适配

复用../research3_baseline_reproduction01/algorithms/KnowHow/original_source/tech_dic.txt，哈希见manifests/KNOWHOW_ADAPTATION.json。固定已有官方提交19a549cf3e8affd8da66004dbf2d566a34f0589c。安全ast.literal_eval读取纯字典，没有运行eval、日志命令或原techtag入口。185父技术、11803非空短语（保留原重复），只允许216候选；其余候选得0。

适配评分：严格公共日志正文中每短语出现记1，跨子技术父级累加，按得分降序及ID升序Top10。这是本项目改写排名接口，不是作者原字段分数、完整嵌入KnowHow、原论文图/攻击意图结果。独立KnowHow环境运行，输入与其他方法相同，日志标签不进入。

Top1={100*float(know['top1_accuracy']):.2f}%，Top5={100*float(know['top5_accuracy']):.2f}%，Top10={100*float(know['top10_accuracy']):.2f}%，MRR={float(know['mrr']):.4f}。词典存在短片段、重复及一般词，共现可能产生弱区分性；本轮未手工删改以迎合测试答案。其知识量、来源版本与BM25不同，不能归因全为排名机制。

完整KnowHow仍缺CTI/CKD、模型/训练、配套原始图标签和评价配置。旧139 Fact上的分数未混入本表。''')
# Paper and README reported numbers kept separate
readme=(R/'official_sources/README.md').read_text();published=[]
for line in readme.splitlines():
 if '|' not in line:continue
 cells=[x.strip() for x in line.split('|')]
 if len(cells)==14 and cells[0].startswith(('meta-llama/','mistralai/','openai/','qwen/')):
  published.append(dict(zip(['model','n_records','top1','top5','top10','mrr','weighted_mrr','p1','r1','p5','r5','p10','r10'],cells)) | {'source':'official README full198 steps; not project inference'})
# The line has 13 columns (split strips no leading table delimiters)
if not published:
 for line in readme.splitlines():
  cells=[x.strip() for x in line.split('|')]
  if len(cells)==13 and cells[0].startswith(('meta-llama/','mistralai/','openai/','qwen/')):
   published.append(dict(zip(['model','n_records','top1','top5','top10','mrr','weighted_mrr','p1','r1','p5','r5','p10','r10'],cells)) | {'source':'official README full198 steps; not project inference'})
published.append({'model':'GPT5.5_paper_narrative','n_records':'198 steps x5','top1':'0.418 (rounded)','top5':'N/A in inspected narrative','top10':'0.672 (rounded)','mrr':'N/A in inspected narrative','weighted_mrr':'N/A','p1':'N/A','r1':'N/A','p5':'N/A','r5':'N/A','p10':'N/A','r10':'N/A','source':'paper section5.2.2 DOI10.1007/s10207-026-01318-x; separate from README precision'})
csvwrite('PAPER_REPORTED_RESULTS.csv',published)
# Joint failure comparison from same legitimate sample IDs
preds=[json.loads(x) for x in (R/'BASELINE_PREDICTIONS.jsonl').read_text().splitlines()];pi={(x['method'],x['input_view'],x['sample_id']):x['predictions'] for x in preds}
# Recreate author matching using normalized saved sanitized responses and official clean hashes.
sys.path.insert(0,str(R));sys.path.insert(0,str(R/'benchmark'))
from run_benchmark import official_clean
mapping=defaultdict(list)
for q in qs:mapping[(q['scenario_id'],q['variant_id'],q['step_id'],q['source_hash'])].append(q['sample_id'])
hp={};ct=Counter()
for line in (R/'official_sources/llm_responses.json').open():
 h=re.match(r'\{"scenario": "([^"]*)", "variant": "([^"]*)", "step": "([^"]*)"',line)
 if h.group(1)=='1' and h.group(3).split('_')[0] in {'35','36','37'}:continue
 j=json.loads(line)
 if j['canonical_slug']!='openai/gpt-5.5-20260423':continue
 key=(j['scenario'],j['variant'],j['step'],hashlib.sha256(j['prompt'].encode()).hexdigest());sid=mapping[key][ct[key]];ct[key]+=1
 hp[sid]=list(dict.fromkeys(str(x).strip().upper().split('.')[0] for x in j['response']['techniques']))
failures=[]
for q in qs:
 gold=set(q['normalized_technique_labels']);sid=q['sample_id']
 bm=set(pi[('BM25_K16_1','strict',sid)][:10]);tf=set(pi[('TFIDF_K16_1','strict',sid)][:10]);ll=set(hp[sid][:10])
 if not(gold&bm) and not(gold&tf) and not(gold&ll):
  failures.append({'sample_id':sid,'scenario_id':q['scenario_id'],'step_id':q['step_id'],'gold':';'.join(sorted(gold)),'log_line_count':q['log_line_count'],'sources':';'.join(q['log_source_ids']),'split':'dev' if q['scenario_id']=='7' else 'baseline_descriptive_test_not_for_tuning'})
csvwrite('results/JOINT_FAILURES.csv',failures)
hard=sorted(rows('results/per_technique_errors.csv'),key=lambda x:(float(x['label_recall_at_10']),-int(x['n_records'])))[:16]
write('BASELINE_ERROR_ANALYSIS.md',f'''# 实际误差分析

{scoretable}

本轮是可信的检索参考线，不等于已覆盖当前最强可运行模型。名称知识BM25 Top10=18.05%，加旧版描述21.23%；TFIDF Top1从1.13%到5.33%，说明知识内容有量化影响，但13候选无描述、知识版本/长度改变，不是独立算法贡献。

BM25_K16_1、TFIDF_K16_1与作者GPT5.5同时Top10完全未命中的采样记录{len(failures)}条、涉及{len(set((x['scenario_id'],x['step_id']) for x in failures))}步，见results/JOINT_FAILURES.csv。该共错集合不证明日志不可观测。错误按技术与来源分组见per_technique_errors.csv、observable_strata.csv；不能据模型错误反向给日志标成无证据。

低标签召回示例（父技术Gold自身是否进入Top10，区别于任一Gold命中）：

{table(hard,['method','technique','n_records','n_steps','label_recall_at_10'])}

多Gold285/975，TopK只中一个便算成功，会掩盖漏掉其余技术，因此同时保存R@K/F1。来源有audit或没有audit只是可观测性代理，不是证据完整性的人工GT。当前没有完整v2/未采样日志对照，不能把失败确定归因为采样。技术描述相似与审计字段噪声是合理假设，尚未建立逐例因果证明。不得称所有错误都是LLM不理解日志。

开发消融显示audit子集/去来源标题有Top10小幅改善，解码无改善。只在12步上成立，来源预算不等，不推广到跨执行泛化。''')
write('BASELINE_FAILURE_TAXONOMY.md','''# 失败分类与证据资格

已确认：词汇检索性能低；285多标签采样；590重复提示词；7个缺失历史响应；显式audit标签清洗必要；部分父候选缺扩展描述；开发来源视图改变排名。

合理推测：技术描述自然语言与原生日志命令/实体词汇不一致，冗长异构日志稀释排序；共享命令/相似技术描述可致混淆。它们不是已验证因果结论。

暂无法验证：逐条失败是否因关键事件缺失、采样丢失、执行失败、时间窗口误标、完整攻击结果未出现或预训练数据污染。本轮没有用模型对错自动生成这些标签。

后续人工审计只能在开发组逐步骤检查日志见证，区分日志无命令/有命令但执行结果不明/证据充分仍错排；保留反例与竞争技术，不能把推测升级为GT。''')
write('METHOD_HYPOTHESIS.md','''# 开发假设

前置条件已满足：评价器一致、输入视图冻结、四项检索基线实际运行。固定场景7为开发，不依据其他场景错误设计规则。

H1：audit十六进制进程参数可读化改善描述检索。实现只做bytes.fromhex→UTF8文本追加，无命令执行、无新关键词。结果无提升，保留负结果。

H2：主机/来源标题或不同来源的弱相关日志稀释排名，来源内检索再融合可能改善。开发仅执行最小必要对照：all、保持所有事件和续行但去标题、audit-only、non-audit-only。Top1仍0，不能把Top10变化包装成创新。

候选科研问题：能否根据可追溯事件见证而非测试答案，控制多源证据稀释与相似技术归因？下一项实验应在开发组做冻结来源权重的late fusion与等预算对照，并单列全部Gold覆盖/无证据归因率。LLM证据验证尚未授权，当前只能准备协议。''')
write('METHOD_RESEARCH_DECISION.md',f'''# 科研决策

主状态BASELINES_READY_METHOD_UNPROVEN；辅状态OFFLINE_STRONG_BASELINES_READY、PARTIAL_REPRODUCTION_WITH_BLOCKERS。P0为受限195步，完整198步与v2全日志尚未认证。

{table(dev,['case','n_records','empty_inputs','top1_accuracy','top10_accuracy','mrr'])}

解码无效；来源选择和去标题在12步开发组有小幅Top10/MRR变化，但Top1仍0，不能证明可发表机制或独立增益。无需立即开发复杂Agent。最值得下一次验证的是来源内归一化检索/证据融合，与等长度/去标题对照及所有Gold召回联合比较；先在开发执行固定消融，再冻结独立执行数据测试。不能继续用全部已曝光P0反复优化。

当前具备技术识别基准实验基础，尚不具备“新算法优于强竞争方法”证据。外部完整TREC/APTREC仍被配套资产阻断。技术排名可连同sample_id、source_hash、执行/步骤顺序、日志来源和不确定证据回查接口留给后续操作目标理解，不能直接转为目标Gold或意图成绩。

P1完整版、跨步骤上下文、子技术/战术推理、LLM重推理均N/A：本轮未取得相应冻结输入/授权/模型条件。''')
# Main report explicitly answers the requested 35 questions.
gpt=next(x for x in hist if 'gpt-5.5' in x['method'] and x['denominator']=='all eligible queries; missing=zero')
answers=[
'是，v2 filtered归档本地合法下载并校验；本轮可评分主输入实际为官方v1预制查询，不能混称v2。',
'是，llm_queries.json，应用作者真实清洗后hash与公开历史prompt配对。',
'是，labels.json的metadata技术键；与查询GT集合975/975一致。',
'文件母体198步990查询；本轮排除受限3步后195步975记录，34被抽选模拟标识、7场景。',
'Gold为79父技术、94原技术/子技术ID；候选为216父技术。',
'285/975=29.23%采样、57/195=29.23%步骤含多个父技术。',
'是，按父技术归并去重，保留原Gold集合。',
'是，matrix691原ID归并216父ID；具体ATT&CK发行号未编码，不能认证。',
'未改官方分类评价脚本实际执行成功；全198步受限，因此仅复现195步分类管线。',
'可在4868合法响应上复算；Ministral缺7，列可用分母与全975分母。',
'一致，TopK/P/R/MRR最大绝对差约1.14e-15；不包括官方辅助weighted-MRR/稳定性的独立认证。',
'结构/目录/显式标签审计完成，原始query确有audit标签；清洗严格等官方历史输入。未穷尽自然语言隐性泄漏。',
'是，四项均在独立算法环境真实推理，保存每项Top10输出；还运行KnowHow字典适配与知识扩展。',
'Top1/5/10具体值见本报告实测表与BASELINE_RESULTS_P0.csv，非复制作者论文数字。',
'P@1/5/10、R@1/5/10、MRR@10、F1@5均实算保存，见同表/CSV。',
'采样日志与作者相同清洗，且同受限子集；显式检索知识与LLM内隐知识不同，扩展16.1条件另列。',
'检索/KnowHow适配是本项目新离线推理；五LLM仅作者历史响应复算，新LLM调用0。',
'逐技术低召回与支持数见results/per_technique_errors.csv；不能无视低支持和多个Gold给出稳定难度排名。',
'多Gold分组已列observable_strata；TopK命中掩盖剩余Gold漏识别，不能把所有多标签错误确定归因为多标签。',
'所有输入有日志；是否缺关键见证未逐条认证，不能把共错样本称为无可见证据。',
'描述相似是待检验机制；没有逐对受控因果证明。',
'尚无完整未采样日志对照，无法确定哪些错误由采样造成；590重复样本说明采样独立性受限。',
'旧审计有298 JSON/约4899万事件；缺认证原算法、图/NOI/标签/划分，空独立环境非模型就绪。',
'已有20页全文与审计；缺原子图GT/划分、实现、LoRA及确切基础模型，未下载权重。',
'可参与，已实跑公开字典的项目Top10适配；不是完整KnowHow原论文复现。',
'本轮运行KnowHowDictionaryAdaptation；TREC/APTREC模型未跑，指标N/A有具体资产原因。',
'是，每项算法各命名虚拟环境；manifest保留真实解释器和pip check，空环境不被当成完整模型环境。',
'有scenario/simulation/step字段，可做分组；模板依赖未完整认证，不强造few-shot划分。',
'原始query存在直接标签风险；作者正则清洗后显式ID残余0；metadata-only弱检索低分仍不能证明完全无捷径。',
f"BM25+16.1 Top10=21.23%，作者GPT5.5同子集Top10={100*float(gpt['top10_accuracy']):.2f}%，差{100*(float(gpt['top10_accuracy'])-.2123076923076923):.2f}个百分点；不是同知识预算因果比较。",
'有描述性影响：TFIDF Top1由1.13%至5.33%；BM25 Top10由18.05%至21.23%，但场景7BM25 MRR反降。',
'未能证明“更多日志必然解决”；开发audit-only好于全部而non-audit-only全错，提示输入选择问题；完整检索也仍低分。',
'存在候选问题但尚无已证实创新：部分可观测多源证据控制与相似技术的证据归因。',
'下一项优先开发来源内归一化排名/证据融合的固定对照，使用等预算与去标题控制；在独立执行上验证，保留负结果。',
'保留排名、源哈希、sample_id、执行/步骤及来源；后续另接逐项证据与目标假设，目标GT/目标指标仍须独立认证。'
]
write('R3_ATTACK_TECHNIQUE_BENCHMARK_RESULTS.md',f'''# R3_ATTACK_TECHNIQUE_BENCHMARK01 实际结果

2026-10-27，主终态 **BASELINES_READY_METHOD_UNPROVEN**。官方受限子集、统一评价与多项离线基线已就绪；外部完整论文复现仍有资产阻断。本轮没有服务器写入、攻击执行、模型下载或外部LLM调用。

## 35项科研问题逐项回答

'''+ '\n\n'.join(f'{i}. {a}' for i,a in enumerate(answers,1))+f'''

## 实际对照结果

同一195步975记录，父技术216候选。百分比列为百分数，P/R/MRR为0—1。Random为五个预注册seed均值（各seed原始预测均保留）；名称知识与描述扩展分别列出。历史LLM行是公开作者输出复算，未重新调用模型；Ministral缺失按0保留全975分母。

{scoretable}

TREC适配、APTREC适配：N/A，缺配套图标签/实现/模型条件。TrainingOnlyPrior与LogInstanceRetrieval：N/A，无独立合法训练集。本文所有检索结果只支持“实测参考线”，不宣称它们已代表当前最先进或已充分调优的强方法。

## 真实性、资格与限制

官方完整198步的论文/README成绩单列PAPER_REPORTED_RESULTS.csv，不能直接与195步表混排比较。P0预制查询来自v1，不是v2；旧v2归档已核验但本轮未读取其成员正文。官方matrix没有描述与版本，16.1扩展203父技术、13缺描述，改变了知识条件。

官方历史输入hash匹配、独立评价器与官方分类指标一致、12项单元测试通过。原始query含直接标签，应用作者清洗后方可用；严格与官方视图本次相同。385不同prompt、590重复项，975不是独立攻击次数。57多Gold步骤要求同时看Recall/F1，且官方预设标签不等于可见证据完整认证。

## 误差与决策

{len(failures)}采样记录中，BM25/TFIDF描述扩展和作者GPT5.5都未在Top10命中任何Gold。它们仍有可见日志，不能断言不可观测。具体技术/来源/多标签分组及证据资格见BASELINE_ERROR_ANALYSIS.md和results/*.csv。未知采样因果、未知完整执行成功状态、未知预训练污染均保留为未验证。

开发场景7只含12步60条。十六进制解码无提升；去标题或audit-only使Top10从8.33%到16.67%，Top1仍0。不能据此声称知识推理/LLM创新已成立。下一步最值得测试固定来源内归一化与证据融合，并用等预算控制及独立执行数据验证。当前不增加复杂Agent。

技术排名与步骤/执行/来源/哈希已保留，为后续证据映射提供接口；本轮没有独立技术证据充分性评分、战术分类成绩或完整操作目标理解成绩。

## 可复核入口

代码：evaluate_techniques.py、benchmark/run_benchmark.py、baselines/predict.py与retrieval.py、method/run_dev.py。数据：STEP_LEVEL_DATASET.jsonl及datasets分离视图。预测：BASELINE_PREDICTIONS.jsonl、experiments各进程输出、method/DEV_PREDICTIONS.jsonl。来源：OFFICIAL_DATA_MANIFEST.json及official_sources固定提交原件。环境/成本/命令：manifests/ENVIRONMENT_MANIFEST.json、experiments/*receipt.json、BASELINE_RUNTIME_REPORT.md。P1来源消融在BASELINE_RESULTS_P1.csv，不能与P0直接同口径。

主要来源：[官方代码与更正](https://github.com/ait-aecid/attack-manifestations-interpretation)、[CAM-LDS v2](https://zenodo.org/records/18861762)、[正式论文全文](https://link.springer.com/article/10.1007/s10207-026-01318-x)、[TREC作者论文](https://nesa.zju.edu.cn/download/TREC.pdf)。APTREC/KnowHow资产依据本地已有原文及官方源码审计，见各自状态报告。
''')
# Minimal interfaces for authorized future work, never invoked externally.
dump('method/FUTURE_LLM_RUNNER_CONFIG.json',{'enabled':False,'NEW_EXTERNAL_MODEL_CALLS':0,'conditions':['L0 logs only','L1 descriptions','L2 retrieved knowledge','L3 multisource context','L4 evidence verification'],'required_before_enable':['new explicit model-call authorization','fixed model/version and input budget','frozen eligible IDs','prompt hashes','evidence spans','tokens/cost/failures log'],'agent_investigation':'only after demonstrated evidence retrieval need'})
write('README.md','''# 本轮交付

先读R3_ATTACK_TECHNIQUE_BENCHMARK_RESULTS.md。主终态BASELINES_READY_METHOD_UNPROVEN。所有数值可回到固定来源、分离数据视图、逐样本Top10预测、评价代码、算法独立环境和命令回执。受限场景1的35—37步排除；模型调用0。原始上游文件只保存用于审计，禁止自动执行get_llm_responses.py或任何日志/攻击命令。

重跑顺序见BASELINE_RUNTIME_REPORT.md。生成结果可能覆盖当前版本，应先复制本目录。
''')
print('reports written',len(list(R.glob('*.md'))),'main_rows',len(display),'joint_failures',len(failures),'published_rows',len(published))
