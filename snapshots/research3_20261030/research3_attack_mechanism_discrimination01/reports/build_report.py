"""Evidence-indexed wrap-up; no models or external writes."""
import csv,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def read(name):return list(csv.DictReader((ROOT/name).open()))
def table(rows,cols):return '| '+' | '.join(cols)+' |\n| '+' | '.join('---' for _ in cols)+' |\n'+'\n'.join('| '+' | '.join(str(r.get(c,'NA')) for c in cols)+' |' for r in rows)
def pct(x):return f'{float(x)*100:.2f}%'
def main()->None:
 results=read('MECHANISM_BASELINE_RESULTS.csv');m={x['method']:x for x in results};audit=json.loads((ROOT/'RERANKER_SCORING_VALIDATION.json').read_text());valid=json.loads((ROOT/'results/MECHANISM_VALIDATION.json').read_text());selection=json.loads((ROOT/'DIAGNOSTIC_30_FROZEN_IDS.json').read_text());budget=read('frozen_inputs/INPUT_BUDGETS.csv');stats=read('results/ALL_EXPLORATORY_CONTRASTS.csv');eq=read('results/CARD_WORD_ORDER_INVARIANCE.csv');external=json.loads((ROOT/'external_dataset/LOCAL_SOURCE_QUALIFICATION.json').read_text())
 mainrows=[x for x in results if x['knowledge'] in ['K2_DESCRIPTION_16_1','MECHANISM_CARD'] and x['input_view'] in ['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']]
 main_table=table([{'方法':x['algorithm'],'日志':x['input_view'],'知识':x['knowledge'],'N':x['n_records'],'Top1':pct(x['top1_accuracy']),'Top10':pct(x['top10_accuracy']),'MRR@10':f"{float(x['mrr']):.4f}"} for x in mainrows],['方法','日志','知识','N','Top1','Top10','MRR@10'])
 checks=[('eval模式','SOURCE_VERIFIED','冻结源码调用.eval；本轮无新运行时探针'),('Tokenizer','SOURCE_AND_REVISION_VERIFIED','两个模型各自固定目录；hash收据继承'),('文本顺序','SOURCE_VERIFIED','日志query在前、技术document在后，与模型卡pair语义一致'),('文本对格式','SOURCE_VERIFIED','Tokenizer(query_list,document_list)，无自定义prompt/instruction'),('输出维度/标签','PARTIALLY_VERIFIED','保存一对一scalar分数；未新forward，config正文未成功取回，不能独立排除原始flatten维度假设'),('raw logit方向','DOCUMENT_SUPPORTED','官方模型卡以logits评分；高值相关，不按CAM得分选方向'),('分数反转','SOURCE_VERIFIED_ABSENT','无取负数或低分优先'),('正负类别','NO_CLASS_SELECTION_IN_SOURCE','源代码flatten；单输出维度仍待独立config核验'),('Softmax/Sigmoid','SOURCE_VERIFIED','未跨候选Softmax，未作非单调分数处理；单调Sigmoid不改变精确实数排名'),('排序方向','SAVED_SCORES_ALL_PASS','按(-score,ID)重建5850条件完全一致'),('跨批次','SAVED_CACHE_CONSISTENT','同一对缓存分数稳定；独立single/batch复测没有授权，不能称实测通过'),('ID与分数索引','SAVED_RECORDS_ALL_PASS','每候选唯一ID对应raw_logit，按ID重建'),('模型输入截断','SOURCE_VERIFIED_FALSE','Tokenizer truncation=False、pair长度断言；上游日志显式预算截取存在'),('描述截断','UPSTREAM_TRUNCATION_PRESENT','65份知识描述在共同1024token预算下截取，整体影响UNRESOLVED'),('不同K输入','HASHES_ALL_PASS','同对日志hash/revision一致；知识版本与预算固定'),('不同K分数','ALL_EXACT_EQUAL','交集对最大差0；来源是同一cached forward'),('重复候选','SAVED_SETS_ALL_PASS','每池K个不同候选'),('父技术','SAVED_IDS_ALL_PASS','216父技术，不新增子技术归一化'),('无效候选','SAVED_IDS_ALL_PASS','候选ID来自冻结216集合'),('评价索引','RECONSTRUCTED','同sample_id与冻结Gold独立关联；旧MRR@10口径保留')]
 audit['twenty_checks']=[{'item':i+1,'check':name,'status':status,'evidence_limit':detail} for i,(name,status,detail) in enumerate(checks)];audit['runtime_config_or_independent_batch_rescore']='NOT_REVERIFIED_NO_NEW_FORWARD_AUTHORIZATION';save('RERANKER_SCORING_VALIDATION.json',audit)
 md('CROSS_ENCODER_FORENSIC_AUDIT.md',f'''# Cross-Encoder实现与适配审计

结论：已保存的5850个条件能够按原始分数和ID完全重建，固定日志—候选对跨K/池分数最大差0；未发现足以解释扩大池退化的保存/排序错误。**不等于所有运行时适配问题已被独立排除**：本轮无新forward，未取得固定config正文或独立单例/批次对照。不得凭source flatten就宣称输出维度已重新验证。

{table([{'项目':i+1,'检查':n,'状态':s,'证据与边界':d} for i,(n,s,d) in enumerate(checks)],['项目','检查','状态','证据与边界'])}

官方[固定revision模型卡](https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/f7481e6055501a30fb19d090657df9ec1f79ab2c/README.md?code=true)给出Transformers logits和CrossEncoder用法；当前[CrossEncoder接口文档](https://sbert.net/docs/package_reference/cross_encoder/model.html)说明activation_fn作用于logits，单输出默认Sigmoid、允许模型配置覆盖。本轮不是实际运行SentenceTransformers wrapper；比较的是冻结Transformers实现与公开接口语义。Sigmoid的单调性只能说明排序不必反向，不能证明模型已校准或每对正确。

浏览器/联网连接失败，备用只读下载自动审查两次超时；没有权重/数据下载，也没有为了提高CAM分数反转logit。保留SCORING_DIMENSION_RUNTIME_NOT_REVERIFIED这个缺口。''')
 md('RERANKER_FAILURE_DIAGNOSIS.md',f'''# D1—D6实际离线诊断

D1继承canonical E1 Embedding原始排名；D2依据官方高logit方向重建CE；D3比较Top20/50/100；D4计算每条件Spearman；D5逐样本逐候选核对分数；D6保存所有候选的升降级及分层错误。新GPU调用为0。

{table(audit['summary'],['pool','K','N','CANDIDATE_NOT_RETRIEVED','CANDIDATE_RETRIEVED_BUT_RANKED_LOW','CANDIDATE_DEMOTED_BY_RERANKER','CANDIDATE_PROMOTED_BY_RERANKER','mean_Spearman'])}

Embedding Top100：101/975无Gold候选；750/975有候选Gold但最终前十没有Gold；另48原已命中仍命中、76原未前十而被提升。两类失败分别为10.36%与76.92%，不混称语义推理失败。Top20到100时部分非步骤Gold的高分候选替换Gold；最常见替换ID及次数：{audit['replacement_techniques_top20'][:8]}。这些是相对步骤标签的非Gold，不表示该技术在日志中必然没有发生。

原排1—10/11—20/21—50/51—100的分数分布见SCORE_DISTRIBUTION_SUMMARY：候选池后部也存在高logit尾部。扩大池改变可竞争集合而非原对分数；排序相关性很低。可确认阶段为候选内排序，不足以确定原因是缺少机制理解。上游截取/领域适配/标签可观测性仍UNRESOLVED。没有修复方向/归一化或搜索融合权重，没有MODEL_SCORING_IMPLEMENTATION_CORRECTION贡献。''')
 md('MECHANISM_EXTRACTION_VALIDATION.md',f'''# 机制提取与来源验证

实际实现为mechanism_ir/extractor.py及build_inputs.py，名称Attack Mechanism IR v1，非NLP AMR标准。只读既有清洗P0和上一轮V2 prefix映射，不读P2完整池或原始归档，不调用LLM。parser只接收原始片段和源哈希；合成GT注入测试不改变输出。

实际975查询、{valid['native_fields_verified']}个原生字段逐一通过原始char span或JSON pointer回查；{valid['native_relations_verified']}条关系通过同source及原生事件key/时间检查；1866个卡片词形提及匹配冻结知识源span。12项安全不变量通过，包括当前uid0不升级为提权、exit0不自动成功、success=no保留失败、不同源不拼接、同PID不认证进程生命周期、普通name不当File、片段边界不完整字段弃用。

这是工程来源/边界一致性，不是机制语义准确率。独立人审尚无，不能报告Precision/Recall或100%语义正确。状态只有observed_state；没有凭当前uid推导state change。result只引用原生success=yes/no，并限定为本次syscall报告，其他return值语义UNKNOWN。关系只包含SAME_NATIVE_AUDIT_EVENT和NATIVE_TIMESTAMP_BEFORE，不表示因果或跨生命周期身份。

所有表示共享相同选定原始片段，日志最多2000 UTF8 bytes，知识1000 bytes；字节不是GTE Token，实际模型Token未取得，必须记NA。RAW+Literal同样受cap约束，因此共享观察有进一步截取，不能把本轮Raw14.87%与上一轮完整预算29.23%直接比较。传感器自带Txxxx注释在预测文本中等长掩码；源追溯保留原始哈希和片段，未使用官方步骤Gold生成字段。

预验证阶段发现普通name字段不能总解释为文件，已在任何新排名之前改为未认证命名实体；旧开发构建保留results/prevalidation_build_v0。正式输入生成后不随分数修改规则。''')
 coverage=json.loads((BASELINES/'knowledge/COVERAGE.json').read_text())
 md('KNOWLEDGE_COVERAGE_AUDIT.md',f'''# ATT&CK知识覆盖与卡片边界

冻结16.1，216候选，203有描述、13按历史协议保留：{coverage['missing']}。全部实验保留216，不用203共同覆盖替代主结果。没有混入v18 detection strategies。

卡片完全由冻结K2的通用动词/对象词形提取，1866个提及有原文span。state/temporal/result requirements全部留空并标NOT_FORMALIZED，不把常见实现写成普遍必要条件。不含按样本Gold选择或补写的条件；知识提及与当前观察分开。未覆盖描述的13项仅能沿用标题/原占位信息，不能称具有完整机制知识。

主知识视图为名称、原描述、去标题、机制卡、原描述+卡五组，每候选最多1000字节。原描述取前缀，机制卡可从同一完整K2抽取后部片段，**可见内容分配并不相同**；因此另登记posthoc CARD_PREFIX_ONLY控制来源范围，以及CARD_WORD_ORDER_CONTROL保留词频打乱词序控制。主/GPU冻结文件未更改，新控制独立存储。字节cap相同不等于信息量或Token数完全相同。

词表是可复核近似词形匹配，存在词义歧义；来源一致不等于概念语义已通过人工审核。所有卡片的条件资格为descriptive mention，不能将KNOWLEDGE_COMPATIBLE当OBSERVATION_SUPPORTED。''')
 md('MECHANISM_REVIEW_GUIDELINES.md','''# 30例独立人工盲审指南

审查包只提供MIR匿名ID、合法原生片段、Literal和关系，不含sample_id、分层、步骤Gold、模型Top10/正确性。管理映射human_review/ADMIN_PACKET_MAPPING.csv和DIAGNOSTIC_30_CASES不得交给首次审查者。原生传感器技术ID已遮盖。若需技术命题，使用所有216卡片或预先固定的无Gold命题，不按答案提供暗示。

逐项判定主体/动作/对象/状态是否有原生支持、结果是尝试/报告成功失败/未知、身份绑定与时间关系是否认证、证据是否足以支持所给命题。选OBSERVED、NOT_OBSERVED_IN_SCOPE、UNKNOWN或IDENTITY_UNRESOLVED；未观察到不等于反证。当前root不代表提权；写文件不代表恶意安装；网络端点不代表攻击者；同PID和时间近不认证生命周期或因果。

每项填写原始event/field/span和理由，记录审查者、日期、冲突与裁定。真实人工完成前全部PENDING，不能用开发Agent、自举卡片或步骤标签生成的解释当独立人审，也不能给机制支持准确率。本轮没有向任何人或外部服务发送审查包。''')
 detail=read('results/PER_SAMPLE_TECHNIQUE_RESULTS.csv');dl={(x['method'],x['sample_id']):x for x in detail};events={x['sample_id']:x['events'] for x in load(ROOT/'MECHANISM_LITERAL.jsonl')};cases=[]
 for c in selection['cases']:
  sid=c['sample_id'];ev=events[sid];a=dl['CHAR__RAW__K2_DESCRIPTION_16_1',sid];b=dl['CHAR__LITERAL__K2_DESCRIPTION_16_1',sid]
  cases.append({'sample_id':sid,'scenario':c['scenario_id'],'step':c['step_id'],'old_error_stratum':c['stratum'],'selected_native_events':len(ev),'explicit_results':sum(e['result']['status'].startswith('REPORTED_SYSCALL') for e in ev),'subjects_known_native_reference':sum(e['subject']['native_id'] is not None for e in ev),'raw_char_hit10':a['top10'],'literal_char_hit10':b['top10'],'evidence_sufficiency':'UNRESOLVED_HUMAN_PENDING','case_cause':'SOURCE_STRUCTURE_AND_RANK_CHANGE_ONLY_NOT_CAUSAL_ATTRIBUTION'})
 csvout('diagnostic_30/CASE_ANALYSIS.csv',cases)
 md('MECHANISM_ERROR_ANALYSIS.md','''# 实际错误与可确认范围

原描述下CHAR Raw14.87%→Literal9.13%，BM25 Raw13.54%→Literal17.03%；后一差的95%逻辑步骤bootstrap CI跨0、Holm p1。关系后BM25与Literal完全相同；实际词表审计发现新增关系/动作规范化标记没有知识文档posting，BM25忽略该通道。这是接口未生效，不是关系语义的有效否证。CHAR有小幅变化但不足归因。不能据此扩充关系图或断言所有关系模型无效。

可确认原因包括：输入进一步截取；许多行缺少可解析动作/主体/对象，Literal会显式UNKNOWN并丢掉未结构化文本；元字段与normalized标签占用文本。是否因此丢了区分具体技术的关键证据，需要独立人工证据判断，不能由错分反推。FILE_PATH_ROLE_UNRESOLVED和PROCESS_REFERENCE_UNBOUND_LIFECYCLE都没有被提升成攻击结果。

机制卡有若干开发性数值提升，但标题、术语、1000字节分配和源片段选择共同改变。词序控制下BM25四视图全部975例完整216排名一致，说明当前检索不利用卡片结构。CARD_PREFIX_ONLY有时更好、有时更差，不能挑一个最高值当新算法。LiteralMechanismMatching Top10仅4.31%，不是可靠技术机制支持判别器；Jaccard分母是相似度长度归一化，不能解读为缺失日志对技术的反证。

30例逐案记录在diagnostic_30/CASE_ANALYSIS.csv，按旧输出分层且已暴露，不能从30例推总体准确率。步骤Gold仅评价技术排名，不认证逐行主体/对象/成功或因果。当前“证据不可观察”、语义歧义、时序/身份不足、标签—日志对齐问题全部仍UNRESOLVED，人工状态PENDING。新GTE/CE机制条件没有授权而未执行，不能以旧RAW输出替代。''')
 md('METHOD_FORMAL_PROBLEM.md',r'''# 问题形式与实际最小实现

给定冻结合法日志L、知识K和216技术集合T，构造z=phi(L)，认证原生关系R=g(z)。phi只读取原生字段/源span，g只在同source的明确audit key或时间字段上产生关系；未知身份、结果和状态变化保留UNKNOWN。卡片C_t=h(K_t)是知识词形与原文片段，不是必要条件逻辑公式。

技术排名为rank_t s_theta(render(z,R),render(C_t))。本轮theta只有冻结CharacterNgramTFIDF、BM25与简单动作/对象Jaccard；未训练新参数，未新增GTE前向。LiteralMechanismMatching使用两个集合相似度等权和，不采用技术专属规则，不输出机制充分性真值。

评价目标是步骤级多标签Top1/5/10、MRR@10、Precision/Recall/F1；机制语义支持判断是另一任务，缺独立人工参考时不可评分。日志不完整时不以机制未出现构成NOT_OCCURRED；技术描述常见手段不强制为所有实例必要条件。

实际假设是“同观察和检索器下显式表示是否改善排名”，不是已经建立新理论。P0已暴露，脚本/场景相关；本轮结果不能证明外部泛化，也不触发RL、DGPR或大型知识图谱开发。''')
 md('METHOD_RESEARCH_DECISION.md','''# GO / NO-GO

主状态：MECHANISM_REPRESENTATION_EXECUTED。

次状态：RERANKER_FAILURE_DIAGNOSED（保存分数层面；运行时维度/独立批次复测仍缺）、NO_SUPPORTED_ALGORITHMIC_GAIN（仅已执行非神经实验）、MODEL_FORWARD_AUTHORIZATION_BLOCKED、EXTERNAL_TEST_NOT_READY。不使用PAPER_READY或GENERALIZATION_PROVEN。

NO-GO：当前Literal/Relations/卡片组合作为已验证独立算法贡献；不增加规则、图复杂度、reflection、RL或DGPR-V3。BM25 Literal有小幅开发数值提升但不稳健，字符检索退化；卡片成绩受词汇和可见知识分配混杂，关系在BM25的评分通道没有生效，CHAR也未支持稳定收益。工程可追溯性成立，机制语义准确性尚未独立认证。

条件GO：保留可追溯IR作为诊断工具。若用户批准已具体列出的新前向，执行同固定模型/同观察的神经表示对照；未批准就保持NA。先确认表示的新增机制特征实际进入评分（当前BM25关系/动作标签通道未生效），再完成30例真实独立审查，区分不可观察标签、动作/对象绑定错误和模型相关性偏差。只有证据显示表示本身有独立价值才继续机制判别；否则优先考虑领域对比学习/困难负例适配，但本轮不启动训练。''')
 # Explicit unrun neural conditions, not fake zero scores.
 csvout('experiments/NEURAL_CONDITION_STATUS.csv',[{'model':model,'input_view':v,'knowledge':k,'status':'MODEL_FORWARD_NOT_AUTHORIZED','N':'NA','Top1':'NA','Top10':'NA','MRR':'NA'} for model in ['GTE_EMBEDDING','GTE_CROSS_ENCODER'] for v in ['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL'] for k in ['K0_NAMES_ONLY','K2_DESCRIPTION_16_1','K3_WITHOUT_TITLES','MECHANISM_CARD','K2_PLUS_CARD']])
 ao='reports/analysis-output/'
 md(ao+'analysis-report.md',f'''# 比较问题与真实证据

问题1：固定候选相同logit是否因K改变？答案：全部交集最大差0，同一cache复用，不能当独立复测。问题2：同选定日志、同检索器、同知识版本/字节cap，Literal/Relations是否改善父技术排名？问题3：卡片改变是否能排除词汇/可见信息分配？

{main_table}

主49条件47775预测；另一次登记的posthoc知识控制16条件15600预测；总65条件63375，所有975查询保留。没有新神经前向。步骤Gold只在预测固定后评价。原始scores、每样本、分场景、消融和140+32=172探索性对比完整保存。

Claim candidates：
- 固定对分数不因K变化：保存记录支持，允许“cache记录一致”，禁止“独立运行稳定性已证明”；下一步有授权后single/batch校验；keep。
- Literal未稳定改善：CHAR退化、BM25数值提升CI跨0。允许“当前检索器/输入协议未支持稳定增益”，禁止“所有机制表示无用”；微小观察预算/无神经对照；weaken。
- BM25不利用卡片词序：975×4全排名不变。允许“当前词袋模型结构无贡献”，禁止推广所有语义模型；下一步固定模型对照；keep。
- IR来源可追溯：34510字段/997关系工程检查，允许“来源一致”，禁止“语义100%正确”；人工PENDING；weaken。
''')
 md(ao+'stats-appendix.md','''# 统计与限制

195逻辑步骤，每步5查询先平均形成成对差，7场景/34执行相关。一次确定性模型，无跨seed重复；不制造run-level mean±std。报告成对差mean/SD，seed42、2000次bootstrap95%percentile CI、5000次signflip（+1修正）双侧p。离散差不假设正态，不做普通独立t检验。

主70对比×2指标=140探索项，后注册知识控制16对比×2=32，最终全部172项统一Holm；初始140文件另存PRECONTROL_CONTRASTS_140.csv。控制是开发性混杂诊断，不是预注册确认性检验。逻辑步骤仍共享脚本/场景，交换性/独立假设可能不满足，CI和p只作条件开发分析，不支持泛化。

BM25 Literal vs RAW原描述：Top10 delta .034872，SD .305304，95%CI[-.006154,.078974]，raw p .124575，Holm1；MRR delta .006013，CI[-.007182,.021455]，Holm1。工程来源一致率不是机制语义准确率。字节cap不等于模型实际Token数；确切GTE Token长度当前NA，不能伪造“严格等Token实测”结论。
''')
 md(ao+'figure-catalog.md','''# 图解释

figure-01-mechanism.pdf/svg/png：同一观测、检索器、描述或卡片的Top10比较，取MECHANISM_BASELINE_RESULTS.csv。看Literal在CHAR退化、BM25提升但不稳定，以及Relations缺乏独立收益；决定不继续叠加关系复杂度。无误差条，是975查询描述统计，单协议EXPOSED_DEV；推断区间另见统计表。

figure-02-knowledge-control.pdf/svg/png：卡片/只从可见前缀提取卡片/相同词频乱序控制。它区分结构、词汇和知识内容分配。BM25乱序完全同分同排名，不能将卡片提升归因结构推理；CHAR变化也可能只是字符n-gram邻接。posthoc控制，不能据此提出确认性新方法。
''')
 save(ao+'provenance.json',{'source_files':[{'path':str(ROOT/n),'sha256':sha256(ROOT/n)} for n in ['MECHANISM_BASELINE_PREDICTIONS.jsonl','experiments/KNOWLEDGE_CONTROL_PREDICTIONS.jsonl','MECHANISM_LITERAL.jsonl','MECHANISM_RELATIONS.jsonl','frozen_inputs/PREDICTION_INPUTS.jsonl','attack_knowledge/KNOWLEDGE_TEXTS.json','experiments/evaluate_offline.py']],'Gold_path':str(BASELINES/'datasets/p0_reference.jsonl'),'Gold_role':'post-prediction step-label evaluation only','new_GPU_calls':0,'new_LLM_calls':0,'split':'P0_EXPOSED_DEV'})
 qa=[
 '未发现保存分数/排序层面的实现错误；但没有新前向和config正文，输出维度及独立批次稳定性仍未重新验证，不能宣称全部实现问题都排除。',
 '官方模型卡支持以raw logit高值排序；本实现不做方向反转。没有依据CAM准确率挑评分方向。',
 '一致，所有保存交集最大差0；这是缓存复用一致性，不是独立重复forward试验。',
 '新增高分非步骤Gold候选替换部分Gold；T1204/T1601/T1592等出现较多，精确逐候选替换与分布已保存。非Gold不等于事件中该技术绝不发生。',
 'Embedding Top100无Gold101/975=10.36%；候选有Gold而最终前十未命中750/975=76.92%，二者分开。',
 '可排除K特有的文本变化/保存索引变化解释：同对hash和分数不变；不能排除上游截取对整体任务的影响（65份知识曾截断），也未新测batch/维度。',
 '是，30个不同scenario+step，在新机制预测前冻结。',
 '是，10降级/6提升/6共同失败/4共同正确/4召回失败，覆盖7场景；仍有脚本依赖，非独立测试。',
 '是，975查询实际提取，运行代码和数据齐全。',
 '是，997条同source原生audit key/时间关系；不以同PID认证生命周期，不从时间近推因果。',
 '34510个字段逐一回查原始span/JSON pointer，未发现未追溯项；这不证明语义解释100%正确。',
 '当前实现未作该推断；uid/euid保留观察状态，没有提权发生或跨生命周期状态变化结论。',
 '没有自动升级；仅native success=yes/no认证本记录报告状态，exit0等未认证返回语义仍未知。',
 '是，216卡片，16.1固定；203完整描述、13缺描述仍保留。',
 '不新增测试Gold规则；卡片词形/片段可追溯。必要/可选条件无法认证时留空或descriptive，不当普遍必要条件；语义词义仍待人工。',
 '生成器不读官方Gold；预测文本Txxxx传感器注释已掩码，输入Schema/GT注入不变测试通过。Gold只在分层选取与独立评价侧。',
 '原描述Literal CHAR：Top1 .82%、Top10 9.13%、MRR .0307；同观察RAW为1.85%/14.87%/.0516。',
 '不稳定。BM25原描述Top10 13.54%→17.03%，CI跨0、Holm1；CHAR退化，不能宣布稳健表示增益。',
 '否，没有本轮新GPU明确授权，GTE新表示未运行；旧RAW分数仅做继承诊断。',
 '是，精确文件/哈希、目的地、项目venv、固定模型、GPU和上限已列MODEL_FORWARD_AUTHORIZATION_REQUEST；等待明确答复。',
 'NA，未运行，不能用旧模型RAW预测推断Literal成绩。',
 'NA，未运行；旧CE的候选内排序诊断不是新表示CE实验。',
 '当前未证明独立收益。BM25新增关系/动作标签不在文档词表，通道未生效，所以相同结果不能否证关系语义；CHAR小幅变化不足归因。',
 '尚不能完全排除，来源/清洗、元字段和字节分配会改变文本，实际GTE Token数未测；CLEAN_FIELDS/去角色/去结果/去动作等控制已保存。',
 '有部分开发数值变化，但词汇、标题、长度与源片段分配未被充分排除；同词频乱序使BM25全部排名不变，不能称机制知识推理贡献。',
 '通用动作对象Jaccard Top10=4.31%，并未复现较好检索；这不意味着复杂机制成立。词序控制能复现全部BM25卡片成绩，说明词袋解释仍在。',
 '继承E1 Top100的101例完全候选缺失可确认；各K分类全部交付，不当作机制语义错误。',
 '继承Top100的750例候选内前十失败可确认，新CPU排名错误也逐样本保存；具体语义原因尚不能仅凭标签确定。',
 '无独立事件/机制参考，不能确认哪些Gold机制在截取日志中不可观察；原始范围不完整不构成技术未发生。',
 '主体对象歧义、状态/结果解释、标签可观测性、域错配、关键证据截取等仍UNRESOLVED。',
 '没有本轮30例新增独立人工参考，全部PENDING。外部派生文件自称human_reviewed，其凭证本轮未独立核实，也未拿来当30例人审。',
 '机制支持Precision/Recall、语义正确率、因果/状态变化判断一致性等不能评分；来源回查与预算工程一致性可报告。',
 'OTRF/Mordor APT29有可查本地26步派生标签，是具体候选；匹配原生日志/原计划、许可、脚本独立性和旧ID处理未资格确认，目前不是合格TEST。',
 '没有。P0曝光，P1/P2相关；Mordor派生副本也在其他项目已见，ExCyTIn图QA任务不匹配。EXTERNAL_TEST_NOT_READY。',
 '没有找到已验证的独立新算法机制；可追溯IR是诊断资产，成熟检索+卡片组合不等于创新。',
 'NO-GO继续堆叠当前Literal/Relations规则；先确认表示新增特征进入评分，再人审与有授权的同模型对照；若仍无收益，转向领域适配/困难负例训练的后续立项，本轮不自动训练。'
 ]
 text=Path('/Users/tianxd/.codex/attachments/996fb6b8-c58e-4959-b27e-825251b4923f/已粘贴的文本.txt').read_text();section=text.split('# 二十四、')[1].split('# 二十五、')[0];qs=re.findall(r'^\d+\. (.+)$',section,re.M);assert len(qs)==len(qa)==36
 answers='\n\n'.join(f'### {i}. {q}\n\n{a}' for i,(q,a) in enumerate(zip(qs,qa),1))
 body=f'''---
type: results-report
date: 2026-10-28
experiment_line: attack_mechanism_discrimination
round: 01
purpose: mechanism-and-reranker-diagnosis
status: offline_completed_with_forward_authorization_blocker
source_artifacts: [reports/analysis-output/analysis-report.md, reports/analysis-output/stats-appendix.md, reports/analysis-output/figure-catalog.md, reports/analysis-output/provenance.json]
linked_experiments: [manifests/EXPERIMENT_REGISTRATION.json, manifests/POSTHOC_KNOWLEDGE_CONTROLS.json]
linked_results: [MECHANISM_BASELINE_RESULTS.csv, RERANKER_SCORING_VALIDATION.json]
---

# R3 攻击行为机制表示与ATT&CK技术判别

主状态 **MECHANISM_REPRESENTATION_EXECUTED**。已完成全部可授权离线工作：Cross-Encoder分数诊断、30逻辑步骤冻结、机制提取与关系来源检查、216知识卡、49主实验加16后注册混杂控制，共63375条真实非神经预测。**没有证明新的独立算法贡献**。新GTE/CE机制前向未获得覆盖本轮授权，全部NA；独立人审PENDING，外部TEST未就绪。

当前判断：不继续增加规则、关系图或DGPR模块。当前BM25关系/动作标签的评分通道未生效，先解决表示接口、独立证据参考和同固定模型对照资格；若机制表示仍无收益，再考虑领域适配，而非把工程来源一致性包装成机制理解。

## 继承与实验协议

核验冻结752个既有资产，旧目录/评价器/预测保持不变。P0仍为195逻辑步骤、975查询、216父技术、7场景、34执行。P0=EXPOSED_DEV，P1/P2=RELATED_DEV。DGPR背景文件确认REJECT当前Full、EARLY_STOP_FIX_ONLY，没有新DGPR、Agent、RL或训练。

日志只来自上一轮V2 prefix已授权P0片段，RAW/LITERAL/LITERAL+RELATIONS/RAW+LITERAL及清洗/去角色/去结果/去动作控制共享同一进一步选取的原生事实。所有日志视图≤2000 UTF8 bytes、知识≤1000 bytes。**字节cap不是实际GTE Token测量**，实际Token长度当前NA；不能声称严格等Token神经实验。由于共同cap，RAW也更短，不与上一轮29.23%或历史27.79%直接比增益。

16.1原知识203描述/13缺失保留全部216。卡片只取通用词形与源片段，不写Gold规则或普遍必要条件；与观察分离，条件不确定保留UNKNOWN。传感器自带Txxxx注释在预测文本中等长掩码。Gold仅用于旧结果分层及输出固定后的评价，不进入提取器/模型输入。

## Cross-Encoder实际诊断

5850条件按ID与raw logit完全重建；固定对跨20/50/100及两池分数最大差0，原因是原运行复用cache。这排除了K特有的保存分数变化，但不构成新的批次稳定性复测。原实现query/log在前、技术描述在后、eval、无跨候选Softmax、降序rank均在冻结源码中可核查；官方模型卡支持高logit方向。没有按CAM得分反转排名。

**输出维度/config正文和独立单例/批次forward尚未重新验证**。Token truncation=False与输入长度断言可见；上游日志预算截取和65份知识描述截取真实存在，整体语义影响未排除。因此结论限定保存记录层面“未发现足以解释退化的实现错误”，不能声称完全排除适配问题。

Embedding Top100有101/975完全召回缺失，750/975有Gold候选而最终Top10失败。随着池扩大，更多非步骤Gold的高分候选挤入：T1204、T1601、T1592等最常见，精确排名和分数分布全交付。它们是相对步骤标签的错误候选，不是逐行已证明不可能发生的技术。机制原因仍UNRESOLVED。

## 真实机制结果

{main_table}

全部65条件、Top1/5/10、Precision/Recall/F1、逐样本和分场景结果见CSV。主49条件在任何本轮输出前固定；额外16条件在观察主结果后登记，专门检查知识来源范围与词序混杂，不冒充预注册结论。

原描述下BM25 Literal Top10从13.54%到17.03%，MRR .0356到.0417；95%Top10差CI[-.0062,.0790]、Holm p1。CHAR从14.87%降至9.13%。关系没有改变BM25 Literal排名；SCORER_CHANNEL_AUDIT发现新增关系/动作标签在知识词表中均无posting，因此BM25忽略这些特征，不能将其零差异解读为关系语义无用。简单机制匹配Top10=4.31%。没有稳定跨检索器/场景的机制增益。

知识卡有部分数值提升，但其可见片段来自完整K2，而原描述有1000字节前缀限制。CARD_PREFIX_ONLY控制仍有不同变化；保留词频打乱卡片词序后，BM25在4视图×975样本完整216排名**全部一致**。所以不能把BM25卡片成绩归因结构推理。CHAR变化也可能仅来自n-gram邻接，不足以证明语义关系。

## 图与统计

![表示对照]({ROOT}/reports/analysis-output/figures/figure-01-mechanism.png)

图1应看到Literal效果随检索器改变；BM25的关系通道未生效，CHAR变化不足归因。先查表示—评分器接口，当前不扩充关系复杂度。

![知识混杂控制]({ROOT}/reports/analysis-output/figures/figure-02-knowledge-control.png)

图2应看到知识内容分配和词序/词袋因素足以改变或保持成绩；不能据最高柱选择新算法。两图为描述统计，无独立测试含义。

统计按195逻辑步骤先聚合5查询，单协议一次确定性计算，非975独立样本。2000 bootstrap、5000 signflip、172项统一Holm；包含后注册控制，均属探索性。共享场景/脚本可能违反交换性假设，不能作泛化推断。详细mean/SD、CI、效应差和p均保存；无机制语义参考，不给支持判断准确率。

## 30例与来源合法性

冻结30不同步骤，实际10降级/6提升/6共同失败/4共同正确/4召回失败，场景分布{selection['scene_counts']}。全量评价不只用这30例。逐例CASE_ANALYSIS只报告原生字段和排名变化，不从错分推断缺日志或机制不存在。

34510字段/997关系/1866知识提及可源回查，12项安全不变量通过。只有同源原生audit key成员关系和明确时间BEFORE，不以PID相等、名称或时间近认证生命周期/因果。uid0只是状态；success字段只认证该syscall报告，exit0未自动成功。工程一致性不等于语义准确率。

盲审包不含Gold、sample_id、层别和模型结果，管理映射隔离；30例均PENDING，没有开发Agent冒充人工。真实独立人审尚无，不评分机制支持Precision/Recall/语义正确率。

## 权限与外部数据

没有新增模型/权重下载、GPU/LLM前向或服务器写入/上传。上一轮预算未重置。新的具体授权请求已准备：4文件9597914字节，指定新服务器项目、同名venv、只读固定模型和依赖、GPU0显存15%/CPU2线程/batch8等全部列明；截至本报告未获得覆盖本轮的明确答复，新表示神经条件为MODEL_FORWARD_NOT_AUTHORIZED。官方文档访问与备用下载存在连接/自动审查超时，没有绕过。

实际核查OTRF/Mordor APT29本地26步派生参考：存在技术标签与自称human_reviewed元数据，但原生日志/原计划、许可、脚本独立性和旧ID映射未完整资格认证，且副本已暴露；不能作为新独立TEST。另核查ExCyTIn现有图QA，任务单位不是ATTACK原生日志步骤标签，拒作该任务TEST。未下载大型归档。CONV-A01及受限PwnKit步骤/别名仍未授权且未读取正文。

## 决策与局限

NO-GO当前组合作为独立算法贡献；保留IR作诊断。BM25的局部数值提升不稳健，关系/动作标签通道未生效；卡片/关系贡献未排除词汇、清洗与知识选择混杂。若取得本轮GPU明确授权，只执行已冻结同模型对照，不改方向或挑样本；否则神经结论保持NA。下一步先独立审查30例、区分标签可观测性与模型排序；在此基础上决定机制判别还是领域适配。本轮不自动启动新训练或大型数据下载。

## 36项逐条回答

{answers}

## 复现与交付索引

原始分数诊断、consistency/rank transitions/failure taxonomy；30例ID/依赖/盲包；IR/schema/source trace/源码；16.1卡片和覆盖；主47775预测在MECHANISM_BASELINE_PREDICTIONS，posthoc15600预测在experiments/KNOWLEDGE_CONTROL_PREDICTIONS；65条件统一结果与消融；source/统计/图在reports/analysis-output；外部资格与新GPU精确请求均独立保存。最终完整性以results/FINAL_VALIDATION.json与manifests/DELIVERY_SHA256.json为准。
'''
 md('R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md',body)
 print('Generated core reports, strict analysis bundle,36 answers and honest unrun neural statuses.')
if __name__=='__main__':main()
