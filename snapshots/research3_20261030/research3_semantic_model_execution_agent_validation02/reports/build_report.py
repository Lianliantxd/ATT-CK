"""Generate evidence-indexed Chinese delivery from completed offline analyses."""
import csv,json,sys,collections,datetime
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT as R,sha256,records
def read(name):return list(csv.DictReader((R/name).open()))
def write(name,text):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n')
def pct(x):return f'{float(x)*100:.2f}%'
def table(rows,cols):
 return '| '+' | '.join(cols)+' |\n| '+' | '.join('---' for _ in cols)+' |\n'+'\n'.join('| '+' | '.join(str(r.get(c,'NA')) for c in cols)+' |' for r in rows)
def main():
 e=read('EMBEDDING_REAL_RESULTS.csv');ce=read('RERANKER_REAL_RESULTS.csv');upper=read('RERANKER_CANDIDATE_UPPER_BOUNDS.csv');rec=read('EMBEDDING_CANDIDATE_RECALL.csv');stats=read('results/NEURAL_EXPLORATORY_PAIRED_STATS.csv');llm=json.loads((R/'results/NEW_LLM_SUMMARY.json').read_text());pairs=read('AGENT_PAIRED_COMPARISON.csv');cost=read('AGENT_COST_REPORT.csv')
 env=json.loads((R/'MODEL_ENVIRONMENT_MANIFEST.json').read_text());receipts=json.loads((R/'results/server_gpu/manifests/MODEL_DOWNLOAD_RECEIPTS.json').read_text());embtime=json.loads((R/'results/server_gpu/EMBEDDING_TOTAL_RUNTIME.json').read_text());cetime=json.loads((R/'results/server_gpu/RERANKER_TOTAL_RUNTIME.json').read_text())
 neural_table=table([{'方法':x['method'],'N':x['n_records'],'Top1':pct(x['top1_accuracy']),'Top10':pct(x['top10_accuracy']),'MRR@10':f"{float(x['mrr']):.4f}"} for x in e+ce],['方法','N','Top1','Top10','MRR@10'])
 upper_table=table([{'候选池':x['pool'],'K':x['K'],'CandidateHit':pct(x['Top10_candidate_upper_bound']),'无正确候选':pct(x['candidate_miss_rate']),'重排Top10':pct(x['actual_Top10']),'升入Top10':x['promoted_into_top10'],'跌出Top10':x['downgraded_out_of_top10']} for x in upper],['候选池','K','CandidateHit','无正确候选','重排Top10','升入Top10','跌出Top10'])
 pairs_table=table(pairs,['static_scope','static_method','valid_same_case_pairs','static_Top10','agent_Top10','static_MRR','agent_MRR'])
 cost_table=table(cost,['scope','method','planned_conditions','completed','attempted_model_requests','native_calls','unknown_timeout_requests','input_tokens','output_tokens'])
 write('MODEL_ASSET_AUDIT.md',f'''# 模型资产：从缺失到真实运行

一次性本地审计检查7个已知缓存、17个文件，未发现候选Embedding/CE完整资产。DistilBERT只有revision引用/锁文件，不是权重；Qwen3-Embedding与BGE-M3未发现完整资产，没有运行或下载。范围是指定缓存，不是全磁盘不存在的证明。初始审计时尚无新授权，后续授权单独记录，未改写历史审计事实。

用户随后明确授权在服务器安装GPU依赖和两个固定GTE模型，采用项目名称的新venv，并单独授权清洗P0预测输入与公开知识上传。Gold留本地。原服务器只读与每模型独立venv约束仅在本项目被明确覆盖，受限步骤和CONV-A01权限不变。

| 完整且实际运行模型 | 固定revision | 权重bytes | SHA256 |
|---|---|---:|---|
'''+ '\n'.join(f"| {x['model_id']} | {x['revision']} | {next(f['bytes'] for f in x['files'] if f['path']=='model.safetensors')} | {x['weight_sha256']} |" for x in receipts)+f'''

权重来自HF镜像，SHA256与官方文件页一致；配置和tokenizer按同一revision下载，逐文件哈希保存在MODEL_DOWNLOAD_RECEIPTS。一次tokenizer断点续传尺寸不符后，只对失败文件强制重新下载，未放松校验、替换模型或revision。官方PyPI超时后使用清华镜像安装轻依赖。失败日志保留在服务器logs。

服务器新venv为 `{env['venv']}`。复用既有torch2.11.0+cu130/CUDA13.0的只读symlink，Transformers4.57.6等安装在新venv，未改系统环境。NVIDIA A40 GPU0、显存比例cap15%、CPU2线程、FP16、SDPA、batch8、offline加载、trust_remote_code=False。每模型实测均远低3小时；项目观测占用最终1,539,144,990 bytes（约1.54GB，含V1保留），低于4GB。

本机M3/24GB统一内存适合已验证的CPU小LLM；不能写成24GB独立显存。本轮GTE没有在本机做性能资格测试，GPU资格来自服务器真实预检。单样本与8样本预检见MODEL_LOAD_TESTS.json。

本地DeepSeek完整GGUF已有且校验通过：digest a42b25d8c10a841bd24724309898ae851466696a7d7f3a0a408b895538ccbc96；本轮未下载LLM。另有7b已有缓存，但未使用它冒充1.5b新结果。

来源：[Embedding模型卡](https://huggingface.co/Alibaba-NLP/gte-modernbert-base)、[官方权重](https://huggingface.co/Alibaba-NLP/gte-modernbert-base/blob/main/model.safetensors)、[Reranker模型卡](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base)、[官方权重](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/main/model.safetensors)。
''')
 write('MODEL_DEPENDENCIES.md',f'''# 实际依赖与资源

环境：服务器Python3.12.4，torch2.11.0+cu130，CUDA13.0，Transformers4.57.6；完整锁文件为results/server_gpu/manifests/requirements-lock.txt。新venv隔离安装轻依赖，通过显式只读链接复用既有CUDA框架，不使用system-site-packages。用户要求项目名venv，因此两个顺序运行模型共享此任务环境。

Embedding：149M、768维、官方CLS取首token并float32 L2归一化、cosine排序；不是任意mean pooling。实际forward {embtime['actual_forward_batches']}批、{embtime['unique_encoded_texts']}个唯一文本；相同文本cache只减少重复forward，仍按975查询评分。模型阶段{embtime['seconds']:.2f}秒。条件GPU峰值allocated最大721152512 bytes、reserved最大1113587712 bytes，进程RSS峰值1914216448 bytes；逐条件见RUNTIME文件，最后一个条件的峰值不能冒充全阶段最大值。

Cross-Encoder：真实成对输入分类模型，官方raw logit排序，没有用Embedding假冒。{cetime['unique_model_pairs']}个唯一日志—技术对、{cetime['forward_batches']}批、{cetime['actual_pair_tokens']}实际pair输入Token；{cetime['seconds']:.2f}秒，GPU峰值allocated{cetime['memory']['GPU_peak_allocated_bytes']}、reserved{cetime['memory']['GPU_peak_reserved_bytes']} bytes，RSS{cetime['memory']['process_peak_RSS_bytes']} bytes。

阶段计时含加载与预检，GPU请求成本不计入本地LLM80次上限。离线评价和科学作图使用本机既有Python3.12.14/Numpy/ReportLab，无新大包安装。图为矢量PDF/SVG，PNG预览已目视核验。
''')
 with (R/'MODEL_EXECUTION_STATUS.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=['model','complete_weights','actual_forward','conditions','queries_each','status']);w.writeheader();w.writerows([{'model':'GTE-ModernBERT','complete_weights':True,'actual_forward':True,'conditions':5,'queries_each':975,'status':'FULL_P0_EVALUATED'},{'model':'GTE-ModernBERT-Reranker','complete_weights':True,'actual_forward':True,'conditions':6,'queries_each':975,'status':'FULL_P0_EVALUATED'},{'model':'DeepSeek-R1-1.5B','complete_weights':True,'actual_forward':True,'conditions':73,'queries_each':'78 attempted requests / 74 receipts','status':'3_VALID_AGENT_EPISODES; PARTIAL_VALID_PILOT'},{'model':'Qwen3-Embedding / BGE-M3','complete_weights':False,'actual_forward':False,'conditions':0,'queries_each':0,'status':'NOT_RUN_NOT_AUTHORIZED_DOWNLOAD'},{'model':'DistilBERT','complete_weights':False,'actual_forward':False,'conditions':0,'queries_each':0,'status':'REFERENCE_ONLY'}])
 write('EMBEDDING_ERROR_ANALYSIS.md','''# Embedding真实错误与不可归因部分

原生前缀E1的Top100仍无任一Gold比例10.36%；窗口E3为8.31%。Top100 CandidateHit分别89.64%/91.69%，不等于多标签全覆盖（74.05%/76.41%）。Hit、macro label recall、all-Gold coverage按不同定义全部交付。

E1与相同输入/知识预算的TF-IDF比较，Top10 28.72% vs29.23%，MRR .1067 vs.1401；E3与匹配窗口TF-IDF比较Top10 30.26% vs26.87%，MRR .1277 vs.1266。不能只挑Top10说模型全面改进。原历史最强TF-IDF 27.79%使用不同输入预算，保留但不是本轮matched对照。

共享原始片段的字段展开E2 Top10下降至23.38%；加入真实source/event_id/literal_fields及重复native没有新增观察，仍可能改变模型注意分布。这是合理假设，未被因果干预确认。窗口max/mean分块分别27.59%/29.13%，均低于同一窗口直接编码30.26%；分块输入相同，差别在聚合，但不能泛化所有分块方法。

逐样本可确认事实为候选缺失、Gold排名、实际可见Token、是否截断；见results/EMBEDDING_PER_SAMPLE_ERROR_AUDIT.csv和服务器NEURAL_INPUTS映射。相似技术混淆、命令语义未识别、关键证据被截断、标签不可观测、结构化理解失败都需要额外语义标注/受控反事实。本轮全部标UNRESOLVED，不用预测错误反推“日志必然缺失”。
''')
 write('RERANKER_ERROR_ANALYSIS.md',f'''# Reranker错误分解

{upper_table}

Embedding Top20：正确技术原已在前十而被降出55次，原不在前十而被升入104次，净增49/975=5.03个百分点；MRR仍下降。Embedding Top100：候选缺失101次；候选有Gold但最终Top10无Gold为750次。后者是可确认的候选内排序失败，不是召回缺失。不能把它直接命名为“主体对象理解失败”。

Lexical Top100：候选缺失186次，候选内最终前十失败693次；升入65次、跌出254次。扩大候选规模的上界提高，实际排序却下降，支持优先检查技术机制判别和相关性校准。定义—动作不匹配、尝试与成功混淆、词汇干扰均为待验证假设。逐样本原候选、原/新Gold排名、原始logit、输入哈希已保存，未删负结果。
''')
 write('AGENT_ERROR_ANALYSIS.md',f'''# Agent错误及分母

新增73个条件=1最小门槛+48预注册V3条件+24后注册V4静态控制。有效提交17，失败56：32次最终排序重复ID、20次完整输入在调用前超8192、4次实际请求超时。49份原生final中32份含重复技术ID，共144次重复出现；没有事后去重或补齐。25份其余原生响应为动作决策。超时没有原生final，不能算模型已给出语义错误答案。20个调用前context失败也不能算真实LLM语义0分。

Agent V3十二例有2条合法最终Episode，1条Top10命中。有效分母Top10=50%、MRR=.25；全12个实际调用条件保留失败为8.33%、.041667。差异来自分母，不能用前者与12条静态结果直接比较。主Pilot原始48条件全部登记，但39失败、9完成；加最小门槛才是10/49。V4静态7/24完成，4次超时计费；超时的后台实际结束时刻未知。

{pairs_table}

V3严格同案合法A1/Agent交集只有1例，双方Top10=0；V4 A1/Agent交集2例，双方Top10=.5、MRR=.25，简单静态查询复现了唯一命中。A2无合法同案Agent交集，NA。不能用“Agent .5 vs Static 0”的不同有效案例集合宣布收益，也不能据2例宣布Agent普遍无效。

真正可确认的新增能力：固定模型发起授权只读查询，完整反馈进入后续模型输入、合法引用返回事件、提交Top10、独立评价，共3个Episode通过。模型是否理解区别性证据、忽略反馈或因果改变排名仍UNRESOLVED；单纯重复获取、过早停止或查询不相关需要逐条机制判据，不能仅由错分归因。返回完整性已证明，不等于内部语义利用已证明。

新请求78/80，74份原生回执；已知输入{llm['actual_input_tokens']}、输出{llm['actual_output_tokens']}；含4次超时保留上限输入{llm['input_tokens_with_unknown_attempt_reservations']}、输出{llm['output_tokens_with_unknown_attempt_reservations']}。请求跨度{llm['request_span_seconds']/60:.2f}分钟，全部新请求在90分钟内结束等待。超时后台完成时间无法确认；随后无prompt卸载控制见LOCAL_MODEL_STOP_RECEIPT，ps为空。卸载控制约在首请求后90.9分钟，不能据此虚构超时推理在90分钟前已完成，也没有在90分钟后新增推理请求。
''')
 write('SEMANTIC_MODEL_INCREMENTAL_VALUE.md','''# 语义模型独立能力判断

已确认：固定GTE Embedding与真实Cross-Encoder均完成975查询/195逻辑步骤评价，候选216父技术。Embedding E1比matched TF-IDF的Top100 CandidateHit高8.72个百分点（89.64% vs80.92%），表明更广候选覆盖的开发性价值；早期排名没有稳定增益。窗口E3提高部分Top10，但Top1下降、MRR只微升且不稳健。字段展开与max/mean分块没有一致改善。

真实CE仅在Embedding Top20带来Top10开发性净增5.03个百分点，MRR下降；Top50/100明显退化。它不是稳定排序改进，更不是创新或泛化证据。正确候选进入池后仍大规模排错，研究重点应从“继续扩大召回”转向机制判别及可观测证据与定义的对应。该解释是研究决策，具体错误语义原因尚未验证。

P0=EXPOSED_DEV，P1/P2=RELATED_DEVELOPMENT_DATA。作者GPT-5.5历史Top10=66.67%属于公开预测复算，没有本轮外部模型调用，不能做新LLM成绩。外部独立测试未就绪。
''')
 write('LLM_AGENT_INCREMENTAL_VALUE.md','''# LLM与Agent增量能力

历史54条只有18个合格final，且条件不统一，不能证明独立语义贡献。本轮固定小LLM有74个新原生响应，3个完整Agent结构性Episode，证明工程闭环已打通。它没有证明内部机制推理或动态查询增益。

预选12例V3矩阵已记录，但上下文与重复输出导致严格配对很少。V3 A1/Agent合法交集N=1；V4后注册上下文控制N=2且双方Top10/MRR一致。当前判断是NO_SUPPORTED_AGENT_INCREMENTAL_GAIN_ON_VALID_DEV_SUBSET；不使用“Agent普遍无效”，也不使用AGENT_INCREMENTAL_GAIN_SUPPORTED_ON_DEV。AGENT_PAIRED_PILOT_COMPLETED不作为完整资格状态：48条件登记完成不等于12组方法都有效。

Agent V3的36次调用、142223输入/4010输出，与A0的12次、37090/2654相比，调用3倍、输入约3.83倍；模型耗时676.70 vs606.28秒，受缓存及输出长度影响。静态V3很多条件调用前失败，不能拿其低总模型成本推导同质量成本收益。V4 A1原生9条、另2超时；A2原生10条、另2超时，完整成本含预留上限见AGENT_COST_REPORT。

下一步先确保更可靠的固定输出合同与公平上下文容量，再谈扩大Agent实验。没有证据支持增加角色、reflection轮数或直接引入RL。动态区别性证据获取保留为待验证假设，先做同观察、同知识、同预算的证据删改干预，并设置固定查询强对照。
''')
 write('METHOD_RESEARCH_DECISION.md','''# 研究路线决策

主状态：RERANKER_BASELINE_READY。次状态：SEMANTIC_EMBEDDING_BASELINE_READY、AGENT_END_TO_END_VALIDATED。Agent配对矩阵已记录但有效配对不足，完整正式配对资格仍部分未完成；不声明增益支持。EXTERNAL_TEST_NOT_READY。

已确认事实：两种预训练模型实际运行；Embedding扩大Top100覆盖但早期排名不足；CE候选扩至100时大规模候选内错排；3个Agent工程闭环；合法严格配对子集未见动态增益。

合理推测：通用相关性表示未充分对齐日志中的主体—动作—对象及尝试/结果条件；字段重复/元数据可能引入噪声。这些不是已证明原因。

研究判断：优先研究ATT&CK机制判别与可观测证据约束，其次检查领域表示；暂停增加Agent复杂度。当前没有足够证据正式提出一个已验证的新算法机制。成熟模型串接、工具回传修复和数学符号本身都不是算法创新。

下一轮具体实验：先在现有授权开发数据上冻结30个按逻辑步骤分层的诊断案例（含候选缺失、候选内降级、稳定正确三类各10）；由独立标注者在不知道模型排序时记录可观察的主体/动作/对象、尝试/成功和“不足以支持”条件，复核标签可观测性。固定raw与可追溯literal机制表示两个视图，在相同片段预算比较TF-IDF、GTE和CE；不推断日志没有的字段。该诊断集不是测试集。新增模型调用需在新预算授权后运行，不能复用已结束额度。

之后先资格核查独立脚本/执行或外部数据，冻结真正独立测试，再训练或评估机制判别模块。Agent只有在静态机制识别可靠、受控证据增减确实改变判别时，才重新开展固定查询与自适应查询的同预算比较。无合格独立数据前不报告外部泛化，不擅自下载大型数据。
''')
 v1et=json.loads((R/'results/server_gpu_v1/EMBEDDING_TOTAL_RUNTIME.json').read_text());v1ct=json.loads((R/'results/server_gpu_v1/RERANKER_TOTAL_RUNTIME.json').read_text())
 write('INPUT_SELECTION_REPAIR.md',f'''# 空输入选择器修复：V1与V2

V1实际模型结果完整保留在results/server_gpu_v1，完整报告/CSV/图快照在reports/V1_ANALYSIS。最终V2主结果不是择优拼接，两模型全部条件均重新跑975查询，所有相同样本与失败案例都保留。差异表为results/INPUT_REPAIR_V1_V2_METRICS.csv。

最终检查发现10个prefix和7个window空视图，原始日志都非空。根因是线性减去“渲染超额”：字段展开与原生重复可使渲染超额大于所选native token数，于是n被直接减至0；外层实际tokenizer缩小代理cap时也可能触发。实际案例1-54-r1选择2048代理token，展开4356，超额2308，下一次n=0。另两个实际案例也复现，见EMPTY_INPUT_ROOT_CAUSE_TRACE.json。不是缺日志或模型返回空。

修复先复用完全冻结的旧选择结果；只有V0为空才用正数可行区间搜索，寻找满足两个实际tokenizer及代理上限2048的原始片段。非空输入不重新优化，1933个非空variant的全部可见文本逐字一致；17个空variant变非空。最终1950个prefix/window均非空、975查询、actual token cap均通过。预算字段legacy proxy诊断值来自第一遍选择；最终权威实际上限为actual_log_token_budget=2048及逐模型实际count，新增修复audit说明所选片段。

这是Gold后开发工程修复，注册明确承认此前已看总体成绩；修复条件只由空文本决定，不用Gold、单案例得分或模型正确性挑选。固定模型/知识/候选/采样和评价器均未改，不把V1到V2分数变化算成算法增益。两种模型只进行这一次修复重跑，无新本地LLM调用。

V1+V2累计模型阶段时间：Embedding {v1et['seconds']+embtime['seconds']:.2f}秒；CE {v1ct['seconds']+cetime['seconds']:.2f}秒，仍在每模型3小时以内。最后服务器项目1,539,144,990 bytes，含V1保留，低于4GB；已无本项目GPU进程。运行及wrapper哈希分别在NEURAL_RUNTIME_PROTOCOL和EMPTY_INPUT_REPAIR_V2_STARTED。

修复后E1/对应TF-IDF的Top10均增加7/975，因此二者差没有改善；E3有小幅变化，但仍无稳健统计支持。原负结果不删除，当前主表统一使用V2。
''')
 # Strict analysis bundle precedes complete wrap-up report.
 ao='reports/analysis-output/'
 write(ao+'analysis-report.md',f'''# 严格分析：配对、指标与分母

主问题：固定预训练模型在相同观察和公开知识预算下是否改善父技术排名？次问题：同固定LLM、同合法池及证据cap下动态查询是否有独立收益？

{neural_table}

原生预测13650行=5×975 Embedding+3×975 matched lexical+6×975 CE。每条件975个唯一sample_id，195个逻辑步骤、7场景、34执行标识；不是975个独立样本。全部预测先固定，Gold只在本地离线进入冻结V1评价器。MRR仅前10，父技术归一化，multi-label recall与any-Gold hit区分。

主比较E1与matched prefix lexical：Top10差-0.51个百分点，MRR差-.0335；窗口matched比较Top10+3.38个百分点，MRR差+.0011。CE Embed20对E1的Top10+5.03个百分点，MRR-.0179。26个探索性对比检验统一Holm校正，未支持CE Embed20 Top10的确认性增益。主表显示全部条件，不选择最高分作为独立测试结论。

Claim candidates：
- 两种预训练模型已全P0真实推理并评价。证据：原生GPU预测/哈希/预检/日志。允许“基线已运行”，禁止“泛化已证明”；不确定性为数据相关性；决定keep。
- Embedding Top100覆盖优于匹配词法。证据：候选召回表。允许“开发集覆盖较高”，禁止“全面排序更好”；单seed/领域限制；下一步独立数据；决定weaken。
- CE扩大候选有候选内降级。证据：排名转移表。允许“本模型本协议观察到”，禁止“所有CE不适用”；因果机制未知；下一步机制标注；决定keep。
- Agent未证明增益。证据：严格同案N1/N2且无超越。允许“未支持”，禁止“普遍无效”；功效极低；下一步输出资格和证据干预；决定weaken。
''')
 write(ao+'stats-appendix.md','''# 统计口径

seed42一次确定性推理，无训练重复；不报告跨seed mean±std。逐查询描述值与195逻辑步骤等权macro同时给出，P0每逻辑步骤5查询，宏均值一致。7场景/34执行逐组结果保存，相关执行和脚本不能当独立测试。

NEURAL_EXPLORATORY_PAIRED_STATS.csv：13个预列分析对比×Top10/MRR两指标=26项。每个逻辑步骤先平均5查询的成对差，报告195个差的mean、SD、5000次有放回bootstrap percentile95%CI，10000次sign-flip（+1修正）双侧p；全26项Holm校正。随机seed42。

条件假设：逻辑步骤对比差可交换且近似独立。相同场景/脚本可违反此假设，故这些CI/p仅为暴露开发集的探索性条件量，不能支持场景或外部泛化。离散成对差不服从正态的默认假设，因此不使用普通独立t检验。bootstrap CI与离散sign-flip p可能不完全一致；不得选择性使用CI或未校正p。

CE Embed20 vs E1：Top10 delta .050256，SD .352513，95%CI [.002051,.098462]，raw p .053695，Holm p .644336；MRR delta -.017950，CI[-.045735,.010360]，Holm p1。不能据正CI边界宣称确认性显著收益。窗口E3 vs matched TF-IDF Top10 delta .033846，CI[-.045128,.112821]，Holm p1；MRR delta+.001076，CI[-.048047,.048004]。

Agent严格有效对仅N1或N2，选择性有效输出导致条件选择偏差；不做显著性检验、置信泛化或效果因果估计。提供valid-only、model-attempted failures-empty和planned-system三分母；超时算实际请求，context调用前失败只进入系统分母。历史54条与本轮预算完全独立。
''')
 write(ao+'figure-catalog.md','''# 图目录与解释要求

figure-01-main.pdf/svg/png：全部值来自EMBEDDING_REAL_RESULTS.csv及RERANKER_REAL_RESULTS.csv。目的：分开Top10覆盖与靠前排序；读者应看到CE Embed20 Top10上升而MRR下降，字段/分块没有一致改善。下一步应验证机制判别，而非只最大化Top10。柱无误差条，是975查询描述统计；相关性、单seed、EXPOSED_DEV必须随图注明。PNG已目视核验，数值没有溢出、遮挡。

figure-02-candidates.pdf/svg/png：来源RERANKER_CANDIDATE_UPPER_BOUNDS.csv。目的：区分召回上界和排序转化；K增加提高CandidateHit却使实际Top10下降。上界指至少一个Gold进入候选，不是多标签全覆盖。下一步优先检查候选内判别；图不能证明缺哪类语义。柱无CI，比例是全部975查询描述值。
''')
 provenance={'prediction_sources':[{ 'path':str(R/'results/server_gpu'/n),'sha256':sha256(R/'results/server_gpu'/n)} for n in ['EMBEDDING_REAL_PREDICTIONS.jsonl','M0_MATCHED_PREDICTIONS.jsonl','RERANKER_REAL_PREDICTIONS.jsonl']],'evaluation_script_sha256':sha256(R/'results/analyze_neural.py'),'agent_audit_script_sha256':sha256(R/'results/analyze_agent.py'),'Gold_location':'LOCAL frozen reference only; no server copy','comparison_question':'same visible observation and knowledge budgets; paired logical-step contrasts; strict valid same-case Agent comparison','split':'EXPOSED_DEV; P2 related development'}
 provenance.update(input_repair_registration_sha256=sha256(R/'manifests/EMPTY_INPUT_REPAIR_V2_REGISTRATION.json'),GPU_wrapper_sha256=sha256(R/'embedding/run_neural_gpu_v2.py'),V1_results_preserved='results/server_gpu_v1',input_repair_difference_table='results/INPUT_REPAIR_V1_V2_METRICS.csv')
 write(ao+'provenance.json',json.dumps(provenance,indent=2))
 qa=[
 '是；服务器两份固定GTE权重均完整并匹配官方SHA256，实际forward成功。',
 'GTE-ModernBERT Embedding、GTE-ModernBERT-Reranker及既有本地DeepSeek-R1-1.5B；7b已有缓存但本轮未使用。',
 'DistilBERT仅revision引用/锁文件；Qwen3-Embedding和BGE-M3在检查范围没有完整资产。',
 '本轮两种GTE已获明确授权并下载，无需再次申请；其他新增模型未获本轮下载授权。',
 '本机M3/24GB统一内存已能运行小LLM CPU；GTE本轮使用授权A40 GPU，真实预检与资源峰值通过。',
 '否。未下载、未运行Qwen3-Embedding。',
 '是。固定revision e7f32e3c00f91d699e8c43b53106206bcc72bb22。',
 '否。未下载、未运行BGE-M3。',
 'Alibaba-NLP/gte-modernbert-base，官方CLS+L2、768维、FP16模型/float32 cosine。',
 '是。全195合法逻辑步骤、975查询、216父技术、7场景、34执行标识；受限步骤未纳入。',
 'E1原生前缀3.79%/28.72%/.1067；E3窗口6.36%/30.26%/.1277；其余全条件见表。MRR为MRR@10。',
 '未稳定超过。E1 matched TF-IDF为9.23%/29.23%/.1401；E3 matched为8.41%/26.87%/.1266，Top10/MRR数值微升，但Top1下降且无稳健统计支持。历史27.79%输入预算不同。',
 '未观察到本方案增益。共享片段字段展开E2 Top10=23.38%、MRR=.0808，比E1下降；原因未因果确认。',
 '本方案没有。相同窗口直接编码Top10=30.26%，chunk-max27.59%、mean29.13%，MRR两者也低。',
 '是，全部Embedding和matched TF-IDF在20/50/100的CandidateHit、macro label recall、all-Gold coverage已交付。',
 '是，固定GTE-reranker-modernbert-base，完整分类权重哈希通过。',
 '是，两池×三个K，各975查询，真实联合编码logit，不是Embedding替代。',
 '仅Embedding Top20的Top10升至33.74%，但Top1=2.05%、MRR=.0887均低于原E1；更大K退化，不能称全面排序改善。',
 'E1 Embedding Top20/50/100全无Gold比例53.33%/32.10%/10.36%；词法58.36%/38.15%/19.08%。这指任一Gold都没有，不等于漏掉任一多标签。',
 '18个最终排序合格：静态RAG16、共享知识Direct2；54中另有24回传协议无效、12输出契约无效。',
 '没有全部同输入。知识、检索候选、额外日志及协议不同；不能汇总为同输入LLM语义收益。',
 '没有可确认的独立收益。旧样本少且不等条件；本轮输出失败多，合法严格配对不足，未做证据因果干预。',
 'V1只合并events，丢knowledge text/error/lexical metadata；V2仍在3500 bytes截知识，工具声明与模型所见不一致。',
 '是。完整消息哈希和原生后端context正文前缀在74/74原生响应逐条一致；有效Episode还核对实际tool结果及提交。',
 '是，22/22工程回放，0模型调用；与真实Episode分开记录。',
 '是，共3个：最小门槛1、主Pilot2。原生调用、完整回传、合法引用、Top10和独立评价俱全。内部语义利用仍未证明。',
 '端到端门槛已完成；剩余阻断是大多数条件的输出重复、完整上下文容量和4次超时，正式完整有效配对不足。',
 '预先固定12例×4方法的48条件已全记录，但39失败。另V4后注册24静态条件7有效；不能说12组全合法完成。',
 '是，同本地固定DeepSeek digest、CPU设置、上下文及最终输出合同；静态方法与Agent均无外部LLM。',
 '是，同一步Full-Authorized合法池，未读Gold/其他步骤/受限正文。',
 '是，同2查询、20新行、2048实际BPE与2048代理上限；不是实际内容完全相同。V4额外把最大可能返回数统一到10。',
 '能够主动选工具、取回并引用事件；没有充分证据证明查询针对竞争技术的区别性条件或因果改变排名。',
 '未证明。V3严格A1配对N1均未命中；V4 N2双方Top10=.5、MRR=.25。不能外推普遍无效。',
 '没有已成立的动态收益可供归因；缺少同事实删除/替换干预，不能判断来自额外日志还是语义判别。',
 '主Pilot Agent36调用、142223输入/4010输出；A0 12调用、37090/2654。调用3倍、输入3.83倍，成本不等。完整逐条件与超时预留见CSV。',
 '在V4合法同案N2，简单BM25静态策略复现同样命中与MRR；只支持这两例。',
 '可确认的E1 Top100完全召回缺失101/975；词法186/975。逐样本索引已保存。',
 '32个真实final因重复ID违反合同；合法错误排名存在，但主体/对象、状态变化等语义原因仍UNRESOLVED。不能由错分直接确定认知原因。',
 '策略层未证明区别性目标；成本增加已确认。错误查询、过早停止、忽略证据的因果归因尚未充分验证。',
 '标签可观测性、命令机制混淆、长文本截断是否删了关键证据、知识—动作错配、LLM内部证据利用等仍UNRESOLVED。',
 '没有。EXTERNAL_TEST_NOT_READY；P0暴露开发，P1/P2相关执行数据不是独立外部测试。',
 '优先机制判别和证据可观测性约束，保留GTE候选覆盖的基线价值；领域表示需后续受控实验。',
 '尚无足够证据正式提出已验证新算法；成熟组件组合、工程修复、查询概率符号本身不是创新。',
 '暂停扩大Agent复杂度；优先领域机制/表示诊断，Agent保留到证据干预与更可靠输出后再检验。',
 '冻结30个开发诊断步骤、盲标主体/动作/对象/尝试结果与不足证据，raw对literal机制表示、TF-IDF/GTE/CE固定预算对照；之后资格核查独立执行/外部数据。新增推理需新预算授权。'
 ]
 assert len(qa)==45
 question_text=Path('/Users/tianxd/.codex/attachments/3d8ef145-85e8-4c43-959d-fa4723cf0626/已粘贴的文本.txt').read_text().split('# 二十二、')[1].split('# 二十三、')[0]
 import re
 qs=re.findall(r'^\d+\. (.+)$',question_text,re.M);assert len(qs)==45
 qa_text='\n\n'.join(f'### {i}. {q}\n\n{a}' for i,(q,a) in enumerate(zip(qs,qa),1))
 body=f'''---
type: results-report
date: 2026-10-27
experiment_line: R3_semantic_model_agent
round: validation02
purpose: actual-model-and-agent-validation
status: complete_with_pilot_qualification_limits
source_artifacts:
  - reports/analysis-output/analysis-report.md
  - reports/analysis-output/stats-appendix.md
  - reports/analysis-output/figure-catalog.md
  - reports/analysis-output/provenance.json
linked_experiments:
  - results/server_gpu/manifests/NEURAL_RUNTIME_PROTOCOL.json
linked_results:
  - EMBEDDING_REAL_RESULTS.csv
  - RERANKER_REAL_RESULTS.csv
  - AGENT_PAIRED_COMPARISON.csv
---

# R3 预训练语义模型实测与Agent验证结果

主状态 **RERANKER_BASELINE_READY**。次状态 **SEMANTIC_EMBEDDING_BASELINE_READY**、**AGENT_END_TO_END_VALIDATED**。两种真实预训练模型完成全P0统一评价；本地小LLM完成3个有效Agent Episode。配对矩阵全部登记，但大量输出与上下文失败使完整科学比较仍不充分。没有已证明的Agent增益，也没有独立外部测试。

本轮最重要的变化是“没有模型实测”已被解决。GTE具有较高Top100候选覆盖，但早期排名未稳定超越词法基线；CE在Embed20改善Top10、损害MRR，候选增大后明显退化。当前证据支持优先研究技术机制判别和可观测证据约束，暂不支持增加Agent复杂度或宣布新算法创新。

## 实验资格、权限与输入

P0共195合法逻辑步骤、975查询、7场景、34执行标识、216父技术，是EXPOSED_DEV。P1/P2来自相关CAM-LDS执行，为RELATED_DEVELOPMENT_DATA，不是三个独立数据集。P2合法池680280行这一继承事实未用重复385×7实验替代新结果。旧目录保持只读，最终校验256份继承资产；受限场景1 PwnKit步骤35–37及别名没有读取/上传，CONV-A01仍未授权。

用户后续明确授权覆盖原服务器只读限制，仅在指定项目安装两种GPU模型及项目名venv；另外明确批准上传975条清洗P0预测输入与公开K2。上传不含Gold和原始归档。授权前自动审查曾因缺少日志外传授权拒绝上传；取得用户明确批准后才成功，未绕过。安装/下载的网络超时和tokenizer续传尺寸错误均保存并有限恢复，最终固定权重官方哈希通过。

同一选取规则内，GTE和匹配词法条件共用原生观察片段及公开知识文本；前缀与窗口选择不同片段，但原始日志池和Token上限相同。日志同时满足两个实际tokenizer的2048上限，知识定义1024实际Token上限，216候选不变。E1原生前缀；E2真实字段/来源元数据加完整native（有重复，无新增观察）；E3固定窗口直接编码；E4/E5同窗口的256实际Token分块max/mean。原始日志长度分词触发过8192警告，实际forward另有长度断言，未把超长原文送入模型。

Embedding官方CLS+L2；CE是联合编码分类raw logit，分别重排canonical E1 Embedding和matched lexical的Top20/50/100。选择canonical E1池在Gold前固定，没有根据最佳Embedding成绩换池。FP16、batch8、GPU0、CPU2线程，离线加载、禁止远程代码。两模型先单例/8例预检后全量；耗时{embtime['seconds']:.2f}/{cetime['seconds']:.2f}秒，55,238个唯一pair。服务器未加载Gold，预测固定后本地冻结V1父技术评价，MRR为前10截断。

## 完整模型结果

{neural_table}

原最强CharacterNgramTFIDF P0 Top1=8.62%、Top10=27.79%、MRR=.1294是继承的不同完整输入协议；本轮matched输入/知识预算下的TF-IDF见表，不混用。作者GPT-5.5历史预测40.92%/66.67%/.4960仅是作者公开预测复算，本轮没有外部模型调用。

E1 GTE未超过matched lexical；E3 Top10较matched窗口高3.38个百分点，但Top1低、MRR只微升约.0011且不稳健。字段展开、chunk max/mean没有一致收益。CE Embed20相对E1 Top10净增49条（5.03个百分点），但Top1/MRR下降；其余5种CE均没有稳定排序收益。

## 候选上界与误差

{upper_table}

E1 Embedding Top100的any-Gold覆盖89.64%，多标签全部覆盖74.05%；窗口E3分别91.69%/76.41%。这是覆盖能力，不能等同技术正确判别。Embed100重排中有750条候选有Gold却没进入前十；词法100为693条。结构/命令/主体对象/尝试与成功等具体语义原因标UNRESOLVED，不能由分数反推日志缺失。

## 图与统计解释

![覆盖与排序](reports/analysis-output/figures/figure-01-main.png)

图1同时显示Top1、Top10和MRR：单看Top10会掩盖CE的靠前排序退化。它改变的研究判断是优先查候选内机制判别，而非只追求更大召回。

![候选上界与实际重排](reports/analysis-output/figures/figure-02-candidates.png)

图2将any-Gold候选上界与真实Top10分开：候选变多，正确技术进入池的机会增加，排序转化却下降。它不能证明某一具体语义原因，只定位失败发生的阶段。两图均为全975查询描述统计、单seed、无独立测试含义；矢量PDF/SVG同时交付。

逻辑步骤聚合195组，保留5查询相关性；13对比×2指标的探索性bootstrap CI、SD、sign-flip p和Holm p完整保存。CE Embed20 Top10差95%CI [.0021,.0985]、raw p=.0537、Holm p=.6443；不能只用正CI宣称确认性显著。场景/脚本共享还会违反步骤独立假设，因此所有推断限于暴露开发数据，不能写成外部泛化。无跨seed重复，不虚构mean±std；详细统计限制见stats-appendix。

## 历史LLM与本轮真实Agent

旧54原生响应中36final、18action；只有18个final科学合格（16静态RAG、2共享知识Direct）。24回传协议无效、12输出契约失败。知识/日志条件不统一，4个逻辑步骤、2场景，未证明LLM独立收益。历史成本与本轮分开，旧失败轨迹未修成有效结果。

新传输修复22项回放通过，0模型调用；真实原生模型响应另计74份、78次尝试。完整GGUF输入正文与后端context前缀74/74一致。3个有效Episode包括最小门槛、v2_sampled_0297和v2_sampled_0326；模型发起只读查询、接收实际完整反馈、引用合法返回事件、提交Top10并独立评价。结构性闭环成立，但内部语义利用及因果排序更新未由此证明。

V3预注册12例×4条件已全记录；A0共享相同部分公开知识，没有额外日志；A1 BM25、A2固定关键词、A3模型选择查询。额外证据同时cap2048实际GGUF与2048 regex代理、20新行、2查询；计算调用另记。V3静态完整封装导致上下文溢出，另注册V4全部24静态控制，减少最大条数，不增加Token预算、不重跑Agent、不查看GT修改案例，不重置额度。V4为posthoc开发性工程控制，不能冒充预注册。

73条件中17有效、56失败：32重复ID、20调用前上下文失败、4实际请求超时。严格有效同案比较：

{pairs_table}

V3 A1/Agent N1均未命中；V4 N2均Top10=.5、MRR=.25。A2同案合法交集为空，NA。Agent有效分母2例Top10=.5，与全12例实际调用条件失败保留Top10=.0833不能混用。当前为“未支持Agent独立增益”，不是普遍否定。完整48条件登记不等于全部12组均具评价资格，不选择AGENT_PAIRED_PILOT_COMPLETED或AGENT_INCREMENTAL_GAIN_SUPPORTED_ON_DEV作为终态。

## 调用、Token与预算

{cost_table}

全新78/80次推理尝试，74条原生回执；输入342841、输出11981，4次超时实际成本未知。按请求预留上限计输入370436/500000、输出14029/45000；失败不按0消费。首请求至最后等待结束82.28分钟。没有重置旧预算或在结束后追加推理。卸载控制（无prompt）约在首请求90.9分钟完成，ps为空；4次超时后台真实结束时刻无法核实，不能声称后台耗时已严格验证。详见逐请求ledger、LOCAL_MODEL_STOP_RECEIPT和成本CSV。

Agent V3调用36次，对比A0 12次为3倍；输入约3.83倍，额外日志cap相等不等计算相等。静态调用前失败造成低计算量，不能解释成低成本同质量。GPU forward与本地生成模型请求分开计量。

## 科研结论与下一步

已确认：真实模型基线、候选内排序失败定位、完整Agent工程闭环。合理推测：通用相关性与日志机制/证据可观测性存在错配。研究判断：优先机制判别与领域表示诊断，暂停增加Agent角色、reflection和RL。没有正式验证的新算法机制。EXTERNAL_TEST_NOT_READY。

下一轮先冻结30个开发诊断步骤，盲标主体/动作/对象、尝试/结果及不足证据，固定原文与可追溯literal机制视图，比较TF-IDF/GTE/CE同预算；该诊断不当测试集。再资格核查真正独立执行/脚本或外部数据。固定小LLM需先解决输出可靠性、完整上下文容量与超时终止验证，才能扩大同预算Agent比较。新增推理须新预算，当前额度不续用。

## 45项逐条回答

{qa_text}

## 复现与交付索引

模型：MODEL_ASSET_AUDIT、MODEL_ENVIRONMENT_MANIFEST、MODEL_LOAD_TESTS、MODEL_DEPENDENCIES、MODEL_EXECUTION_STATUS；授权见三个manifests；服务器原生结果/输入映射/锁文件在results/server_gpu，代码固定SHA见运行协议。

预测与评价：EMBEDDING_REAL_PREDICTIONS/RESULTS/CANDIDATE_RECALL，RERANKER_REAL_PREDICTIONS/RESULTS/CANDIDATE_UPPER_BOUNDS；逐样本错误、排名转移、分场景/执行表和探索性统计在results。

LLM/Agent：旧54资格与回执审计；新native_receipts逐请求原生文件；AGENT_VALID_EPISODES、AGENT_PAIRED_COMPARISON、AGENT_COST_REPORT、NEW_LLM_CONDITION_RESULTS及ERRORS；V3/V4注册和源码哈希、回放测试及原生后端输入证明。

严格分析bundle为reports/analysis-output四份文档/溯源及两幅图。最终交付哈希和旧资产完整性以manifests/DELIVERY_SHA256.json及results/FINAL_VALIDATION.json为准。所有源码、预测、错误及负结果保留；完成后停止，不创建自动任务。
'''
 body=body.replace('## 实验资格、权限与输入','本报告模型主表统一使用空输入修复后V2。V1完整预测与报告保留；修复只更改17个空视图，1933个非空视图逐字不变，两模型全量重新运行。修复规则在运行前登记为posthoc工程校验，不是新算法或择优拼接；详见INPUT_SELECTION_REPAIR.md及前后差异CSV。\n\n## 实验资格、权限与输入')
 body=body.replace('![覆盖与排序](reports/analysis-output/figures/figure-01-main.png)',f'![覆盖与排序]({R}/reports/analysis-output/figures/figure-01-main.png)').replace('![候选上界与实际重排](reports/analysis-output/figures/figure-02-candidates.png)',f'![候选上界与实际重排]({R}/reports/analysis-output/figures/figure-02-candidates.png)')
 write('R3_SEMANTIC_MODEL_EXECUTION_AGENT_VALIDATION_RESULTS.md',body)
 print('Generated required reports and strict analysis bundle.')
if __name__=='__main__':main()
