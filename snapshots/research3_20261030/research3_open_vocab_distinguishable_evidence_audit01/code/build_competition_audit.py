"""Nonindependent post-seal comparison from inspected definitions and facts.

No old AI assessments,rank values or baseline outcomes feed semantic decisions.
Manual exceptions encode source-based candidate checks; defaults explicitly
retain unestablished predicates,not false technique occurrences.
"""
import hashlib,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from build_first_pass import binding,source_type,csvout
R=Path(__file__).resolve().parents[1]
def load(n):return json.loads((R/n).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
# First branch is not an exhaustive parent definition. No external completion.
PARTIAL_BRANCH={'T1016','T1027','T1053','T1059','T1070','T1071','T1078','T1087','T1090','T1132','T1216',
'T1499','T1505','T1548','T1552','T1553','T1555','T1559','T1561','T1562','T1563','T1564','T1568','T1584','T1590','T1596','T1598','T1608'}
# New manual candidate interpretations: (level,source union lines,reason).
# Entries not present in a query's candidate packet are never emitted as a
# compared candidate. Intersect every support with that exact query.
SPECIAL={
'1-13':{'T1552':('PARTIAL',[1,2,3,6,7,11,13,14,16,18,19,21,23,24],'metadata.google.internal的DNS查询不等于向实例元数据API请求凭据；没有API路径或凭据结果。'),
         'T1590':('PARTIAL',[1,2,6,11,16,21],'有网络域名/端点信息，但没有独立认证的受害IP搜集用途；普通解析可同样解释。')},
'1-15':{'T1543':('PARTIAL',[6],'vim参数指向systemd服务文件，缺少创建/修改及重复执行的状态；与自启配置共享准备线索。')},
'1-2':{'T1190':('PARTIAL',[9,10,14,15],'拒绝的TCP探测不能建立利用公开应用漏洞或初始访问；仅支持网络请求背景。')},
'1-25':{'T1021':('SCOPE',[17,19,20,22],'实际为SSH会话凭据，不是正文VNC变体；不能补全其完整父类。')},
'1-26':{'T1021':('SCOPE',[14,16,17],'当前SSH凭据记录不定义VNC操作，父类其他分支未完整提供。'),
         'T1082':('PARTIAL',[7],'仅检查lsusb程序是否存在，尚非详细系统/硬件信息获取。')},
'1-27':{'T1082':('PARTIAL',[7],'date是特定时间查询，缺少OS/硬件版本等完整系统信息；泛化信息读取与具体时间对象不能默认互斥。')},
'1-28':{'T1083':('PARTIAL',[7,9,16,22],'find路径或请求涉及文件搜索；有明确virtualbox参数的视图可与VME检查共享文件查找动作，但当前候选出现的r0没有参数。'),
         'T1082':('PARTIAL',[9,16,22],'寻找virtualbox文件可能用于主机环境信息，但没有系统配置结果；与虚拟化检查的目的联系未认证。'),
         'T1021':('SCOPE',[4,12,19,25],'SSH session closed只显示会话背景，正文VNC与父类范围无法完成映射。'),
         'T1133':('PARTIAL',[4,12,19,25],'SSH会话退出不充分建立外部远程服务被用于初始/持续访问；网络边界和身份用途未知。')},
'1-29':{'T1105':('PARTIAL',[1,2,6,7],'ELF下载派生签名和网络流部分关联文件输入；缺少原生文件结果及外部受控边界绑定。')},
'1-3':{'T1190':('PARTIAL',[1,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18],'XSS/passwd/Tomcat等请求模式既可来自扫描也可来自利用尝试；签名不提供漏洞或初始入侵结果。'),
        'T1594':('PARTIAL',[5,6,7,8,10,11,12,13,14,15,16,17,18],'Web路径访问可相容搜集网站信息，但没有返回内容/受害站点目标或信息使用。')},
'1-30':{'T1105':('PARTIAL',[2,9],'HTTP200 README或curl参数关联取回文件；未独立绑定受控外部端与被控环境。'),
         'T1016':('PARTIAL',[1,2,3,8,9],'网络GET/连接可相容连通性检查，也可为文件下载，检查目的未建立。')},
'1-38':{'T1105':('PARTIAL',[1,3,6,7,9,11],'wget参数记录文件下载请求；不认证返回文件、内容或边界。')},
'1-41':{'T1105':('PARTIAL',[1,3,6,8],'wget请求不建立完整传输成功或受控边界；与修改PAM是不同动作。')},
'1-42':{'T1105':('PARTIAL',[1,6,10],'派生ELF下载签名不建立认证修改或完整输入文件内容。'),
         'T1140':('NONE',[],'cat/xargs路径与审计十六进制表示不是进程实际解码/反混淆证据。')},
'2-19':{'T1016':('PARTIAL',[8,10,12],'单域DNS与网络连接不等于确认互联网连通性的测试；目的和检查结果未建立。')},
'2-21':{'T1590':('PARTIAL',[2,4,6,8,10,12,14],'多个PTR获取系统标识也可能服务于IP网络信息搜集；阶段/主体/目标角色未知，无法排除共同解释。')},
'3-17':{'T1560':('PARTIAL',[2,3],'dpkg-deb打包请求共享归档工具行为，但对象为软件包，不认证所收集数据的归档产物。')},
'3-18':{'T1018':('PARTIAL',[1,4,5],'仓库域名解析只有单端点信息，不等于枚举其他系统。'),
         'T1590':('PARTIAL',[1,4,5],'仓库DNS不认证搜集受害网络IP用途；是常规软件管理解释。')},
'3-25':{'T1105':('PARTIAL',[1,2,3,5,6,7,9,10,11,12,13,14],'curl/ELF下载告警部分支持工具传输准备，不建立文件落盘或加密行为。')},
'3-26':{'T1218':('SCOPE',[1,3],'Linux动态加载器/opt程序不等于正文Rundll32；父类完整范围不可评价。'),
         'T1070':('SCOPE',[7,8],'文件重命名不是可见正文中的清除系统日志；其他父类分支未提供。')},
'3-30':{'T1070':('SCOPE',[1,2,7,8,10,12,15,16],'删除图片/标注并非可见正文中的清系统日志；父类FileDeletion标题不是完整判别合同。'),
         'T1564':('SCOPE',[10,12],'rm删除数据不建立AV排除路径；隐藏分支范围不足以由此裁定。')},
'3-34':{'T1039':('PARTIAL',[1,2,5],'NFS及共享路径访问可关联网络共享内容；无敏感文件读取/收集结果。'),
         'T1005':('PARTIAL',[5],'vim文件访问请求没有获取数据的结果；共享/本地角色未知。'),
         'T1570':('PARTIAL',[1,2],'NFS通信不认证传输工具内容、方向或被控端点间移动。')},
'3-40':{'T1105':('PARTIAL',[1,2],'curl|bash管理任务存在，但pipeline success不证明下载内容正确取得；缺少源端角色和文件结果。')},
'3-46':{'T1005':('PARTIAL',[1,3,6,7,9,10],'cat私钥路径是本地数据访问请求；不见读取结果或SharePoint语义。')},
'3-60':{'T1105':('PARTIAL',[1,2],'管理任务中curl下载请求可共现工具传输，不能从pipeline退出状态认证文件内容。'),
         'T1570':('PARTIAL',[1,2],'工具获取与集中部署可能共现；源目的均被控内部主机及实际文件流不明。')},
'3-7':{'T1005':('PARTIAL',[5,7,10,11],'仅cat本地CA文件请求；邮件投递视图不能借用其文件访问证据。')},
'5-2':{'T1185':('PARTIAL',[1,3,5,7],'浏览器登录自动化不建立浏览器被注入/会话劫持；无控制权或窃取证据。'),
        'T1056':('PARTIAL',[3,5],'输入用户名/密码是提供输入，不是捕获输入；网页字段存在不证明Keylogging。')},
'5-3':{'T1190':('PARTIAL',[1],'auth参数200响应是API访问，不建立漏洞利用或初始访问。')},
'6-1':{'T1571':('PARTIAL',[1,6],'HTTP8086为非标准Web端口线索；没有C2关系或绕行上下文。')},
'6-26':{'T1053':('SCOPE',[3],'timedate服务请求不是WindowsTaskScheduler或Cron作业操作；父类范围没有完整正文。')},
'6-28':{'T1217':('PARTIAL',[1,3],'浏览器存储路径是信息保存位置，但删除journal不是枚举浏览历史/账号信息。')},
'6-29':{'T1217':('PARTIAL',[1,3],'Firefox自身rename不建立有人读取浏览器信息；仅存储活动。')},
'6-34':{'T1217':('PARTIAL',[1,3],'sessionstore路径未显示信息枚举，不能把缓存维护当浏览信息窃取。')},
'6-59':{'T1129':('NONE',[],'只见python解释器调用，不见共享模块或负载加载。'),
         'T1202':('PARTIAL',[1,2,4],'python从stdin执行是解释器运行准备；无间接工具绕过限制与实际脚本内容。')},
'7-6':{'T1609':('PARTIAL',[2,3],'containerd exec进程清理错误提示容器执行背景；无管理API调用或指令，不能与PUT自动作因果绑定。')}
}

def main():
 seal=load('audit/FIRST_PASS_SEAL.json');assert all(sha(R/e['path'])==e['sha256'] for e in seal['files'])
 first=[json.loads(s) for s in (R/'review/FIRST_PASS_CASE_EVIDENCE.jsonl').read_text().splitlines()]
 packets=[json.loads(s) for s in (R/'inputs/SHUFFLED_COMPETITOR_PACKETS.jsonl').read_text().splitlines()]
 defs=load('inputs/COMPETITOR_FROZEN_DEFINITIONS.json');golddefs=load('review/GOLD_CONDITION_REGISTRY.json')
 aid={x['step']:x for x in load('inputs/FIRST_PASS_READING_AID.json')}
 cat={}
 for t,d in defs.items():
  m=re.search(r'Adversaries\b|An adversary\b|Once established within a system',d)
  body=d[m.start():] if m else None
  clause=re.split(r'(?<=[.!?])\s+',body,maxsplit=1)[0] if body else None
  scope=golddefs[t]['definition_scope'] if t in golddefs else 'FIRST_VARIANT_NOT_COMPLETE_PARENT' if t in PARTIAL_BRANCH else 'GENERAL_VISIBLE_CORE'
  cat[t]={'technique_id':t,'frozen_description':d,'description_sha256':hashlib.sha256(d.encode()).hexdigest(),
   'literal_core_clause':clause,'behavior_body_available':body is not None,'scope':scope,
   'parent_scope_complete_not_claimed':True,'optional_examples_not_universal_requirements':True,
   'missing_definition_reason':None if body else 'Only names/tactics or truncated list of subtype headings;no behavior proposition supplied. Do not complete from title or memory.'}
 dump('review/COMPETITOR_DEFINITION_AUDIT.json',cat);dump('review/SECOND_PASS_MANUAL_INTERPRETATIONS.json',SPECIAL)
 comps=[];audits=[];diagnoses=[];eligible=[];pairs=[]
 body_missing_query_count=0
 for q,p in zip(first,packets):
  assert q['sample_id']==p['sample_id'];step=q['logical_step_id'];own={f['fact_id']:f for f in q['visible_facts']}
  assessment=[];pairrows=[]
  for c in p['competitors_in_actual_review_order']:
   t=c['technique_id'];definition=cat[t]
   lev,ulines,why=SPECIAL.get(step,{}).get(t,('NONE',[], '当前逐行可见内容未建立该候选的核心命题：'+str(definition['literal_core_clause'])+'。既有步骤笔记和当前字面记录没有该机制所需动作/对象/结果，未建立不表示技术未发生。'))
   texts={aid[step]['lines'][i-1]['text'] for i in ulines};refs=[f for f,x in own.items() if x['text'] in texts]
   # A manual union note is not evidence if absent from this sampled view.
   if lev!='NONE' and not refs:lev='NONE';why='该视图不含步骤中其他采样的候选线索；不能跨查询借用。'+why
   ev='NOT_EVALUABLE' if not definition['behavior_body_available'] or lev=='SCOPE' else 'PARTIALLY_SUPPORTED' if lev=='PARTIAL' else 'NOT_ESTABLISHED'
   b=binding([{'text':own[f]['text']} for f in refs]);src=sorted({source_type(own[f]['text']) for f in refs}) if refs else ['NO_SUPPORTING_SOURCE']
   contexts=[{'condition_id':q['review_id']+'_'+t+'_CANDIDATE_CORE','condition_type':'CANDIDATE_CORE',
     'condition_text':definition['literal_core_clause'],'evidence_status':ev,'supporting_fact_ids':refs if ev=='PARTIALLY_SUPPORTED' else [],
     'contradicting_fact_ids':[],'context_fact_ids':refs if ev!='PARTIALLY_SUPPORTED' else [],
     'supporting_source_type':src if ev=='PARTIALLY_SUPPORTED' else ['NO_SUPPORTING_SOURCE'],**b,
     'missing_information':[definition['missing_definition_reason'] or why],
     'scope_limitations':[definition['scope'],'full parent subtype coverage not established','adversarial attribution not inferred'],
     'reasoning':why,'human_review_required':True},
    {'condition_id':q['review_id']+'_'+t+'_CANDIDATE_BINDING','condition_type':'OBJECT_PRECONDITION_RESULT_BINDING',
     'condition_text':'将候选核心命题中的动作、对象/前提及其必需结果绑定到同一主体、资产和时间；示例不是通用必要条件',
     'evidence_status':'NOT_EVALUABLE' if ev=='NOT_EVALUABLE' else 'NOT_ESTABLISHED',
     'supporting_fact_ids':[],'contradicting_fact_ids':[],'context_fact_ids':refs,'supporting_source_type':['NO_SUPPORTING_SOURCE'],**b,
     'missing_information':['不能由工具名、日志字段或相邻事件补出完整机制和结果；'+why],
     'scope_limitations':[definition['scope'],'current frozen view only'],'reasoning':why,'human_review_required':True}]
   assessment.append({'technique_id':t,'description_sha256':definition['description_sha256'],'definition_scope':definition['scope'],
     'definition_behavior_body_available':definition['behavior_body_available'],'candidate_evidence_level':lev,
     'conditions':contexts,'condition_evidence_status':ev,'sufficient_candidate_support':'NOT_ESTABLISHED' if ev!='NOT_EVALUABLE' else 'NOT_EVALUABLE',
     'relevant_fact_ids':refs,'reasoning':why,'unprovided_additional_information_needed':True})
  opaque=[x['technique_id'] for x in assessment if not x['definition_behavior_body_available']]
  body_missing_query_count+=bool(opaque)
  for g in q['gold_audits']:
   for c in assessment:
    if g['fresh_relatedness_level']=='SCOPE' or c['condition_evidence_status']=='NOT_EVALUABLE':label='NOT_EVALUABLE'
    elif g['fresh_relatedness_level']=='INPUT_UNKNOWN':label='INSUFFICIENT_INPUT'
    elif c['candidate_evidence_level']=='PARTIAL' and g['fresh_relatedness_level'] in {'DIRECT','PARTIAL'}:label='BOTH_COMPATIBLE_NOT_DISTINGUISHABLE'
    elif g['observable_necessary_conditions_supported_AI_only']:
     label='DISTINGUISHABLE_SUPPORT_FOR_GOLD'
    else:label='NEITHER_SUFFICIENTLY_SUPPORTED'
    shared=sorted(set(g['supporting_fact_ids'])&set(c['relevant_fact_ids']))
    row={'sample_id':q['sample_id'],'gold_technique_id':g['technique_id'],'competitor_technique_id':c['technique_id'],
      'comparison_label':label,'gold_condition_ids':g['condition_ids'],'competitor_condition_ids':[z['condition_id'] for z in c['conditions']],
      'gold_relevant_fact_ids':g['supporting_fact_ids'],'competitor_relevant_fact_ids':c['relevant_fact_ids'],
      'shared_fact_ids':shared,'shared_observable_conditions': ('当前引用行的共同行为可同时相容两种解释；对象角色/用途/结果仍未建立' if shared else '未认证共同机制；一般背景或缺少事实不能建立互斥性'),
      'distinguishing_condition':golddefs[g['technique_id']]['distinguishing_condition'],
      'distinguishing_fields_reliably_bound':g['observable_necessary_conditions_supported_AI_only'] and not c['relevant_fact_ids'] and label=='DISTINGUISHABLE_SUPPORT_FOR_GOLD',
      'can_exclude_competitor_as_having_occurred':False,
      'definition_scope_limit':c['definition_scope'],
      'additional_information_needed':[c['reasoning'],'Gold：'+g['reasoning']],
      'reasoning': '仅比较本次明列的可见行为命题；支持Gold表示相对该可评价命题的可见证据，不等于排除整个父类或证明唯一真值。'+
       ('候选/Gold命题缺失或范围未解，保留不可评价。' if label=='NOT_EVALUABLE' else '缺少完整必要链时不选唯一技术。'),
      'blinding_status':'INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE','qualified_independent_reference':False}
    pairrows.append(row);pairs.append(row)
  # Strict query-level distinction requires an interpretable comparison for
  # every selected competitor,not only a favorable subset of pair results.
  distingu=any(all(x['comparison_label']=='DISTINGUISHABLE_SUPPORT_FOR_GOLD' for x in pairrows if x['gold_technique_id']==g['technique_id']) for g in q['gold_audits'])
  related=q['related_behavior_evidence_AI_only'];core=q['observable_gold_core_supported_AI_only'];scope=q['gold_scope_unresolved_AI_only']
  diagnosis='GOLD_SCOPE_OR_GRANULARITY_UNRESOLVED' if scope else 'INSUFFICIENT_VISIBLE_EVIDENCE' if not related else 'EVIDENCE_PRESENT_AND_DISTINGUISHABLE' if distingu else 'UNRESOLVED' if core else 'EVIDENCE_PRESENT_BUT_AMBIGUOUS'
  reason='Gold目标范围先决未解。' if scope else '当前视图未建立Gold核心必要行为；背景/准备或代码不可见不作反证。' if not related else '全选定候选有可解释的区分证据，仍只是非独立AI候选。' if distingu else '有直接核心行为，但候选定义/语义区分不能完整评价，不能归因为算法错误。' if core else '仅有部分相关机制，缺少完整条件或区分字段，不能确定唯一Gold。'
  secondary=['NONINDEPENDENT_AI_AUDIT','BOUNDED_VISIBLE_SCOPE','REFERENCE_MISSING']
  if opaque:secondary.append('COMPETITOR_DEFINITION_BODY_MISSING')
  if scope:secondary.append('TARGET_DEFINITION_SCOPE_UNRESOLVED')
  if any(g['fresh_relatedness_level'] in {'BROAD','PREPARATORY'} for g in q['gold_audits']):secondary.append('BROAD_OR_PREPARATORY_CONTEXT')
  comp={'sample_id':q['sample_id'],'review_id':q['review_id'],'second_pass_audit_complete':True,
    'semantic_comparison_status':'NONINDEPENDENT_AI_PRE_AUDIT_NOT_GOLD','competitors_in_actual_serialized_comparison_order':[x['technique_id'] for x in assessment],
    'reviewer_exposure_note':'same context;reviewer also read canonical-ID definition/index coverage tables;randomized serialization is not proof of independent cognitive order',
    'shuffle_seed':p['shuffle_seed'],'candidate_scope':p['candidate_scope'],'candidate_count_reviewed':10+len(q['gold_technique_ids']),
    'competitor_definitions_checked':10,'all_216_reviewed':False,'unreviewed_candidate_count':216-10-len(q['gold_technique_ids']),
    'candidate_assessments':assessment,'pairwise_comparisons':pairrows,'pair_comparison_attempts':len(pairrows),
    'evaluable_pair_comparison_count':sum(x['comparison_label'] not in {'NOT_EVALUABLE','INSUFFICIENT_INPUT'} for x in pairrows),
    'missing_body_candidate_ids':opaque,'full_subset_distinguishable_AI_only':distingu,
    'qualified_distinguishable_evidence':'NOT_AVAILABLE_WITHOUT_INDEPENDENT_REFERENCE',
    'scope_limitation':'subset only;uninterpretable candidates remain unknown;no all216 exclusion or unique true technique claim',
    'blinding_status':'INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE','human_review_required':True}
  comps.append(comp)
  record={**q,'phase':'FIRST_PASS_PLUS_POST_SEAL_COMPETITOR_AUDIT','audit_complete':True,
    'competing_audit_reference':'review/COMPETING_TECHNIQUE_AUDIT.jsonl#'+q['sample_id'],
    'primary_diagnosis':diagnosis,'secondary_diagnoses':secondary,'diagnosis_reason':reason,
    'candidate_scope':p['candidate_scope'],'candidate_count_reviewed':comp['candidate_count_reviewed'],
    'all_216_reviewed':False,'unreviewed_candidate_count':comp['unreviewed_candidate_count'],
    'distinguishable_AI_only':distingu,'qualified_reference_status':'INDEPENDENT_SEMANTIC_REFERENCE_NOT_AVAILABLE',
    'independent_test_status':'DEVELOPMENT_SELECTED_ON_GTE_MISS_NOT_INDEPENDENT_TEST',
    'qualified_residual_error_status':'NOT_AVAILABLE'}
  audits.append(record)
  diagnoses.append({'sample_id':q['sample_id'],'logical_step_id':q['logical_step_id'],'primary_diagnosis':diagnosis,
     'secondary_labels':secondary,'reasoning':reason,'audit_complete':True,'reference_status':'NONINDEPENDENT_AI_NOT_GOLD'})
  eligible.append({'sample_id':q['sample_id'],'logical_step_id':q['logical_step_id'],'scenario_id':q['scenario_id'],
    'gold_technique_ids':q['gold_technique_ids'],'primary_diagnosis':diagnosis,'evidence_present':related,
    'distinguishing_evidence':'AI_SUBSET_SUPPORT_ONLY' if distingu else 'NOT_AVAILABLE_FOR_FULL_SELECTED_SUBSET' if opaque else 'NOT_ESTABLISHED',
    'gold_scope_status':'UNRESOLVED' if scope else 'NOT_INDEPENDENTLY_QUALIFIED',
    'input_coverage_status':'BOUNDED_FROZEN_VIEW;omitted_count_unknown','candidate_scope':p['candidate_scope'],
    'independent_reference_status':'INDEPENDENT_SEMANTIC_REFERENCE_NOT_AVAILABLE','human_review_required':True,
    'eligible_for_algorithm_error_analysis':False,'AI_candidate_for_human_priority':core or related,
    'eligible_for_confirmatory_primary_metric':False,'independent_test_qualified':False,
    'eligibility_reason':'AI审查不是合格独立参考；'+reason+'；候选缺正文及完整父类覆盖另列，不能以有利子集替代。'})
 for path,data in [('review/CASE_EVIDENCE_AUDIT.jsonl',audits),('review/COMPETING_TECHNIQUE_AUDIT.jsonl',comps),('review/GOLD_COMPETITOR_PAIR_AUDIT.jsonl',pairs)]:
  (R/path).write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in data))
 csvout('review/CASE_DIAGNOSIS.csv',diagnoses);csvout('review/CASE_EVALUATION_ELIGIBILITY.csv',eligible)
 dump('audit/SECOND_PASS_SEAL.json',{'created_utc':datetime.now(timezone.utc).isoformat(),'first_pass_seal_sha256':sha(R/'audit/FIRST_PASS_SEAL.json'),
  'query_audits':len(audits),'competitor_assessments':sum(len(c['candidate_assessments']) for c in comps),'Gold_competitor_pair_attempts':len(pairs),
  'new_historical_baseline_result_reads_in_this_phase':False,'same_context_not_independent':True,
  'files':[{'path':p,'sha256':sha(R/p)} for p in ['review/CASE_EVIDENCE_AUDIT.jsonl','review/COMPETING_TECHNIQUE_AUDIT.jsonl','review/GOLD_COMPETITOR_PAIR_AUDIT.jsonl','review/CASE_DIAGNOSIS.csv','review/CASE_EVALUATION_ELIGIBILITY.csv','review/COMPETITOR_DEFINITION_AUDIT.json','review/SECOND_PASS_MANUAL_INTERPRETATIONS.json']]})
 print(json.dumps({'queries':len(audits),'competitor_assessments':3840,'pairs':len(pairs),'missing_body_candidate_types':sum(not x['behavior_body_available'] for x in cat.values()),
  'queries_with_missing_candidate_body':body_missing_query_count,'pair_labels':dict(Counter(x['comparison_label'] for x in pairs)),
  'primary_diagnoses':dict(Counter(x['primary_diagnosis'] for x in diagnoses))},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
