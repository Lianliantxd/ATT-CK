"""Descriptive audit counts and bounded Chinese report,not model evaluation."""
import csv,json,hashlib
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from build_first_pass import csvout
R=Path(__file__).resolve().parents[1];B=R.parent
def load(n):return json.loads((R/n).read_text())
def dump(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def write(n,x):(R/n).write_text(x.strip()+'\n')
def main():
 q=[json.loads(s) for s in (R/'review/CASE_EVIDENCE_AUDIT.jsonl').read_text().splitlines()]
 comp=[json.loads(s) for s in (R/'review/COMPETING_TECHNIQUE_AUDIT.jsonl').read_text().splitlines()]
 cat=load('review/COMPETITOR_DEFINITION_AUDIT.json');base=load('audit/BASELINE_QUALIFICATION_SUMMARY.json')
 old=load('audit/OLD_ASSET_HASH_SNAPSHOT.json');conditions=[z for x in q for z in x['gold_conditions']]
 required=[z for z in conditions if z['required_for_observable_behavior_contract']]
 diag_names=['EVIDENCE_PRESENT_AND_DISTINGUISHABLE','EVIDENCE_PRESENT_BUT_AMBIGUOUS','INSUFFICIENT_VISIBLE_EVIDENCE',
 'GOLD_SCOPE_OR_GRANULARITY_UNRESOLVED','INPUT_OR_SOURCE_MAPPING_UNRESOLVED','UNRESOLVED']
 evnames=['DIRECTLY_SUPPORTED','PARTIALLY_SUPPORTED','EXPLICITLY_CONTRADICTED','NOT_ESTABLISHED','NOT_OBSERVABLE_IN_CURRENT_VIEW','NOT_EVALUABLE']
 primary={k:sum(x['primary_diagnosis']==k for x in q) for k in diag_names}
 paircount=Counter(z['comparison_label'] for x in comp for z in x['pairwise_comparisons'])
 counts={'unit':'frozen query unless explicitly stated;all semantic counts are current same-context AI audit,not qualified truth',
  'frozen_queries':len(q),'completed_limited_audit_records':len(q),'unique_logical_steps':len({x['logical_step_id'] for x in q}),
  'unique_input_text_hashes':len({x['input_view_hash'] for x in q}),
  'Gold_target_assignments':sum(len(x['gold_audits']) for x in q),'unique_Gold_techniques':len({g['technique_id'] for x in q for g in x['gold_audits']}),
  'Gold_condition_instances':len(conditions),'required_observable_condition_instances':len(required),
  'optional_context_attribution_instances':len(conditions)-len(required),
  'deduplicated_logical_Gold_conditions':len({(x['gold_technique_id'],x['condition_type'],x['condition_text']) for x in conditions}),
  'displayed_line_instances':sum(x['visible_scope']['visible_record_count'] for x in q),
  'primary_diagnosis_counts_exclusive':primary,
  'related_behavior_queries_AI_only':sum(x['related_behavior_evidence_AI_only'] for x in q),
  'observable_Gold_necessary_behavioral_contract_supported_queries_AI_only':sum(x['observable_gold_core_supported_AI_only'] for x in q),
  'full_Gold_semantic_sufficiency_qualified':'NOT_AVAILABLE',
  'full_selected_candidate_subset_distinguishable_queries_AI_only':sum(x['distinguishable_AI_only'] for x in q),
  'qualified_Gold_vs_competitor_distinguishability':'NOT_AVAILABLE',
  'broad_or_preparatory_only_queries_AI_only':sum(any(g['fresh_relatedness_level'] in {'BROAD','PREPARATORY'} for g in x['gold_audits']) and not x['related_behavior_evidence_AI_only'] for x in q),
  'Gold_scope_questions_queries_AI_only':sum(x['gold_scope_unresolved_AI_only'] for x in q),
  'current_insufficient_visible_evidence_primary_queries':primary['INSUFFICIENT_VISIBLE_EVIDENCE'],
  'bounded_input_scope_queries':len(q),'known_omitted_source_record_counts':0,
  'competitor_candidate_instances':sum(len(c['candidate_assessments']) for c in comp),
  'Gold_competitor_pair_attempts':sum(c['pair_comparison_attempts'] for c in comp),
  'evaluable_supplied_predicate_pair_comparisons':sum(c['evaluable_pair_comparison_count'] for c in comp),
  'pair_label_counts':{k:paircount[k] for k in ['DISTINGUISHABLE_SUPPORT_FOR_GOLD','DISTINGUISHABLE_SUPPORT_FOR_COMPETITOR',
    'BOTH_COMPATIBLE_NOT_DISTINGUISHABLE','NEITHER_SUFFICIENTLY_SUPPORTED','INSUFFICIENT_INPUT','NOT_EVALUABLE']},
  'unique_competitor_techniques':len(cat),'competitor_techniques_without_behavior_body':sum(not x['behavior_body_available'] for x in cat.values()),
  'missing_behavior_body_technique_ids':[t for t,x in cat.items() if not x['behavior_body_available']],
  'queries_with_at_least_one_competitor_body_missing':sum(bool(c['missing_body_candidate_ids']) for c in comp),
  'queries_with_every_selected_competitor_body_available':sum(not c['missing_body_candidate_ids'] for c in comp),
  'all216_reviewed_queries':sum(x['all_216_reviewed'] for x in q),
  'human_adjudication_completed':0,'documented_qualified_independent_reference_records':0,
  'actual_qualified_residual_ranking_error_count':'NOT_AVAILABLE','qualified_baseline_recovery_count':'NOT_AVAILABLE',
  'cross_protocol_lexical_comparison_queries':base['native_lexical_cross_protocol_queries'],
  'historical_outcome_comparisons_completed':0,'human_review_required_queries':sum(x['human_review_required'] for x in q),
  'currently_admitted_algorithm_error_analysis_queries':0,'confirmatory_primary_metric_eligible_queries':0,'independent_test_qualified_queries':0,
  'Gold_condition_status_counts':{k:sum(x['evidence_status']==k for x in conditions) for k in evnames},
  'required_Gold_condition_status_counts':{k:sum(x['evidence_status']==k for x in required) for k in evnames},
  'formal_accuracy_Precision_Recall_F1_significance_computed':False,
  'reference_boundary':'documented qualified-reference count0 is a work record;true residual/error count remainsNOT_AVAILABLE;0 admitted is a gate outcome,not proof0 real errors'}
 dump('results/QUERY_AGGREGATE_COUNTS.json',counts)
 summary=[];human=[]
 for x,c in zip(q,comp):
  pairdist=Counter(z['comparison_label'] for z in c['pairwise_comparisons'])
  summary.append({'sample_id':x['sample_id'],'logical_step_id':x['logical_step_id'],'scenario_id':x['scenario_id'],
    'Gold_technique_ids':x['gold_technique_ids'],'primary_diagnosis':x['primary_diagnosis'],'secondary_diagnoses':x['secondary_diagnoses'],
    'related_behavior_AI_only':x['related_behavior_evidence_AI_only'],'observable_Gold_behavior_contract_AI_only':x['observable_gold_core_supported_AI_only'],
    'full_subset_distinguishable_AI_only':x['distinguishable_AI_only'],'qualified_distinguishability':'NOT_AVAILABLE',
    'Gold_scope_question_AI_only':x['gold_scope_unresolved_AI_only'],'pair_label_counts':dict(pairdist),
    'missing_body_competitor_ids':c['missing_body_candidate_ids'],'reviewed_candidate_count':c['candidate_count_reviewed'],
    'unreviewed_candidate_count':c['unreviewed_candidate_count'],'qualified_residual_error_count':'NOT_AVAILABLE',
    'human_review_required':True,'audit_complete_with_evaluability_limits':True})
  human.append({'sample_id':x['sample_id'],'logical_step_id':x['logical_step_id'],'Gold_technique_ids':x['gold_technique_ids'],
    'priority':'SCOPE_AND_DEFINITION' if x['gold_scope_unresolved_AI_only'] else 'DIRECT_CORE_AND_DEFINITION' if x['observable_gold_core_supported_AI_only'] else 'PARTIAL_BINDING' if x['related_behavior_evidence_AI_only'] else 'OBSERVATION_COVERAGE',
    'literal_evidence_fact_ids':list(dict.fromkeys(f for g in x['gold_audits'] for f in g['supporting_fact_ids'])),
    'Gold_condition_ids':[z['condition_id'] for z in x['gold_conditions']],'missing_candidate_body_ids':c['missing_body_candidate_ids'],
    'required_review':'独立核验目标范围、原生/派生事实绑定、必要结果与竞争命题；缺定义先保留NOT_EVALUABLE；不重跑AI作Gold。',
    'reviewer_status':'PENDING_NO_HUMAN_CONTACT_THIS_TASK','reference_status':'AI_PRE_AUDIT_NOT_GOLD','blinding_status':'INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE'})
 csvout('results/QUERY_SUMMARY.csv',summary);csvout('protocol/HUMAN_REVIEW_QUEUE.csv',human)
 grouped=defaultdict(list)
 for x,c in zip(q,comp):
  for g in x['gold_audits']:grouped[g['technique_id']].append((x,g,c))
 gs=[]
 for t,rr in sorted(grouped.items()):
  gs.append({'Gold_technique_id':t,'query_count':len(rr),'logical_steps':len({x['logical_step_id'] for x,g,c in rr}),
   'related_behavior_queries_AI_only':sum(g['fresh_relatedness_level'] in {'DIRECT','PARTIAL'} for x,g,c in rr),
   'observable_Gold_behavior_contract_supported_AI_only':sum(g['observable_necessary_conditions_supported_AI_only'] for x,g,c in rr),
   'full_Gold_sufficiency_qualified':'NOT_AVAILABLE','full_subset_distinguishable_AI_only':sum(all(z['comparison_label']=='DISTINGUISHABLE_SUPPORT_FOR_GOLD' for z in c['pairwise_comparisons'] if z['gold_technique_id']==t) for x,g,c in rr),
   'qualified_distinguishability':'NOT_AVAILABLE','Gold_scope_question_queries_AI_only':sum(g['fresh_relatedness_level']=='SCOPE' for x,g,c in rr),
   'current_input_insufficient_for_this_target_AI_only':sum(g['fresh_relatedness_level'] in {'NONE','BROAD','PREPARATORY','INPUT_UNKNOWN'} for x,g,c in rr),
   'human_review_required':len(rr),'documented_qualified_independent_reference':0,'confirmatory_metric_eligible':0})
 csvout('results/GOLD_TECHNIQUE_SUMMARY.csv',gs)
 cs=[]
 for name,rr in [('ALL_GOLD_CONDITIONS',conditions),('REQUIRED_OBSERVABLE_GOLD_CONDITIONS',required),('OPTIONAL_ATTRIBUTION_CONTEXT',[z for z in conditions if not z['required_for_observable_behavior_contract']])]:
  for state in evnames:cs.append({'scope':name,'evidence_status':state,'condition_instance_count':sum(x['evidence_status']==state for x in rr),
     'scope_total_condition_instances':len(rr),'deduplicated_logical_condition_count':len({(x['gold_technique_id'],x['condition_type'],x['condition_text']) for x in rr}),
     'unit':'query-by-Gold-by-condition instance;not independent events or attacks'})
 csvout('results/CONDITION_SUMMARY.csv',cs)
 decision='GO_AFTER_INPUT_OR_LABEL_AUDIT'
 blockers=[
 {'id':'B1','scope':'all384','status':'OPEN','reason':'当前上下文既有历史预测/AI判断暴露；本轮禁止新增Agent，独立审查者/协调者不可用。','effect':'INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE；本轮不是人工Gold。'},
 {'id':'B2','scope':'379queries;12candidateIDs','status':'CONFIRMED_AS_FROZEN_TEXT_AVAILABILITY_LIMIT','reason':'实际竞争定义中11种仅名称/战术，另T1574文本全为变体标题，没有行为正文。','effect':'不能从名称/外部记忆补条件；对应配对NOT_EVALUABLE，不能证明整组Top10可排除。'},
 {'id':'B3','scope':'34target-scopeflagqueries','status':'AI_SCOPE_QUESTION_NOT_CONFIRMED_MISLABEL','reason':'具体目标行为与冻结正文变体范围不合，例如本地rm对云生命周期正文、ACL对NAT正文。','effect':'不回改标签/定义，不把部分父类变体未满足推成父类错误。'},
 {'id':'B4','scope':'all384','status':'OPEN','reason':'没有合格独立人工参考，源日志省略数未知、原生事件身份未独立认证。','effect':'真实Gold充分性、可验证残余排序错误NOT_AVAILABLE；正式指标不计算。'},
 {'id':'B5','scope':'all384full216nativelexicalcomparison','status':'CONFIRMED_PROTOCOL_DIFFERENCE','reason':'全216词法与GTE知识文本整体不同，查询也多数不同。','effect':'CROSS_PROTOCOL_NOT_COMPARABLE；不以旧成绩差作算法因果比较。'},
 {'id':'B6','scope':'historicaloutcomes','status':'NOT_PERFORMED_BY_QUALIFICATION_RULE','reason':'本轮没有完整选定候选区分并获合格参考的案例。','effect':'未新增打开逐例C4/词法结果以补残余错误；384行资格审计完成，结果比较工作量0，真实性能数量未知。'},
 {'id':'B7','scope':'legacyreport','status':'PRE_EXISTING_DISCLOSED','reason':'旧融合报告与其历史清单有1项此前已披露的哈希差异。','effect':'原样保留；本轮末对当前hash快照核验，不声称旧清单全部无差异。'}]
 dump('protocol/BLOCKER_REGISTER.json',blockers)
 write('protocol/REVIEW_PROTOCOL.md',f'''
# 本轮实际协议 v2 / 2026-10-29

本轮执行同上下文AI离线审计，新增模型/Agent/网络/训练/服务器调用均0。沿用结果分析与报告技能的审计原则；用户明确要求本地交付，生成所列审计表和限制报告，不作统计推断或收益图。

第一遍只读取白名单冻结文本、目标定义及源/覆盖元数据。当前上下文已有暴露，移除字段不消除记忆。重新阅读54份字面目标定义与80步骤全部737个去重阅读行及384查询出现映射；保留2178显示行实例。新手写笔记和条件释义未导入旧AI标签/旧判断脚本。分组辅助用于阅读，不合并查询、不跨视图借用。复合动作、结果及主体归属分开。

初次封存前后，候选访问仍未开始时修正一次表达：步骤笔记包含视图对比，不能作为单视图的复合“直接支持”命题；背景条件缩窄为当前引用字面行。v1封存及文件在audit/phase1_v1_superseded保留，版本历史明确无定义或手写判断更改，未读候选。以audit/FIRST_PASS_SEAL.json最终封存为第一遍锁定点。

第一遍封存后才从旧卡提取候选ID与冻结定义，先按ID中性排序，再以样本绑定SHA256种子打乱；每例实际序列/seed保存在SHUFFLED_COMPETITOR_PACKETS。未输出分数、seen标志或原排名。协调器与审查者没有独立上下文；本轮语义解释还查看按ID排列的定义目录和候选集合覆盖索引。因此只说随机化封装/逐例序列，不把它称为独立认知盲审。

实际检查125种竞争定义，其中34种已作为目标字面定义读过且版本一致，另91种全文读取；逐步骤/视图查看全部候选集合映射。按新手写候选解释与当前事实逐对记录，缺机制不补事实，缺定义正文不凭名称补条件。当前可评判的是冻结可见命题，父类完整范围未声称穷尽；没有竞争条件支持不等于竞争技术未发生。

第二遍全部384候选审计记录封存后才进行历史基线资格核验。没有合格参考及完整可区分案例，所以不新增读取逐例C4/词法输出值；只核验文件存在/hash与输入/知识协议。GTEmiss属性来自冻结选择和候选与目标ID不交集，不证明目标语义正确。

来源类型标注按用户枚举：原生格式的冻结日志副本为NATIVE_LOG_RECORD，但不认证原始文件真实性或独立事件身份；IDS/Wazuh模式为DERIVED_PATTERN；自动化运行轨迹/解析 companion为OTHER_DOCUMENTED_SOURCE。静态十六进制解释另标DERIVED_PATTERN，仅读完整字节，不执行或补尾。Fact ID始终是派生显示行定位符；孤立片段不能当独立事件/单独直接依据。

必要行为合同与完整攻击意图分开：Gold条件{len(conditions)}实例，其中{len(required)}为可见行为必要合同，其他为归属/背景。支持必要行为核心不等于作者Gold完整真值或攻击意图已确认。定义中的may/示例不是每条技术必需的共同实现方式。公开定义是语义参考来源，不是日志事实。

引用字段口径：逐条件supporting_fact_ids只有在该条件DIRECTLY/PARTIALLY_SUPPORTED时才表示支持该条件；逐目标gold_audits.supporting_fact_ids是聚合选定引用，BROAD/PREPARATORY/SCOPE目标下仅指背景/范围问题的上下文，不表示支持Gold。后续Gold_relevant_fact_ids也只指相关引用，必须与条件状态和fresh_relatedness_level一起读取，不能单看字段名认证语义。

主要诊断按优先级：目标范围疑问→D；（有实际源映射不可核验错误才E，本轮无已确认实例）；无相关Gold机制→C；全部候选有可评价区分支持→A；有核心直接行为但整组区分仍不可评价→F；其余相关部分机制→B。次级标签重叠。A的数量0是未有查询进入该审计类别，不能解释成真实可区分案例数确定为0。

全部384条完成的是有限审计及不可评价原因登记；并非全部配对都获得可评价结果，更不是384次独立人审。当前完整Gold语义、合格区分及残余错误保留NOT_AVAILABLE。机械校验只核验来源/覆盖/数据合同，不认证语义正确。
''')
 write('protocol/BLINDING_INTEGRITY_REPORT.md',f'''
# 实际盲化和暴露

**INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE**。当前助手在此前任务中已经接触历史预测、错误诊断和旧AI预审，本轮用户又直接给出历史数量。未创建新Agent，未取得独立协调者或真人审查者，也未证明OS级隔离。

本轮第一遍新增语义输入仅为源日志、目标冻结定义、覆盖和身份元数据；没有导入旧AI判断作为标准答案。准备阶段工具曾解析含候选/分数的混合旧卡JSON容器以查看字段schema，仅向审查上下文输出字段名/容器结构，没有显示候选值/分数。因此不能声称工具或底层字节未接触预测字段，也没有独立协调者。第一遍实际阅读是步骤内去重行加逐查询位置，不是独立逐查询上下文。

FIRST_PASS_SEAL中“new_current_candidate_payload_access_before_seal=false”只描述本轮审查上下文尚未新增显示/解释候选值，不是文件字节访问隔离证据；准确的传输访问披露另见TRANSPORT_ACCESS_DISCLOSURE.json。该限定不恢复任何独立盲审资格，原字段和历史记录均保留。

第一遍最终封存hash与时间在audit/FIRST_PASS_SEAL.json；候选包装回执在audit/CANDIDATE_PACKAGING_RECEIPT.json，引用该封存hash。之后才将10候选的ID与原定义封装，每例固定SHA256种子随机序列，原排名/分数未输出。125竞争定义及91个新正文已读，覆盖索引为中性ID排序；随机序列由序列化比较记录保存，并不证明AI的认知读取顺序始终随机或没有候选来源偏差。

候选集合来自旧模型，本身带模型选择偏差；不能因打乱顺序就称候选无偏。新比较为非独立AI预审，未接触新Agent意见，未取得任何人审标签。历史基线阶段在第二遍封存后，只做限定资格/hash核验，没有足够资格时不扩展逐例结果读取。

独立人工裁定本轮完成0，当前成果不得转成Gold、训练监督或确认性测试。所有384均保留人审要求。未来最低要求：冻结知识生成/父子范围的可追溯审计；原始作者标签与可见行为/人审充分性/完整攻击意图四者分离；预测隔离的真人双审与仲裁；明确候选全集或子集范围、未知与曝光；不经新授权扩大数据读取或补下载知识。
''')
 # Analysis notes precede the final report;no inferential or model metrics.
 write('reports/analysis-report.md',f'''
# 可辨识性审计分析

问题：冻结384个漏召回开发查询的当前日志，是否有支持和区分目标技术的证据？本轮单位是查询，条件与候选实例另列。

新事实：第一遍及第二遍有限审计均有384记录；相关机制AI判断96、可见必要行为核心31、目标范围疑问34。竞争125种定义中的12种无可用行为正文，影响379查询；本轮不能补定义后仍冒充原冻结比较。

配对5200中，193个对所提供命题有相对Gold支持、57个共同相容、2958个均不足、1964不可评价、28输入不足。193不是193条唯一查询、不是193个错误，也不意味整组Top10或全216排除。整体可区分查询的合格真值仍NOT_AVAILABLE。

Claim：当前不具备可验证残余排序错误参考。来源：逐例资格与阻断；允许“未取得参考、结果未知”，禁止“真实错误数为0”。下一检查：先核冻结定义与父子范围，再独立人审。Decision keep。
Claim：输入/知识合同先于新算法。来源：12缺正文候选、34目标范围线索及跨协议字节差异；允许作为下一步优先级，不称漏召回主因已证实。Decision keep with boundary。
Claim：新模型将改善这些问题。无本轮方法实验或独立参考，禁止，Decision discard。
''')
 write('reports/stats-appendix.md',f'''
# 分母与不适用统计

384查询、80逻辑步骤、145文本hash、520目标分配；2178显示行不是独立原生事件。新条件模式共有{len(conditions)}实例，必要行为{len(required)}，归属/背景{len(conditions)-len(required)}，去重逻辑条件{counts['deduplicated_logical_Gold_conditions']}。旧2618是另一模式，不应为凑数保留旧语义判断或用差值解释改进。

候选实例3840、Gold—候选配对5200、定义种类125、可见命题配对可评价3208；这些都不是查询数。每例实际只检查Gold与10候选，未审199至205个候选，all216均false。主要类别合计384且互斥；相关96、核心31、范围34与缺正文379等是非互斥查询属性。

显示核心支持是同上下文AI判断；没有参考所以不计算语义准确率、Precision、Recall、F1、CI、显著性或算法收益。没有新预测/模型评价。0人审/0准入是实际工作或资格计数；真实Gold充分性和合格残余错误数NOT_AVAILABLE，不用0代替未知。
''')
 write('reports/figure-catalog.md','''
# 图件

NOT_CREATED。用户要求的是证据审计，本轮没有合格语义真值或新实验，不画暗示真实根因/性能分布的科学推断图。完整精确计数见CSV与报告表。
''')
 cn={'EVIDENCE_PRESENT_AND_DISTINGUISHABLE':'证据存在且可区分','EVIDENCE_PRESENT_BUT_AMBIGUOUS':'证据相关但有歧义','INSUFFICIENT_VISIBLE_EVIDENCE':'当前可见证据不足','GOLD_SCOPE_OR_GRANULARITY_UNRESOLVED':'目标范围/粒度未解','INPUT_OR_SOURCE_MAPPING_UNRESOLVED':'输入或源映射未解','UNRESOLVED':'仍无法可靠归因'}
 table='\n'.join(f'| {cn[k]} | {v} |' for k,v in primary.items())
 rootfiles=['DISTINGUISHABLE_EVIDENCE_AUDIT_REPORT.md','inputs/FROZEN_CASE_MANIFEST.json','review/CASE_EVIDENCE_AUDIT.jsonl',
 'review/CONDITION_EVIDENCE_MATRIX.csv','review/COMPETING_TECHNIQUE_AUDIT.jsonl','review/CASE_DIAGNOSIS.csv',
 'review/CASE_EVALUATION_ELIGIBILITY.csv','review/BASELINE_RESIDUAL_ERROR_AUDIT.csv','results/QUERY_SUMMARY.csv',
 'results/GOLD_TECHNIQUE_SUMMARY.csv','results/CONDITION_SUMMARY.csv','protocol/REVIEW_PROTOCOL.md',
 'protocol/BLOCKER_REGISTER.json','protocol/BLINDING_INTEGRITY_REPORT.md','protocol/HUMAN_REVIEW_QUEUE.csv','RUN_MANIFEST.json','results/FINAL_VALIDATION.json']
 index='\n'.join(f'- [{n}]({R/n})' for n in rootfiles)
 report=f'''
---
type: results-report
date: 2026-10-29
experiment_line: open-vocab-distinguishable-evidence-audit
round: 1
purpose: evidence-and-error-qualification
status: limited_nonindependent_audit_reference_and_definition_blocked
source_artifacts:
  - {R}/reports/analysis-report.md
  - {R}/reports/stats-appendix.md
  - {R}/results/QUERY_AGGREGATE_COUNTS.json
linked_experiments:
  - {B}/research3_open_vocab_failure_mechanism_diagnosis01
linked_results:
  - {R}/review/CASE_EVIDENCE_AUDIT.jsonl
---

# 384条Unseen漏召回：证据可辨识性与归因审计 / 2026-10-29

## 执行结论与边界

**384条的有限证据审计与竞争定义检查均已形成结果，完整独立语义裁定仍受阻。** 状态PARTIAL_WITH_REFERENCE_AND_DEFINITION_BLOCKERS。不能将其称为独立盲审、正式Gold或确认性算法错误集。唯一决策：**{decision}**。

本轮重新读了实际冻结文本和定义，未导入旧AI标签作为结论；但上下文此前已有暴露，仍为INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE。没有新增Agent或模型调用。第一遍封存、候选包装、第二遍封存、基线资格核验的次序与hash分别保留。

本轮确认了一个此前门控中没有逐候选展开的具体限制：**实际涉及的125种竞争技术中，12种缺少可用行为正文，影响379/384查询。** 11种只有名称/战术，另T1574的1000字符全为变体标题，未到行为正文。这是当前冻结文本的实际可用性问题，不是对完整ATT&CK标准的断言，更不能直接证明GTE漏召回的因果主因。

## 覆盖、来源和完成定义

冻结384唯一sample_id，输出384，缺失0、重复0；80逻辑步骤、145种输入文本、54个目标技术、520个查询—目标分配。全部查询保持原顺序，没有合并不同采样或多Gold。逐案比较含3840竞争候选实例、5200个Gold—候选配对尝试。可评价所提供命题的配对3208，其余1992明确保留不可评价/输入不足，不能声称5200个都获得了充分语义结论。

实际阅读54份冻结Gold原文，80步骤内全部737条去重显示行及每个查询的位置映射；这些涵盖2178显示行实例。之后检查125种竞争定义，34种与此前本轮读过的Gold相同、91种新增；查看全部步骤和采样的候选集合映射。阅读辅助表不是合并评价，当前引用严格与本查询求交。其全过程仍共用AI上下文，不是384次独立裁定。

Fact ID沿用源的VISIBLE_LINE定位符，是派生显示行ID，不是独立认证的原生事件。NATIVE_LOG_RECORD仅标冻结副本中的原生日志格式，不证明原始文件真实性；IDS/Wazuh签名是DERIVED_PATTERN，自动化轨迹另列。主体账号、进程、路径、端点及时间仅按可见字段绑定，不把root当攻击者，不把相邻时间当因果；原始完整日志和省略数未知，不自动确认截断或预处理错误。

第一遍有一次候选访问前的措辞修正：将步骤内多视图阅读笔记与单视图直接支持命题分开。v1和历史hash保存，未改字面定义或手写判断，也没有在看竞争候选后回改Gold侧结论。最终以FIRST_PASS_SEAL为准。

## 查询主要诊断（互斥，分母384）

| 主要诊断 | 查询数 |
|---|---:|
{table}

A类0表示本轮没有查询获得完整选定候选子集的区分支持，不表示真实可区分查询数已知为0。E类0也不证明源映射完美，只是没有足够核验依据将某个已完成查询归为该主要问题。F类29不是未审查占位：这些查询有可见必要行为核心，但候选定义或区分资格不能闭合，具体配对原因已保存。未读取的基线逐例结果另行记未执行，不藏在F类中。

目标范围疑问优先保留D；没有必要核心行为的背景/准备或代码缺失归C；有部分相关机制而不能判别归B。所有分类是非独立AI审计，不是真实攻击根因分布；256不能解释为原日志没证据或256个模型错误由预处理造成。

## 十个科研问题的实际答案

1. **可追溯相关行为证据**：96/384查询有直接或部分机制线索的本轮AI判断；不是96个已确认攻击，也不是96个正确预测。
2. **足以支持Gold必要条件**：31/384在本轮明示的“可见必要行为合同”上得到支持，覆盖账户创建、硬件/时间/窗口查询尝试、PTR标识查询、服务停止及配置管理任务执行等。完整Gold语义适用性、攻击者归属和意图的合格参考结论仍**NOT_AVAILABLE**；不能把31当正式充分Gold。
3. **区分Gold与主要竞争技术**：对可评价的已提供命题，有193个配对相对支持Gold，分母为5200配对；没有查询完成整组10候选的充分区分支持。合格独立区分查询数**NOT_AVAILABLE**，不以0代替。193不是193条查询或193个算法错误。
4. **仅宽泛行为描述**：73/384属于“至少有BROAD/PREPARATORY背景，但没有任何直接/部分Gold机制”的操作性AI分类；另65条主要类别为相关但歧义。两者口径不同，不能混成一类准确率。
5. **Gold范围/粒度疑问**：34/384至少一个目标有具体疑问，不是34个已证实错标。完整父技术与子类型的合同仍需核验。
6. **可验证历史排序错误**：本轮取得合格独立人工裁定0；可验证残余错误真实数量**NOT_AVAILABLE**。不能用AI核心支持或193有利配对补齐资格。
7. **已被强基线正确排序的数量**：**NOT_AVAILABLE**。没有满足整组区分及参考门槛的查询，本轮未扩大读取其逐例C4/词法输出；不把未比较解释为无命中。
8. **跨协议无法公平比较**：384/384相对历史native全216 BM25/字符检索存在知识或查询合同差异；属于可核验的比较资格限制，不是384个模型错误的因果解释。
9. **需要独立人工裁定**：384/384。人审队列全量保留，没有联系审查者或把AI重复运行当人审。
10. **是否支持启动方法实验**：不支持。本轮仅完成有限审计、资格统计及决策，没有训练、模型推理或新算法结果。

## 可观察动作、定义解释和竞争判断必须分开

REV_0020/0021的useradd new user及属性是创建状态的直接相关记录；REV_0022等的lspci、REV_0033的date、REV_0256至0259的wmctrl-l是明确请求，不能补出未显示的输出。REV_0173至0175明确Stopped/Deactivated exim4；REV_0181至0185与REV_0201至0205记录Puppet catalog Exec success，但未认证脚本内容和操作者目的。

command-v lsusb只是工具存在性检查；xclip-output请求不证明采集成功；encrypt参数和jpg改名后缀不认证密文或不可用；Firefox存储维护不认证输入/剪贴板捕获；浏览器自动输入密码不等于捕获密码。单一execve失败或connect -115不能反驳整个技术。

Gold范围例子：本地rm与T1485云生命周期正文；本地Puppet CA路径与T1213信息仓库正文；Shorewall ACL改变与T1599 NAT正文；Linux管道与T1218 Rundll32主体正文。这里是冻结父类参考范围不完整的具体问题，不用某一变体条件否定整个父技术，也不临时扩大定义来迎合Gold。

第二遍候选打乱只减少原排序提示，不能消除模型选候选偏差。程序按实际保存shuffle序列序列化比较；AI也查看中性ID定义目录和覆盖索引，因此不声称独立认知顺序始终随机。每例只看Gold+10候选，实际11至17种，未审199至205种；all_216_reviewed全部false。全局读过145种不同目标/竞争定义也不等于每例审完145或216候选。

候选缺正文清单：{', '.join(counts['missing_behavior_body_technique_ids'])}。不得从技术名称、外部记忆或另一个版本填充当前冻结必要条件。379条具有至少一个此类候选；其余5条不意味着已获独立Gold或足够日志证据。

## 条件级与技术级汇总

本轮Gold条件2555实例：DIRECTLY_SUPPORTED240、PARTIALLY_SUPPORTED201、EXPLICITLY_CONTRADICTED0、NOT_ESTABLISHED1990、NOT_OBSERVABLE_IN_CURRENT_VIEW12、NOT_EVALUABLE112。其中必要可见行为条件1905，直接110、部分201、未建立1470、不可观测12、不可评价112；其余650为归属/背景条件，不能都当Gold必要条件。去重逻辑条件{counts['deduplicated_logical_Gold_conditions']}，按技术ID+条件类型+文字计算，不是独立事件。旧2618属于旧条件模式，本轮不为凑相同数量导入旧标签或删查询。

54个Gold技术的逐技术查询、相关机制、核心合同、范围/输入限制、人审及资格均完整存CSV；同查询有多个Gold不能跨技术行相加当独立查询。193个Gold有利配对、57个共同相容、2958个均不足、1964个不可评价、28个输入不足均为AI命题级比较；不计算正式语义Precision/Recall/F1或显著性。没有科学推断图，只有实际计数表与审计数据。

## 历史结果有限对照：资格不是新评价

证据第二遍封存后，核验历史基线文件、版本和文本合同。当前Gold与候选选择满足冻结GTE miss属性，但作者标签不因此成为正确参考。没有完整区分且获合格独立参考的查询，故384行残余审计主类均REFERENCE_INSUFFICIENT，逐例C4/词法结果比较完成量0，不能冒充性能数值0。

历史native全216词法与GTE候选ID一致，但整体知识文本不同（216中仅41份逐字相同）；每条比较都存在知识协议差异，样本当前文本逐字相同仅{base['native_lexical_query_text_matches_within384']}/384。对照文件已存在并hash，不代表本轮查看或重新评价其全部预测。CROSS_PROTOCOL_NOT_COMPARABLE为384条的次级资格标记，和REFERENCE_INSUFFICIENT可以同时成立。不能据此说强基线没有恢复任何Gold，也不能把既有32例C4损失重新当本轮发现。

## 唯一科研决策与下一步最低材料

**{decision}**。

本轮有可追溯行为线索，不能说没有研究候选；但在独立参考之前，必须先核查已经实际发现的冻结知识可用性及父子范围合同：12种竞争条目没有行为正文、379查询整组比较受影响，34查询的目标定义范围有疑问。这个顺序是门控优先级，不是已识别主要失败原因，更不表示补定义必有模型收益。参考资格仍为随后必须满足的硬门槛。

最低材料：固定候选/知识版本与生成来源；对12种条目核查原冻结文档是否本就无正文或标题截断，区分知识覆盖与渲染/裁剪问题；对父/子技术适用范围及作者标签保留独立审计依据；给实际相关/核心行为查询做预测隔离的真人双审和仲裁，确认主体—动作—对象—结果及合理竞争解释。不得在本轮回写历史定义/标签或读取未授权原日志；若需要新知识版本或额外字段，应另行冻结并授权，不用新版本修补本轮成绩。

只有未来具备合格语义参考和明确可区分失败，才重新判断是否值得设计方法实验。当前384始终是按GTE漏召回筛选且已曝光的开发集，不会因人审、重命名或新目录变成独立测试。

## 资源、完整性及停止

新增模型/API/Agent/Embedding/CE调用0，训练0，下载0，GPU0，网络0，服务器0。当前助手的语义阅读属于AI预审，不冒充“未使用AI”；内部Token/CPU峰值未独立计量。只用已有Python标准库与静态解析，没有执行日志中的命令。

实际核验{len(old['assets'])}个旧资产，保留1项此前已披露的旧融合报告hash差异，不修复旧文件。核心输入在第一遍前锁定，其他旧资产广域hash清单在第二遍后建立，不能冒充全任务开始前OS快照；末次验证将对当前快照、核心早期hash和两次封存逐项核对。写操作只针对本轮新目录。

完成交付、机械核验与hash封存后停止；机械通过只证明文件、引用和合同记录一致，不认证语义结论。没有通过新的AI判断填补独立参考，没有启动下一轮模型实验。

## 实际交付文件（绝对路径）

{index}
'''
 write('DISTINGUISHABLE_EVIDENCE_AUDIT_REPORT.md',report)
 dump('RUN_MANIFEST.json',{'task_id':'R3_OPEN_VOCAB_DISTINGUISHABLE_EVIDENCE_AUDIT01','client_report_date':'2026-10-29',
  'run_version':'v2_firstpass_wording_amendment_before_candidate_access','execution_status':'PARTIAL_WITH_REFERENCE_AND_DEFINITION_BLOCKERS',
  'completed_scope':'384 bounded same-context Gold/competitor audits with explicit unevaluable reasons;no qualified reference or historical case outcome comparison',
  'final_decision':decision,'blinding_status':'INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE','counts':counts,
  'new_model_calls':0,'new_agent_calls':0,'new_training_runs':0,'downloads':0,'GPU_tasks':0,'network_access':False,'server_access':False,
  'historical_case_outcome_comparisons_completed':0,'new_model_metrics_computed':False,
  'first_pass_seal':load('audit/FIRST_PASS_SEAL.json'),'second_pass_seal':load('audit/SECOND_PASS_SEAL.json'),
    'first_pass_pre_candidate_revision':load('audit/FIRST_PASS_VERSION_HISTORY.json'),
    'preseal_mixed_transport_access':{'mixed_source_card_JSON_parsed_for_schema':True,'reviewer_visible_candidate_values_or_scores_newly_displayed_beforeseal':False,'no_underlying_prediction_byte_isolation_claim':True,'independent_coordinator':False},
  'old_asset_snapshot_path':str(R/'audit/OLD_ASSET_HASH_SNAPSHOT.json'),'legacy_hash_mismatches':old['legacy_version_differences'],
  'required_artifact_paths':rootfiles,'manifest_phase':'ANALYSIS_AND_REPORT_COMPLETE_PENDING_INDEPENDENT_MECHANICAL_VALIDATION',
  'actual_commands':['python3 -B research3_open_vocab_distinguishable_evidence_audit01/code/prepare_first_pass.py',
   'python3 -B research3_open_vocab_distinguishable_evidence_audit01/code/build_first_pass.py (v1 and wording-onlyv2 beforecandidateaccess)',
   'python3 -B research3_open_vocab_distinguishable_evidence_audit01/code/prepare_competitors.py',
   'python3 -B research3_open_vocab_distinguishable_evidence_audit01/code/build_competition_audit.py',
   'python3 -B research3_open_vocab_distinguishable_evidence_audit01/code/audit_baseline_eligibility.py',
   'python3 -B research3_open_vocab_distinguishable_evidence_audit01/code/summarize_audit.py'],
  'input_output_code_hashes':'PENDING_FINAL_SEAL','remaining_limitations':blockers,'stop_after_delivery':True})
 print(json.dumps({'primary_diagnoses':primary,'related_behavior_AI':counts['related_behavior_queries_AI_only'],
  'Gold_observable_behavior_AI':counts['observable_Gold_necessary_behavioral_contract_supported_queries_AI_only'],
  'broad_only_AI':counts['broad_or_preparatory_only_queries_AI_only'],'unique_conditions':counts['deduplicated_logical_Gold_conditions'],
  'decision':decision},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
