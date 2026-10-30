from audit_io import *
import collections,re
B=BASE/'research3_attack_technique_benchmark01';S=BASE/'research3_technique_strong_baselines_generalization02';M=BASE/'research3_attack_mechanism_discrimination01';D=BASE/'research3_domain_adaptive_contrastive_learning01';G=BASE/'research3_method_hypothesis_gate01'
count=json.loads((R/'results/AUDIT_COUNTS.json').read_text());replay=json.loads((R/'audit/BOUNDED_TRANSFORMATION_PROOF.json').read_text());rp={x['technique_id']:x for x in replay};defs=list(csv.DictReader((R/'TECHNIQUE_DEFINITION_AUDIT.csv').open()));scope=list(csv.DictReader((R/'GOLD_SCOPE_AUDIT.csv').open()));impact=list(csv.DictReader((R/'DEFINITION_IMPACT_SUMMARY.csv').open()))
# Explicitly read historical gate contracts and inventory fields; conclusions are context only.
gate_context={}
for f in ['ASSET_INVENTORY.csv','CASE_QUALIFICATION_MATRIX.csv','EXISTING_BASELINE_AUDIT.csv','METHOD_HYPOTHESIS_REGISTER.json','REFERENCE_REQUIREMENTS.md','GO_NO_GO_DECISION.md','FINAL_VALIDATION.json']:
 p=G/f;b=tracked(p,role='HISTORICAL_GATE_CONTEXT_NOT_REFERENCE');gate_context[f]={'sha256':digest(b),'bytes':len(b),'status':'CONTEXT_ONLY_NOT_SEMANTIC_TRUTH'}
 if f.endswith('.csv'):
  rr=list(csv.DictReader(b.decode().splitlines()));gate_context[f]['rows']=len(rr);gate_context[f]['fields']=list(rr[0]) if rr else []
 elif f.endswith('.json'):
  j=json.loads(b);gate_context[f]['fields']=list(j);gate_context[f]['final_decision']=j.get('final_decision')
 else:gate_context[f]['text']=b.decode()
save('audit/GATE_CONTEXT_INSPECTION.json',gate_context)
for i,p in enumerate(['/Users/tianxd/.codex/attachments/52f05c7a-c1df-416f-b565-d3d2ff77772a/已粘贴的文本.txt','/Users/tianxd/.codex/attachments/bef210d1-919c-429c-8717-7c00e426fd9b/已粘贴的文本.txt'],1):
 (R/('protocol/USER_REQUEST_PART_%d.txt'%i)).write_bytes(tracked(p,role='USER_AUTHORIZED_TASK_CONTRACT',source_type='ORIGINAL_SOURCE'))
# Exact static-code evidence snippets with file hash and line numbers, no execution of these modules.
code_specs=[
 ('AUTHOR_LABEL_SELECTION',B/'benchmark/run_benchmark.py',64,83,[str(B/'official_sources/labels.json')],'labels[scenario_variant-step].metadata.keys → official_technique_labels','COMPLETE_FOR_CHECKED_34_QUERY_IDS;raw logs not reread'),
 ('PARENT_NORMALIZATION',B/'evaluate_techniques.py',8,12,[],'validated Txxxx(.xxx) → split(".")[0]','MATCHES51_CHECKED_ORIGINAL_LABEL_ASSIGNMENTS'),
 ('AUTHOR_CANDIDATE_TITLE_GROUPING',B/'benchmark/run_benchmark.py',66,71,[str(B/'official_sources/mitre_matrix.json')],'691 matrix IDs →216parent IDs;append each name+tactics in matrix insertion order','PURE_SELECTED_DOC_REPLAY_MATCHES_SAVED_OFFICIAL_DOCS'),
 ('DESCRIPTION_EXTENSION',B/'benchmark/run_benchmark.py',161,174,[str(BASE/'provenance_baserepro_04/data/enterprise-attack-16.1.json.gz')],'iterate active STIXattack-patterns;normalize parent;append name+description in source order','PURE_SELECTED_DOC_REPLAY_MATCHES_SAVED_FULL_K2;11TARGET_IDS_HAVE_NO_OBJECT'),
 ('P0_COPY',S/'manifests/P0_FREEZE.json',None,None,[str(B/'datasets/extended_knowledge_documents.json')],'source→frozen_p0 copy','SAVED_JSON_EQUAL;manifest source/frozen hashes checked separately'),
 ('BASELINE_K2_COPY',S/'baselines/prepare_inputs.py',35,47,[str(S/'frozen_p0/datasets/extended_knowledge_documents.json')],'K2 copies frozen extension;K3 separate no-title variant','K2_EQUALS_FULL_EXTENSION;no subtype priority/sorting introduced for K2'),
 ('UTF8_PREFIX_CAP',M/'mechanism_ir/build_inputs.py',7,34,[str(S/'knowledge/K2_DESCRIPTION_16_1.json')],'clip(text,1000)=text.encode()[:1000].decode(utf8,errors=ignore)','PURE_SELECTED_DOC_REPLAY_EXACT;T1574_TITLE_PREFIX_EXCLUDES_ALL_BEHAVIOR'),
 ('DOMAIN_KNOWLEDGE_COPY',D/'data/prepare_grouped_data.py',29,59,[str(M/'attack_knowledge/KNOWLEDGE_TEXTS.json')],'copy K2 todata/KNOWLEDGE_K2;Goldparent normalization andretainraw_ground_truth','ALL216_SAVED_DOCS_EQUAL;51GOLD_ID_CHAINS_CHECKED'),
 ('AUDIT_CANDIDATE_PACKAGING',PREV/'code/prepare_competitors.py',12,38,[str(D/'data/KNOWLEDGE_K2.json')],'selectedhistorical candidateid/description exactequality;seedshuffle','384PACKETIDS_AND_DESCRIPTIONS_MATCH;no scoring/readjudication'),
 ('AUDIT_GOLD_PACKAGING',PREV/'code/prepare_first_pass.py',20,51,[],'copy frozen target definitions andmanifest;no new Gold normalization','PREVIOUS60DELIVERY_HASHES_MATCH;selectedGoldtext equalsdomainK2')]
pipeline=[]
for name,p,a,z,inputs,op,result in code_specs:
 b=tracked(p,role='STATIC_PIPELINE_CHAIN_CODE_OR_RECEIPT');snippet='\n'.join('%d: %s'%(i,l) for i,l in enumerate(b.decode().splitlines(),1) if a is not None and a<=i<=z) if a is not None else 'JSON copy receipt inspected;not executable code.'
 pipeline.append({'stage_id':name,'path':str(p),'sha256':digest(b),'code_or_source_version':'CURRENT_LOCAL_SHA256','line_start':a,'line_end':z,'input_paths':inputs,'input_fields':'metadata keys / name / tactics / STIX external_references,description;exact contract in excerpt','output_fields':'author raw IDs / grouped parent ID / serialized text as indicated','operation':op,'static_code_excerpt':snippet,'check_result':result,'reproducibility':'BOUNDED_PURE_EXPRESSION_CHECK' if name in ['AUTHOR_CANDIDATE_TITLE_GROUPING','DESCRIPTION_EXTENSION','UTF8_PREFIX_CAP'] else 'STATIC_INSPECTION_AND_EXISTING_ARTIFACT_EQUALITY','historical_code_executed':False,'evidence_level':'LEVEL_2_REPRODUCIBLE_TRANSFORMATION_PROOF' if name in ['AUTHOR_CANDIDATE_TITLE_GROUPING','DESCRIPTION_EXTENSION','UTF8_PREFIX_CAP'] else 'LEVEL_1_DIRECT_SOURCE_PROOF','missing_link':'author matrix upstream extraction/release not supplied;does not invalidate checked local conversion equality','limitations':'Proof is local saved input→output correspondence,not full original data authenticity or causal performance impact.'})
csvout('EXTRACTION_PIPELINE_AUDIT.csv',pipeline)
repair=[]
for d in defs:
 t=d['technique_id'];clip=t=='T1574'
 repair.append({'issue_id':'DEF_'+t,'technique_id':t,'issue_scope':'competitor behavior body missing','confirmed_cause':d['root_cause_status'],'repairability':d['repairability'],'available_materials':'full savedK2 andactiveSTIX parent/subtype bodies' if clip else 'author matrix ID/name/tactics andSTIX16.1 proof ofcoveragegap','minimum_missing_materials':'No missing text forT1574;need approved new rendering/budget contract before anyrepair' if clip else 'compatible versioned parent/subtype source text for'+t+';source acquisitionreceipt/hash;author matrix release or cross-version mapping rationale','requested_source_path':None if not clip else str(S/'knowledge/K2_DESCRIPTION_16_1.json'),'source_path_status':'Compatible source not named/provided;no fabricated filesystempath' if not clip else 'EXISTING_LOCAL_SOURCE','required_future_authorization':'Separate approval fornewknowledgeversion/newinputcontract;download/network ifneeded separatelyauthorized;no historical overwrite','current_authorization':'AUDIT_AND_REPAIR_PLAN_ONLY','repair_executed':False,'would_prove':'Changed inputtext/contract only;no automatic modelbenefit','would_not_prove':'Historical rankerrorcause,Goldcorrectness,SeenUnseentradeoff,independenttestvalidity'})
for t in sorted({r['gold_technique_id'] for r in scope if r['prior_scope_question_flag']=='True'}):
 repair.append({'issue_id':'SCOPE_'+t,'technique_id':t,'issue_scope':'author-parent scopequestion andparentbody outsidecurrentprefix','confirmed_cause':'ORDERED_PARENT_SUBTYPE_POOLING_PLUS_PREFIX_CAP;not confirmed Gold error','repairability':'REQUIRES_HUMAN_ADJUDICATION','available_materials':'original author labelmetadata,rawIDs,parent rule,full existingSTIX parent/subtype text','minimum_missing_materials':'author labelingrationale/scopecontract;independent human opinions and arbitration for listed queryIDs','requested_source_path':None,'source_path_status':'Label rationale/independentreference not supplied','required_future_authorization':'Human reference qualification andnewversion contract;do not contact outsiders automatically','current_authorization':'AUDIT_ONLY','repair_executed':False,'would_prove':'Qualified visible-behavior label scope afterindependent adjudication','would_not_prove':'Full attackintent or modelbenefit'})
repair.append({'issue_id':'MATRIX_UPSTREAM','technique_id':None,'issue_scope':'author matrix exactATTCKrelease andgenerationchain','confirmed_cause':'NOT_AVAILABLE','repairability':'REQUIRES_MISSING_SOURCE_ARTIFACT','available_materials':'pinned GitHub commit metadata andmatrix hash;no description fields','minimum_missing_materials':'author matrix generation/export recipe,source release/commit,original fields,compatible description crosswalk','requested_source_path':None,'source_path_status':'No known original filepath;must recover author-provided source information','required_future_authorization':'Read locally supplied provenance;network/download onlyif separatelyauthorized','current_authorization':'AUDIT_ONLY','repair_executed':False,'would_prove':'Upstream version alignment andcorrect compatible source','would_not_prove':'AI orauthorlabels automaticallycorrect'})
csvout('REPAIRABILITY_REGISTER.csv',repair)
# Verify existing source/version receipts instead of accepting filenames as provenance.
checks=[]
def hcheck(p,expect,origin):
 raw=tracked(p,role='SOURCE_OR_MANIFEST_HASH_COMPARISON');actual=digest(raw) if raw is not None else None;checks.append({'path':str(p),'expected_sha256':expect,'actual_sha256':actual,'expected_source':origin,'match':expect==actual,'qualification':'LOCAL_HASH_MATCH_ONLY_NOT_EXTERNAL_AUTHENTICITY'})
v=readj(B/'ATTACK_KNOWLEDGE_VERSION.json');hcheck(B/'official_sources/mitre_matrix.json',v['official_matrix_sha256'],str(B/'ATTACK_KNOWLEDGE_VERSION.json'));hcheck(BASE/'provenance_baserepro_04/data/enterprise-attack-16.1.json.gz',v['extension_sha256'],str(B/'ATTACK_KNOWLEDGE_VERSION.json'))
manifest=readj(B/'OFFICIAL_DATA_MANIFEST.json')
for e in manifest:
 p=Path(e['local_path'])
 if p.name in ['mitre_matrix.json','labels.json','commit.json','create_llm_prompt.py']:hcheck(p,e['sha256'],str(B/'OFFICIAL_DATA_MANIFEST.json'))
freeze=readj(S/'manifests/P0_FREEZE.json')
# Only already-audited source files are checked against this broader receipt.
state=json.loads(STATE.read_text())
def recurse(x):
 if isinstance(x,dict):
  for key in ['source','frozen_path','path']:
   if isinstance(x.get(key),str) and x[key] in state:
    expected=x.get('sha256') or x.get('source_sha256')
    if expected:hcheck(Path(x[key]),expected,str(S/'manifests/P0_FREEZE.json'))
  for v in x.values():recurse(v)
 elif isinstance(x,list):
  for v in x:recurse(v)
recurse(freeze)
# Prior disclosed legacy report mismatch is intentionally retained.
old=readj(PREV/'RUN_MANIFEST.json');legacy=old.get('legacy_hash_mismatches',[]);save('audit/LEGACY_HASH_MISMATCHES_PRESERVED.json',legacy)
for x in legacy:
 p=Path(x['path']);raw=tracked(p,role='KNOWN_PREEXISTING_HASH_DIFFERENCE_NOT_MODIFIED');actual=digest(raw)
 expected=x.get('expected_sha256') or x.get('expected')
 checks.append({'path':str(p),'expected_sha256':expected,'actual_sha256':actual,'expected_source':'previous explicitly disclosed legacy manifest','match':expected==actual,'qualification':'PREEXISTING_MISMATCH_PRESERVED_NOT_REPAIRED'})
save('audit/SOURCE_HASH_COMPARISONS.json',checks)
# Build complete inventory, retaining missing requested path vs existing relocated summary.
state=json.loads(STATE.read_text())
for key,e in state.items():
 p=Path(key)
 if p==BASE/'provenance_baserepro_04/data/enterprise-attack-16.1.json.gz':
  e.update(source_type='OFFICIAL_EXPORTED_DATA',source_version='STIX collection16.1 verified internally;local pinned SHA256',upstream_source='Existing local exported bundle;not downloaded or independently reauthenticated',extraction_script=str(B/'benchmark/run_benchmark.py'),transformation_history='activeattackpatterns groupedbyparent → titles+descriptions → UTF8prefix1000')
 elif p.name=='mitre_matrix.json':e.update(source_type='MAPPING_TABLE',source_version='author repo commit42bbd2cf8409f64a1e6c8fc936c91725e8c558b2;exactATTCKreleaseunknown',upstream_source='author matrixgeneration source notrecovered',extraction_script=str(B/'benchmark/run_benchmark.py'),transformation_history='691rawIDs→216parents;name+tactic prefix')
 elif p.name=='labels.json':e.update(source_type='AUTHOR_LABEL',source_version='authorcommit42bbd2cf8409f64a1e6c8fc936c91725e8c558b2',upstream_source='author metadata;not semanticGold',extraction_script=str(B/'benchmark/run_benchmark.py'),transformation_history='metadata keys→rawreference→parentnormalization')
 elif p.suffix=='.py':e.update(source_type='TRANSFORMED_ARTIFACT',qualification=e['qualification']+';STATIC_ONLY_OR_HASH_ONLY_NOT_EXECUTED')
 elif p==S/'knowledge/K2_DESCRIPTION_16_1.json':e.update(source_type='EXTRACTED_TEXT',upstream_source=str(B/'datasets/extended_knowledge_documents.json'),extraction_script=str(B/'benchmark/run_benchmark.py'),transformation_history='titles then append activeSTIXdescription inobjectorder')
 elif 'KNOWLEDGE_K2' in p.name or 'FROZEN_DEFINITIONS' in p.name:e.update(source_type='FROZEN_PROJECT_TEXT',upstream_source=str(M/'attack_knowledge/KNOWLEDGE_TEXTS.json'),extraction_script=str(M/'mechanism_ir/build_inputs.py'),transformation_history='UTF8byteprefix1000;subsequent exactcopies')
 elif not e['exists']:e.update(source_type='UNKNOWN_SOURCE',qualification='MISSING_PATH;do not treat as semantic proof')
 e['limitations']+=' Hash-only inspection of sealed supporting files is not semantic re-review. Source fields not recovered remain NOT_AVAILABLE.'
 if e['upstream_source'] is None:e['upstream_source']='NOT_AVAILABLE_OR_NOT_APPLICABLE;role is listed'
 if e['extraction_script'] is None:e['extraction_script']='NOT_AVAILABLE_OR_NOT_APPLICABLE'
 if e['transformation_history'] is None:e['transformation_history']='No additional transformation certified in this audit'
csvout('ASSET_SOURCE_INVENTORY.csv',list(state.values()))
blockers=[
 {'blocker_id':'B_SOURCE_COMPATIBLE_11','status':'UNRESOLVED','technique_ids':[d['technique_id'] for d in defs if d['technique_id']!='T1574'],'confirmed_fact':'matching behavior sources absent inexisting16.1;not extraction omission','minimum_need':'compatible versionedsource text plusauthorcandidate version/reconciliation','current_pipeline_cause_known':True,'upstream_version_or_missing_source_reason_known':False,'action_taken':'NONE;noexternalrecovery'},
 {'blocker_id':'B_MATRIX_UPSTREAM','status':'UNRESOLVED','confirmed_fact':'matrix fields name/tactics only;exactATTCKrelease andgenerating source notencoded/recovered','minimum_need':'matrix export recipe,original release/commit,compatible mapping','action_taken':'PINNED_LOCAL_COMMIT_AND_HASH_ONLY'},
 {'blocker_id':'B_SCOPE_34','status':'UNRESOLVED','confirmed_fact':'34query scopeclaims,51authorparentIDchainschecked;source parent bodiesrecoverable butsemanticapplicabilityunknown','minimum_need':'author rationale plusindependent human adjudication','action_taken':'QUEUE34FROZEN;NO_LABEL_CHANGE'},
 {'blocker_id':'B_REFERENCE','status':'NOT_AVAILABLE','confirmed_fact':'AI notesnotindependentGold;noqualifiedhumanreference ininspected records','minimum_need':'independentreviewopinions,exposure,arbitration,qualifiedevaluationcontract','action_taken':'NO_NEW_SEMANTIC_REVIEW'},
 {'blocker_id':'B_CAUSAL_PERFORMANCE','status':'NOT_EVALUATED','confirmed_fact':'379queryinputmembershipverified;historicalerrorcausesnotidentified','minimum_need':'future separatelyauthorizedfair sameprotocolcomparison afterinput/referencequalification','action_taken':'NO_EXPERIMENT'},
 {'blocker_id':'B_LEGACY_HASH','status':'PREEXISTING_DIFFERENCE_PRESERVED','details':legacy,'action_taken':'NOT_REPAIRED'},
 {'blocker_id':'B_REQUESTED_SUMMARY_LOCATION','status':'RESOLVED_BY_EXISTING_ALTERNATIVE','missing_path':str(PREV/'review/GOLD_TECHNIQUE_SUMMARY.csv'),'existing_path':str(PREV/'results/GOLD_TECHNIQUE_SUMMARY.csv'),'minimum_need':'NONE;bothpathcheckandactualsourceexplicitlyrecorded'}]
save('protocol/BLOCKER_REGISTER.json',blockers)
protocol='''# 输入与标签来源审计合同 / 2026-10-29

本轮是 R3_OPEN_VOCAB_INPUT_LABEL_SCOPE_AUDIT01。用户附件两部分首尾有截断与重复，结合聊天内续文执行；范围为已有本地来源、12个竞争定义、实际ID恢复的34条范围疑问及379条影响映射。输出仅在本轮新目录，不改历史文件。

## 检查顺序与证据合同

先核验上轮60个交付文件哈希，再读取冻结manifest、定义与案例结构，随后追溯本地matrix、STIX16.1、保存完整K2、1000UTF8字节前缀代码及原始作者标签。所有历史模块仅静态读取；没有import或执行其顶层代码，没有重新提取原始日志或重建候选知识库。

仅对21个相关ID独立计算纯字符串表达式：matrix中name+tactics按原顺序拼接，再按保存STIX对象顺序追加有效name+description，与保存完整文档比较，再计算1000UTF8字节前缀与保存冻结文本比较。这是有限输入输出证明，不保存替换知识、不运行历史提取流水线、不调用模型。

LEVEL_1为直接现有来源字段证明；LEVEL_2为代码与保存输入输出一致的有限转换证明；LEVEL_3为缺少链路的间接记录；LEVEL_4为未验证推测。局部转换可确认，不等于上游matrix发布版本已恢复或外部来源已重新认证。

## 统计合同

查询用sample_id去重，逻辑步骤用logical_step_id。范围队列从旧gold_audits.fresh_relatedness_level==SCOPE重建，并与CASE_DIAGNOSIS范围类ID集合相等核对；不是新语义预审。34条查询原作者父标签51项、旧目标Unseen分配46项、被标SCOPE分配34项分别记录。共存Gold全部保留独立行，不把51项叫51条查询。

候选来自封存SHUFFLED_COMPETITOR_PACKETS，逐ID/文本hash与COMPETING_TECHNIQUE_AUDIT及冻结定义相连。受影响Gold分配单位为(sample_id,先前targetUnseenGoldID)，配对单位为(sample_id,targetUnseenGoldID,缺陷竞争ID)，竞争实例单位为(sample_id,竞争ID)。515分配不是全部作者标签数；1700配对不是查询数，也不是错误数。报告各技术影响非互斥，汇总用真实键集合去重。

“视图不足”交集只使用此前主诊断INSUFFICIENT_VISIBLE_EVIDENCE的256个sample_id；不是本轮新判定，也不代表所有可能存在观察限制的查询。Gold范围与此主诊断互斥，因此三重交集0是分类合同结果，不能解释成范围查询没有观察限制。

## 证据与推断边界

不通过名称、战术或模型记忆补行为正文。原作者标签、当前可见行为、人工充分性与完整攻击意图分开；本轮既不裁定标签真伪，也不产生独立Gold。机械映射未发现错误仅限51个已检查原始ID运输链，不能证明语义映射正确。

T1574父候选文档有意汇聚父/子字段；冻结文本不是单独description字段。确认的是标题前缀占满预算、行为正文被裁剪，不是字段交换或错误ID。11个目标在当前STIX无对象，不能称为官方没有定义、提取代码跳过正文或精确发布版本冲突已查明。

独立裁定与模型因果效应均NOT_AVAILABLE。所有未知字段使用null/NOT_AVAILABLE并解释范围，禁止用零替代未检验。旧AI笔记只作历史审计线索，不在本轮重新解释日志。修复仅计划，下一轮需要新版本合同及另行授权。

## 资产与访问披露

初步定位时已读若干代码/元数据，之后开始逐文件首次受跟踪读取快照；不能声称全工作区有任务开始前快照。已核验的旧字节在结束复核，范围以ASSET_SOURCE_INVENTORY为准。未读取原始日志归档、受限PwnKit35—37日志或CONV-A01。

作者labels.json是包含metadata和cmd/attackmate等字段的混合容器；读取和解析过该容器，早期schema定位工具展示过一个非目标标签示例的附带命令字段。后续只保留指定34查询的metadata字段，不执行命令、不用命令补日志证据；不能声称实现了工具字节级字段隔离。没有读取原始llm_queries日志正文。此前模型排名曝光仍然存在，不能声称独立盲审。

资源合同：没有新增LLM/Agent/embedding/cross-encoder调用、训练、GPU、网络、服务器、下载、上传或历史资产修复。机械检查与科学资格分开；完成交付封存后停止。
'''
(R/'protocol/INPUT_LABEL_AUDIT_PROTOCOL.md').write_text(protocol)
limitations='''# 来源与推断边界

1. 本地STIX内部collection字段确认为16.1，不仅依赖文件名；与既有manifest SHA256一致。其官方真实性沿用本地历史来源，没有本轮网络重新认证。作者matrix有固定仓库commit，但exact ATT&CK release未编码，上游提取代码不在已恢复材料中。
2. 11种缺少行为文本的目标在当前STIX连父/子attack-pattern对象也不存在；可以确认当前组合来源覆盖不足，不能确认官方某版本没有定义，也不能捏造其引入日期。confirmed_source_version_mismatches=null保留精确版本问题；ID覆盖缺口11另列。
3. T1574确认为UTF8字节前缀截断。其1000字符包含父技术Hijack Execution Flow标题及子技术标题/战术，因此“全部是子技术变体标题”字面上不准确；可确认全部为名称与战术，无行为正文。
4. 34条旧AI范围疑问对应5种目标父ID。该父正文在本地源中存在，但不在当前1000字节冻结前缀。现有代码是有意父化汇聚，并未发现错误ID运输；父文本修复不等于作者标签正确。51项共存标签逐项保留，未给非目标共存标签新增语义判断。
5. 原作者标签、行为证据、独立人工充分性和完整意图真值不同。当前没有独立人审裁定，旧AI说明只作为队列线索。34条仍需裁定；未证明34个错误标签。
6. 379条输入中含缺陷竞争文本，证明当前比较输入受影响；全部379条历史模型错误的因果解释仍未知，不能报告0个真实因果错误或性能改善。
7. 515是该379查询的先前目标UnseenGold分配去重键，1700是只针对缺陷候选的Gold×候选配对；1171是缺陷候选实例；不包含全部216候选，也不等同全部作者正标签或错误实例。327多缺陷查询，交集通过ID恢复。
8. “当前视图不足”交集使用旧主诊断，不是新语义判定；三重交集0源自该主分类与范围分类互斥，不能推断范围问题没有观察不足。
9. 文件初始hash在首次跟踪读时建立，早期发现/schema读取先于部分快照；结束校验只证明登记范围内未变，不证明整个工作区任务前后无变化。已知旧报告差异保留。
10. 审计过程中解析混合作者标签容器，schema输出曾带出非目标标签的命令字段；未执行、未用来补行为或裁定Gold。没有工具字节级字段隔离，不新增原始日志读取。
11. 本轮只是静态来源审计。独立测试、正式语义参考、精确作者matrix来源版本和性能因果影响保持NOT_AVAILABLE。未恢复完整来源链，不能将文件交付完成升级成科研资格通过。
'''
(R/'protocol/SCOPE_AND_PROVENANCE_LIMITATIONS.md').write_text(limitations)
required=['INPUT_LABEL_SCOPE_AUDIT_REPORT.md','ASSET_SOURCE_INVENTORY.csv','TECHNIQUE_DEFINITION_AUDIT.csv','GOLD_SCOPE_AUDIT.csv','EXTRACTION_PIPELINE_AUDIT.csv','PARENT_CHILD_MAPPING_AUDIT.csv','AFFECTED_QUERY_MAP.csv','DEFINITION_IMPACT_SUMMARY.csv','REPAIRABILITY_REGISTER.csv','HUMAN_ADJUDICATION_QUEUE.csv','protocol/INPUT_LABEL_AUDIT_PROTOCOL.md','protocol/BLOCKER_REGISTER.json','protocol/SCOPE_AND_PROVENANCE_LIMITATIONS.md','RUN_MANIFEST.json','results/FINAL_VALIDATION.json']
# Read-only source report with evidence pointers and distinct unknowns.
report='''# 输入与标签范围来源审计报告

任务：R3_OPEN_VOCAB_INPUT_LABEL_SCOPE_AUDIT01；日期：2026-10-29（Asia/Shanghai）。

## A. 执行状态

**PARTIAL_WITH_REFERENCE_AND_DEFINITION_BLOCKERS**。完成12/12冻结竞争定义、本地可用来源与21个相关ID的有限转换核验、34/34范围疑问查询及其51个原始作者标签运输链、379/379受影响查询的ID重建。没有重做384条语义审查，没有修复知识、标签或新模型实验。

查明两个可直接核验的局部原因：T1574行为正文被1000UTF8字节前缀完全排除；其余11种在本地16.1描述源不存在匹配父/子对象，候选来自另一个作者matrix，故最终只保留名称和战术。精确作者matrix的ATT&CK发布版本与上游生成来源尚未恢复，11种兼容行为文本仍缺失；独立人审及语义Gold未建立。机械完整性通过不能解除这些科研阻断。

## B. 12个竞争技术定义的核验结果

来源是作者仓库matrix（commit42bbd2cf8409f64a1e6c8fc936c91725e8c558b2）与现有STIX bundle（collection明确x_mitre_version=16.1），不是仅凭文件名认定官方来源。matrix691个原始ID归并为216父候选，只含name/tactics，没有description。STIX已有22905个对象；目标对象按external_references.external_id实际检索，未以ID大小推断含义或年代。

|ID|完整冻结文本字符/字节|当前链内确认原因|证据|受影响查询|兼容正文可恢复性|
|---|---:|---|---|---:|---|
'''
for d in defs:
 im=next(x for x in impact if x['technique_id']==d['technique_id'])
 report+='|'+d['technique_id']+'|'+d['frozen_text_length']+'/'+d['frozen_text_bytes']+'|'+d['root_cause_status']+'|'+('L2' if d['technique_id']=='T1574' else 'L1当前源缺口')+'|'+im['affected_query_count']+'|'+('现有完整K2/STIX可用于新版本方案' if d['technique_id']=='T1574' else '需恢复兼容且有版本的源文本')+'|\n'
report+='''
逐项原文、hash、名称/战术、父/子ID、来源路径、脚本及修复资格见TECHNIQUE_DEFINITION_AUDIT.csv；原始字段对象与位置见audit/SELECTED_SOURCE_FIELD_EVIDENCE.json。12种当前均不具备所需行为比较资格。

### T1574的直接核验与措辞更正

冻结文本是1000字符、1000UTF8字节；它与保存完整K2的前1000字节完全相同，也恰好等于matrix为该父ID拼接的名称/战术前缀。完整K2为26335字节（26327字符），第一个描述正文从第1048字符开始，父技术自身正文从第19641字符开始（均零基字符偏移）。保存代码明确DOC_CAP=1000且clip=text.encode()[:cap].decode(utf8,errors=ignore)，有限纯表达式可复现同一输出。

**并非全部都是子技术标题**：其中还包括父技术Hijack Execution Flow标题；准确说法是“全部为父/子名称与战术，没有行为正文”。未发现标题字段与description字段交换的证据。原始STIX有14个有效父/子对象及各自描述，matrix有13个相关ID；父化拼接顺序及前缀预算造成完整行为排除。这里确认的是局部转换缺陷/合同后果，不能认定错误ID或序列化损坏。

### 其余11种的确认范围

对每个ID都实际检索了整个本地STIX中父/子对象，包括被撤销/废弃对象检查；均无对应ID。matrix的对应条目只有名称和战术；完整K2与短冻结文本相等，故这11种没有因1000字节规则进一步丢失已有正文。它们的当前链内原因是DESCRIPTION_NOT_IN_CURRENT_SOURCE，不能写成EXTRACTION_OMISSION或TEXT_TRUNCATION_CONFIRMED。

已确认作者候选集合与16.1描述源存在ID覆盖差异；matrix确切ATT&CK发布版本未编码，所以精确发布版本冲突数量仍NOT_AVAILABLE。不能声称官方定义不存在，也不能从名称补正文。为何没有提供兼容描述源、matrix如何产生仍未查明。

## C. 34条Gold范围疑问的核验结果

从CASE_EVIDENCE_AUDIT的SCOPE分配重建34个sample_id，与CASE_DIAGNOSIS的范围主类集合完全一致，涉及8个逻辑步骤。旧汇总要求的review/GOLD_TECHNIQUE_SUMMARY.csv并不存在；实际位于results/GOLD_TECHNIQUE_SUMMARY.csv，已登记两处路径和替代关系。

|被标范围疑问的目标父ID|查询数|来源链确认的输入事实|标签判断|
|---|---:|---|---|
|T1218|12|前缀行为段来自T1218.011；父正文偏移5960，在预算外|不能据此认定作者父标签错|
|T1569|5|前缀行为段来自T1569.001；父正文偏移1095，在预算外|服务行为与当前日志关系需独立裁定|
|T1485|5|前缀行为段来自T1485.001；父正文偏移1181，在预算外|删除调用不自动证明破坏性语义/结果|
|T1213|7|先展开T1213.002等；父正文偏移4157，在预算外|本地路径与信息仓库标签的范围需裁定|
|T1599|5|前缀行为段来自T1599.001；父正文偏移1877，在预算外|边界策略与具体子类型适用性需裁定|

34查询包含51项作者父标签，46项是此前目标UnseenGold，34项被旧AI标为SCOPE；三者不能互换。所有51项均找到作者metadata键、原始ID、保存raw_ground_truth、显式父化规则、冻结候选ID及对应文本，并逐项保留。查询有多个Gold时未合并为一项判断；未被标SCOPE的共存标签仅核查机械映射，不新增语义结论。

**在这51条已检查运输链中发现的机械ID映射错误为0**：作者metadata键与raw_reference相等，父ID与明确split('.')规则相等，候选ID存在。这个零有明确检查范围，不意味着Gold正确。34项SCOPE的父正文未进入冻结前缀已得到转换证据支持，但这是定义覆盖问题，不能直接叫作34个父子ID映射错误。作者标签真实适用范围、意图及当前视图证据充分性仍NOT_AVAILABLE，34条均进入独立人工队列。

GOLD_SCOPE_AUDIT.csv逐行列出原始标签、来源、支持/限制、机械映射与未裁定状态；PARENT_CHILD_MAPPING_AUDIT.csv给出完整ID链、STIX关系字段和来源指针；HUMAN_ADJUDICATION_QUEUE.csv仅列34项实际SCOPE目标，不伪造审查者或裁定。

## D. 提取与转换链审计

检查了以下实际链条，脚本只静态阅读，无旧模块导入或执行：

1. author labels.metadata → benchmark/run_benchmark.py标签选择 →保存原标签；evaluate_techniques.py验证ID并父化。
2. author mitre_matrix name+tactics → benchmark/run_benchmark.py按原顺序聚合到216父候选。
3. STIX16.1有效attack-pattern外部ID →同一脚本按父ID追加name+description，遵循STIX对象顺序，不优先父正文。
4. extended_knowledge_documents →P0冻结副本→baseline K2；保存JSON内容相等。
5. mechanism_ir/build_inputs.py对K2调用UTF8前缀1000字节，写KNOWLEDGE_TEXTS。
6. domain data/prepare_grouped_data.py只读复制K2及父化标签，原标签保存在P0_REFERENCE.raw_ground_truth。
7. 上轮prepare_competitors/prepare_first_pass复制冻结文本与ID，候选文本按domain K2作相等断言。

对12个竞争ID及34查询涉及的9种作者父ID，共21种相关ID核验保存输入输出。纯字符串拼接与UTF8切片的结果全部与保存文档一致，记录在audit/BOUNDED_TRANSFORMATION_PROOF.json。未重新生成/替换216候选知识，未执行大数据提取。

该证据能确认本地转换如何形成冻结文本；不能恢复matrix上游官方导出、版本历史或作者原标签意图。文档顺序导致首先看到某个子类型不代表该子类型应覆盖全部父类。没有证据证明代码读取错字段、ID覆盖、编码损坏或最终渲染额外丢失；这些“未发现”限于实际检查链。

## E. 379条受影响查询的影响范围

从封存候选ID逐一连接12个缺陷技术与当前定义，重建379/379条，未确认0条；去重后仍为379条，涉及79个逻辑步骤。

|统计单位与集合|数量|
|---|---:|
|去重受影响查询sample_id|379|
|缺陷竞争技术实例(sample_id,competitor)|1171|
|受影响旧目标UnseenGold分配(sample_id,gold)|515|
|缺陷竞争配对(sample_id,gold,competitor)|1700|
|受两个及以上定义缺陷影响的查询|327|
|与34条Gold范围疑问的交集|34|
|与256条旧“当前视图不足”主诊断的交集|251|
|上述三组的三重交集|0|

三重交集0来自旧主诊断的互斥分类，不说明范围疑问查询没有观察不足。受1/2/3/4/5/6个缺陷影响的查询分别为52/60/128/87/45/7，合计379。各技术影响非互斥，不能直接相加当查询数。515不是全部作者Gold分配；1700也不是5200全部配对，更不是错误数量。具体键集合及交集在audit/IMPACT_ID_SETS.json，逐查询连接在AFFECTED_QUERY_MAP.csv，各技术非互斥影响在DEFINITION_IMPACT_SUMMARY.csv。

379条均有直接“比较输入包含缺陷定义”的证据，所以影响资格为CONFIRMED_DIRECT_IMPACT_ON_COMPARISON_INPUT；379条实际模型错误原因仍未知。本轮没有性能因果实验，不能把任何数填成因缺陷造成的已确认排序错误数。

## F. 已确认的事实与未解决的问题

已确认：12份冻结比较文本无可用行为正文；T1574发生有代码与输入输出证明的正文排除；11种匹配行为对象不在当前STIX源；34条疑问目标父正文均不在冻结前缀；51项检查ID运输链符合当前父化规则；379查询及其影响键可以复现。

未解决：matrix原始生成来源和确切ATT&CK发布版本；11种兼容描述文本的恢复；父/子范围应该如何成为本任务的评价合同；作者父标签与当前日志证据的适用关系；独立人工参考与测试；任何历史性能错误的原因。

没有把语义不一致判成机械映射错，没有把缺失证据当反证，也没有通过读取额外日志或更改定义消除疑问。此前AI说明仍是历史线索，未升级为Gold。

## G. 可修复性与最小材料需求

T1574完整正文已在现有合法资产中，可制定新版本的父/子分段与信息预算方案；本轮只登记REPAIRABLE_FROM_EXISTING_FROZEN_ASSETS，不实施。五种范围疑问的父文本也存在，但标签适用性需要REQUIRES_HUMAN_ADJUDICATION，不能仅靠补文本裁定。

其余11种需要兼容版本的父/子原始描述、版本与hash回执、与作者候选matrix的对齐合同。现有材料没有给出这些缺失文件的真实路径，因此明确记录“兼容源文件未提供，路径NOT_AVAILABLE”，不编造路径。最小上游材料还包括作者matrix生成/导出规则与release信息、标签意图说明；独立参考需未曝光审查者、逐条件证据、分歧及仲裁记录。

未来如获准修复，必须创建独立新版本，保留旧知识和Gold，保存全候选新旧差异、父子映射差异、字段增删及输入hash，重核受影响案例并标明历史结果不可直接比较。不存在“技术可修复即已授权修改”的推断。

## H. 唯一科研决策

**GO_AFTER_SOURCE_RECOVERY**。

T1574局部转换原因已明确且现有源可用于修复计划；但其余11种缺少兼容行为来源，作者matrix的确切发布/生成链未恢复。全候选比较合同仍无法补齐，所以按来源链优先规则，主决策是先恢复最小来源。34条标签范围独立裁定和语义参考是后续仍不可跳过的阻断。该主决策不授权下载、修复旧知识、修改标签或重跑模型，也不是NO_GO问题已经永久不可研究。

## I. 统计与方法限制

本轮是对已曝光、按旧排序筛选的开发案例作来源和ID审计；不是新的独立样本。查询、逻辑步骤、Gold分配、候选实例和配对分开计数，不做准确率、显著性、置信区间或算法收益推断。未检查全部216候选的语义适用性，也未建立完整攻击意图真值。源文本恢复仅改变输入合同，不会自动证明GTE、C4、Seen/Unseen收益。

字段未知时保持null/NOT_AVAILABLE。confirmed_source_version_mismatches无法给精确发布差异数；另报11个当前源ID覆盖缺口。confirmed_mapping_errors=0仅限51个已实际检查的机械运输链；unresolved_mapping_cases=34表示范围适用性仍待人工裁定。unresolved_definition_causes=11只指上游兼容源缺失与版本由来的解释未恢复，不否定其在本地16.1不存在对象这一已确认直接原因。

## J. 资源、资产完整性和停止状态

新增模型、Agent、训练、GPU、网络、服务器、下载、上传及旧文件修改均为0；只运行本地标准库静态审计和去重程序。没有执行历史参数网格或改动标签、评价器及checkpoint。机械验证细节见results/FINAL_VALIDATION.json；历史资产结束hash核验范围以登记清单为准。

初步发现/schema读取先于部分资产首次跟踪快照，因此不声称全工作区有任务开始前快照。已保留旧generalization结果报告原有hash差异，不修复、不宣称所有历史manifest无差异。作者labels.json为混合容器，解析时存在非metadata字段读取和早期schema展示，已在协议披露；未执行命令或用它补日志事实，没有工具字节级隔离。没有读取原始llm_queries或受限日志正文。

最终机械状态为PASS_MECHANICAL_AUDIT_WITH_DOCUMENTED_BLOCKERS；科研执行状态仍为PARTIAL_WITH_REFERENCE_AND_DEFINITION_BLOCKERS。完成交付封存后停止，不自动启动下一轮。

## K. 交付导航

'''
for f in required:report+='- ['+f+']('+str(R/f)+')\n'
report+='\n附加证据：audit/BOUNDED_TRANSFORMATION_PROOF.json、audit/SELECTED_SOURCE_FIELD_EVIDENCE.json、audit/SELECTED_AUTHOR_LABEL_METADATA.json、audit/IMPACT_ID_SETS.json、audit/SOURCE_HASH_COMPARISONS.json、audit/DELIVERY_SHA256.json。全部位于本轮目录。\n'
(R/'INPUT_LABEL_SCOPE_AUDIT_REPORT.md').write_text(report)
# Compact execution ledger; exact new code hashes/output hashes sealed after validation.
resources={k:0 for k in ['new_model_calls','new_agent_calls','new_training_runs','GPU_tasks','server_access','network_access','downloads','uploads','old_files_modified']}
manifest={'task_id':'R3_OPEN_VOCAB_INPUT_LABEL_SCOPE_AUDIT01','client_report_date':'2026-10-29','timezone':'Asia/Shanghai','execution_status':'PARTIAL_WITH_REFERENCE_AND_DEFINITION_BLOCKERS','final_decision':'GO_AFTER_SOURCE_RECOVERY','required_artifact_paths':required,'counts':count,'resources':resources,'actual_execution':['read two attached user prompts andchatcontinuation','local rg metadata/code searches;no rawarchive contents','verified60previoussealedfilehashes','staticreadexistingknowledge/labels/mappingcode;historicalmodulesneverimported','parsedexistingSTIX16.1 andauthorlabelcontainer;selectedmetadata/sourcefields','bounded21documentpurestringreplayagainstsavedartifacts','rebuilt34scopequeue;checked51authorlabelIDchains;no semanticreadjudication','rebuilt379queryIDmappinganddeduplicated515assignments/1700pairs','wrote substantive auditfiles andreport;independentmechanicalvalidator follows'],'first_tracked_read_snapshot':str(STATE),'snapshot_scope_limit':'some preliminary discovery/schema reads preceded first tracked snapshots;no workspacewide task-start proof','mixed_label_container_access_disclosure':'labels.json parsed as mixedcontainer;earlyschema display includednon-target accompanyingcommandfields;not executed orusedasbehaviorproof','forbidden_raw_log_or_archive_reads':False,'historical_code_executed':False,'new_knowledge_corpus_or_candidate_generation':False,'bounded_pure_expression_checks_not_model_or_extraction_job':True,'experiment_executed':False,'semantic_reference_status':'NOT_AVAILABLE','independent_test_status':'NOT_AVAILABLE','causal_performance_impact':'NOT_AVAILABLE','legacy_hash_mismatches':legacy,'manifest_phase':'AWAITING_INDEPENDENT_MECHANICAL_VALIDATION','stop_after_delivery':True}
save('RUN_MANIFEST.json',manifest)
print(json.dumps({'report_created':True,'required_artifacts_before_validation':{f:(R/f).exists() for f in required},'pipeline_rows':len(pipeline),'repair_rows':len(repair),'source_hash_comparisons':len(checks),'source_hash_mismatch_rows':[x for x in checks if not x['match']]},ensure_ascii=False))
