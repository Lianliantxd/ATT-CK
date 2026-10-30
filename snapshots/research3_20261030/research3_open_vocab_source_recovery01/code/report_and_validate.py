from pathlib import Path
import json,csv,hashlib,gzip,datetime
R=Path(__file__).resolve().parents[1];B=R.parent
H=lambda x:hashlib.sha256(x).hexdigest()
def j(p):return json.loads(Path(p).read_text())
def c(p):return list(csv.DictReader(Path(p).open()))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
stats=j(R/'results/RECOVERY_COUNTS.json');m=j(R/'RUN_MANIFEST.json')
contract='''# 来源恢复及V2版本合同 / 2026-10-29

本轮遵循“继续恢复缺失来源”的指令，只检查已存在本地知识缓存和版本/获取记录，并创建独立新版本。未使用网络或下载，未读取查询、原始日志、Gold记录用于处理，未执行历史模型或脚本。

## 来源与候选合同

- 原始216候选ID不变，来自作者matrix。对应作者仓库commit固定，但其ATT&CK发布版本未知。
- 单一行为来源采用现有19.2 STIX整份固定字节，内部collection版本、历史SOURCE.md与SHA256.txt及多份相同拷贝相互核对。未重新网络认证，未取得该快照的上游gitcommit，不能仅靠URL证明新下载真实性。
- 对216原ID逐字保留同ID对象的name、description、revoked/deprecated及对象元数据，不把16.1和19.2正文拼接。所有父文本无截断；不声称新旧定义语义等价。
- 其中213父对象有效，3个已撤销。对撤销ID保留原候选及源存档正文，明确待裁定；不应用revoked-by替换，不改标签、预测、评价器或候选数。
- 480个按原ID前缀定位的子对象单独存档，其中464有明确subtechnique-of关系，16个已撤销子对象没有该关系。16项仅为词法ID归属的历史记录，不认证父子语义，不用于生成必要条件。不能把480项都叫经确认的有效子技术。
- source_tactics与author_tactics分列；47项战术集合有差异，不能把新旧战术字段混成同一版标签。

## V2用途及禁止推断

V2是完整来源字段版本，但完整语义评价合同尚未就绪。恢复216正文不等于216类已获独立语义资格。T1562/T1656/T1672的撤销及替代关系、T1211名称/范围变化需作明确合同选择；旧34查询范围疑问仍需独立人审。正式输入预算、独立测试也未在本轮建立。

如果保留旧216标签，应明确采用“固定历史候选ID+19.2同ID存档正文”作为新评价合同，并评估撤销ID/父子粒度影响；不能称为当前19.2有效技术全集。如果迁移到新ID，必须另建新标签/候选版本、逐项映射与独立裁定，禁止覆盖原标签。当前只记录两种路线，不实施标签迁移。

主决策GO_AFTER_LABEL_SCOPE_ADJUDICATION：缺失正文已找到，当前优先阻断是新来源与历史标签/撤销ID的适用范围。作者矩阵确切发布版本仍未恢复；这阻止“原版同源”声明，但不否定已恢复的逐ID正文存在。任何模型实验仍需合同和独立参考通过后单独授权。

## 统计和完整性

216/13为父候选或父定义数，非查询数；本轮不更新379条受影响查询统计，不推断模型性能原因。32项登记输入首次跟踪hash后结束复核；若前期发现读取先于快照则披露，不声称任务开始时全工作区已快照。前一版封存文件部分含历史审计信息，读字节用于hash，不声称OS字节级未接触标签。新文件只写本轮目录，旧资产保持原样。
'''
(R/'protocol/SOURCE_RECOVERY_CONTRACT.md').write_text(contract)
required=['SOURCE_RECOVERY_REPORT.md','knowledge/KNOWLEDGE_V2_SOURCE19_2.json','knowledge/PARENT_ONLY_FULL_V2.json','SOURCE_VERSION_MIGRATION.csv','RECOVERED_13_DEFINITIONS.csv','REVOCATION_CROSSWALK_NOT_APPLIED.csv','CONTRACT_REVIEW_QUEUE.csv','PARENT_CHILD_SOURCE_AUDIT.csv','audit/SOURCE_PROVENANCE_RECEIPT.json','protocol/SOURCE_RECOVERY_CONTRACT.md','RUN_MANIFEST.json','results/FINAL_VALIDATION.json']
report='''# ATT&CK来源恢复报告

2026-10-29（Asia/Shanghai）。执行状态：**SOURCE_RECOVERY_COMPLETED_WITH_VERSION_AND_SCOPE_BLOCKERS**。

## 已完成与更正

从已有本地rp3_phase1_local_cache找到Enterprise ATT&CK19.2完整STIX快照，13种原先在16.1不存在的候选正文全部找到，无需网络或下载。本轮创建单一19.2来源的独立V2版本，保留原216候选ID且不截断父正文。

上一轮“13种缺少来源”只对当时检查的16.1文件成立；上一轮没有检查到本地19.2缓存，不能推广成整个工作区无来源。本轮更新这一阻断，并保留旧版及旧报告不变。

## 来源如何核实

缓存JSON的SHA256为dc1639caa5501d720e280cf1cbd8fbe009884a0c9b3e6e9ed9d0c25166c3d8f4。内部collection.x_mitre_version为19.2。原有2026-09-02本地SOURCE.md记录MITRE attack-stix-data官方仓库URL及同一hash，SHA256.txt也一致。压缩副本解压后字节完全相同，三个备份副本也相同。

这是现有来源记录+内部版本+字节一致性证明，不是本轮重新下载认证；官方上游精确gitcommit未恢复。作者matrix虽有仓库commit，但其ATT&CK发布版本仍未知，不声称19.2就是作者原始版本。

## 结果和跨版本差异

|项目|数量|含义|
|---|---:|---|
|保留原父候选ID|216|候选集未删减或替换|
|有同ID完整源正文|216|其中3个是已撤销对象|
|补齐上一版缺失正文|13|含T1672撤销对象的存档正文|
|有效源父对象|213|不是216项都有效|
|已撤销候选|3|T1562、T1656、T1672|
|与作者父名称不同|1|T1211，涉及范围/名称核验|
|与作者战术集合不同|47|源战术与原标签字段分列|
|原203项中正文发生变化|59|不是仅补13条，其它定义也变了|
|原203项中正文相同|144|按完整字符串比较|
|单独存储的子对象|480|包含撤销记录|
|有明确原父subtechnique-of关系的子对象|464|16项没有关系，未认证父子语义|
|父全文被截断|0|不等于Token预算已冻结|

RECOVERED_13_DEFINITIONS.csv逐项保存完整正文、字符/字节、对象ID、源位置、修改时间及状态。SOURCE_VERSION_MIGRATION.csv覆盖全部216项，保存16.1/19.2字段hash、命名、战术、状态及替代关系差异。没有读取日志去选择有利定义。

## 必须单独处理的撤销关系

|原候选|19.2明确revoked-by目标|本轮处理|
|---|---|---|
|T1562|T1685|保留旧ID及存档正文，不应用替换|
|T1656|T1684.001|保留旧ID，父级候选转子技术的粒度问题待裁定|
|T1672|T1684.002|保留旧ID，父级候选转子技术的粒度问题待裁定|

这些是源中实际关系，不是本轮AI推测。但是“被替代”不授权把原Gold自动改成新ID，更不证明旧标签错了。

T1211在作者matrix名为Exploitation for Defense Evasion，19.2名为Exploitation for Stealth。此前16.1相对作者的T1176/T1219名称差异，在19.2已同名；这仍不证明全部语义适用范围相同。4项具体合同问题列入CONTRACT_REVIEW_QUEUE；47项战术变化单独保留全量差异。16个无原父关系的子对象均已撤销，作为档案记录而非已核验的有效父子关系。

## 新知识版本具体是什么

KNOWLEDGE_V2_SOURCE19_2.json中216项都保存19.2同ID的完整源字段，并把作者元数据、源元数据、状态、子类型和替代关系分开。PARENT_ONLY_FULL_V2.json是源父名称+换行+完整description，不加名称/战术前缀，不混入子类型正文，也不裁剪。撤销3项明确标记待合同复核；未把它们伪装成当前有效技术。

上一版16.1知识和所有历史文件未改。这里不是给16.1补13条19.2后假装同版，而是新建单一19.2来源版本，因此59项既有正文改变已明确记录。没有新预测、标签纠错或模型收益。

## 当前科研决策

**GO_AFTER_LABEL_SCOPE_ADJUDICATION**。

“缺失行为正文”这个局部阻断已经解除，下一步优先确定旧216标签如何与19.2存档/有效定义比较，处理3个撤销ID和T1211范围问题，并继续对既有34条范围疑问建立独立人审。尚未具备GO_METHOD_EXPERIMENT资格，不能直接运行模型或称完整输入合同已通过。

保留旧候选与存档正文、或迁移到新有效ID是两种不同评价任务。当前只保存可审查材料，不自动选择会改变标签含义的迁移，不实施新Gold。作者矩阵确切版本未恢复仍是局限；若要求与原版严格同版，就仍需其生成/导出记录。

## 资源、完整性与停止

新增模型/Agent调用、训练、GPU、下载、网络、服务器、上传以及旧文件修改均为0。仅本地知识与已有回执静态处理。完整性范围为本轮登记输入，部分发现读取先于首次跟踪快照，不声称全工作区任务开始前快照。所有新产物只在本轮新目录。

机械验证与科学资格分开记录，最终结果见FINAL_VALIDATION。完成封存后停止，不自动开展标签迁移、模型实验或联系外部审查者。

## 交付导航

'''
for n in required:report+='- ['+n+']('+str(R/n)+')\n'
(R/'SOURCE_RECOVERY_REPORT.md').write_text(report)
m['required_artifact_paths']=required;save('RUN_MANIFEST.json',m)
# Independent verification reconstructs fromsourcefiles;never imports constructionmodule.
snapshot=j(R/'audit/INPUT_HASH_SNAPSHOT.json');checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)})
changed=[]
for x in snapshot:
 path=Path(x['path']);ok=path.is_file() and H(path.read_bytes())==x['sha256'];ck('old_asset:'+str(path),ok)
 if not ok:changed.append(str(path))
sourcepath=B/'rp3_phase1_local_cache/enterprise-attack.json';bundle=j(sourcepath);patterns={};byobject={};rels={}
for o in bundle['objects']:
 if o.get('type')=='attack-pattern':
  for e in o.get('external_references',[]):
   if e.get('source_name')=='mitre-attack':patterns[e['external_id']]=o;byobject[o['id']]=e['external_id']
 if o.get('type')=='relationship':rels[o['id']]=o
matrix=j(B/'research3_attack_technique_benchmark01/official_sources/mitre_matrix.json');ids={t.split('.')[0] for t in matrix};k=j(R/'knowledge/KNOWLEDGE_V2_SOURCE19_2.json');full=j(R/'knowledge/PARENT_ONLY_FULL_V2.json');records={x['candidate_id']:x for x in k['records']};migration={x['candidate_id']:x for x in c(R/'SOURCE_VERSION_MIGRATION.csv')};previous={x['candidate_id']:x for x in j(B/'research3_open_vocab_knowledge_repair01/knowledge/KNOWLEDGE_V1.json')['records']}
ck('216IDsets',len(ids)==216 and ids==set(records)==set(full)==set(migration));sourcehash=H(sourcepath.read_bytes());ck('sourcehash',k['source_file_sha256']==sourcehash)
for t,r in records.items():
 o=patterns[t];ck('source_exact:'+t,r['source_description']==o['description'] and r['source_name']==o['name'] and r['source_description_sha256']==H(o['description'].encode()) and r['source_object_id']==o['id']);ck('full_untruncated:'+t,full[t]==o['name']+'\n'+o['description'] and not r['truncated']);ck('status_exact:'+t,r['source_revoked']==o.get('revoked',False) and r['source_deprecated']==o.get('x_mitre_deprecated',False));ck('legacy_ID_unchanged:'+t,r['replacement_applied'] is False and r['author_name']==matrix[t]['name']);ck('migration_exact:'+t,migration[t]['STIX19_2_description_sha256']==H(o['description'].encode()) and migration[t]['candidate_ID_changed']=='False' and migration[t]['Gold_changed']=='False')
 for child in r['subtypes_separate']:
  co=patterns[child['technique_id']];ck('childexact:'+child['technique_id'],child['description']==co.get('description','') and child['revoked']==co.get('revoked',False));targets=[byobject.get(z.get('target_ref')) for z in bundle['objects'] if z.get('type')=='relationship' and z.get('relationship_type')=='subtechnique-of' and z.get('source_ref')==co['id']];ck('child_relation_truth:'+child['technique_id'],child['source_parent_ids_from_relationships']==targets and child['same_legacy_parent_relationship_present']==(t in targets))
recovery=c(R/'RECOVERED_13_DEFINITIONS.csv');expected_missing={t for t,r in previous.items() if r['parent_description'] is None};ck('13recoveryexact',len(recovery)==13 and {x['candidate_id'] for x in recovery}==expected_missing and all(x['source_description']==patterns[x['candidate_id']]['description'] for x in recovery))
cross=c(R/'REVOCATION_CROSSWALK_NOT_APPLIED.csv');expected={'T1562':'T1685','T1656':'T1684.001','T1672':'T1684.002'};ck('3revocationlinks',len(cross)==3 and {x['original_candidate_id']:x['target_id'] for x in cross}==expected)
for row in cross:ck('explicit_revocation:'+row['original_candidate_id'],row['relationship_id'] in rels and rels[row['relationship_id']]['relationship_type']=='revoked-by' and byobject[rels[row['relationship_id']]['target_ref']]==row['target_id'] and row['mapping_applied']=='False')
ck('213active3revoked',sum(not r['source_revoked'] and not r['source_deprecated'] for r in records.values())==213);ck('47tacticdifferences',sum(x['tactics_equal_as_set']=='False' for x in migration.values())==47);ck('59changed144same',sum(x['description_changed_between_sources']=='True' for x in migration.values())==59 and sum(x['description_changed_between_sources']=='False' for x in migration.values())==144);ck('4contractissues',len(c(R/'CONTRACT_REVIEW_QUEUE.csv'))==4)
childtable=c(R/'PARENT_CHILD_SOURCE_AUDIT.csv');ck('480subtypes464relations16archived',len(childtable)==480 and sum(x['same_legacy_parent_relation']=='True' for x in childtable)==464 and all(x['revoked']=='True' for x in childtable if x['same_legacy_parent_relation']=='False'))
for p in R.rglob('*'):
 if p.is_file():
  if p.suffix=='.json':j(p)
  elif p.suffix=='.csv':ck('nonempty:'+p.name,len(c(p))>0)
presence={n:(R/n).is_file() and (R/n).stat().st_size>0 for n in required if n!='results/FINAL_VALIDATION.json'};presence['results/FINAL_VALIDATION.json']=True;ck('requiredfiles',all(presence.values()));ck('noadditionalresources',all(v==0 for v in m['resources'].values()) and not m['experiment_executed']);ck('unknownnotzero',stats['author_matrix_exact_release'] is None and stats['model_performance_change'] is None)
failed=[x for x in checks if not x['pass']];save('audit/VALIDATION_CHECKS.json',checks)
validation={'status':'PASS_MECHANICAL_SOURCE_RECOVERY_WITH_SCOPE_BLOCKERS' if not failed else 'FAIL','execution_status':m['execution_status'],'source_bodies_recovered':216,'previous_missing_recovered':13,'missing_body_sources':[],'active_source_candidate_count':213,'revoked_source_candidate_IDs':stats['revoked_source_candidate_IDs'],'revocation_mappings_applied':0,'author_matrix_exact_release':None,'author_source_name_mismatches':['T1211'],'author_source_tactic_mismatch_count':47,'semantic_contract_status':'NOT_QUALIFIED;3revokedIDs+scopequestionsrequireadjudication','reference_status':'NOT_AVAILABLE','independent_test_status':'NOT_AVAILABLE','assets_checked':len(snapshot),'old_files_modified':len(changed),'old_files_changed':changed,'mechanical_checks':len(checks),'failed_checks':failed,'required_artifacts_present':presence,'new_model_calls':0,'new_agent_calls':0,'new_training_runs':0,'GPU_tasks':0,'downloads':0,'network_access':0,'server_access':0,'uploads':0,'experiment_executed':False,'model_performance_change':None,'final_decision':m['final_decision'],'limitations':m['limitations']+['480subtypearchiveincludes16revokedobjectswithoutcurrentparentrelation;notallarequalifiedsubtypes.','LocalhistoricalsourceURLandhashreceipt corroborated;upstreamgitcommitnotrecovered,no new externalreauthentication.']}
save('results/FINAL_VALIDATION.json',validation);assert not failed,failed
m['sealed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();m['manifest_phase']='SEALED_SOURCE_RECOVERED_CONTRACT_PENDING';m['actual_operations'].append('independentlyverified literalbodies,statuses,crosswalks,versiondifferencesandregisteredoldhashes;sealedoutputs');m['code_hashes']=[{'path':str(p.relative_to(R)),'sha256':H(p.read_bytes())} for p in sorted((R/'code').glob('*.py'))];m['output_hashes_excluding_self_and_delivery']=[{'path':str(p.relative_to(R)),'sha256':H(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(R.rglob('*')) if p.is_file() and p.name not in ['RUN_MANIFEST.json','DELIVERY_SHA256.json']];save('RUN_MANIFEST.json',m)
files=[{'path':str(p.relative_to(R)),'sha256':H(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(R.rglob('*')) if p.is_file() and p!=R/'audit/DELIVERY_SHA256.json'];save('audit/DELIVERY_SHA256.json',files)
for x in files:assert H((R/x['path']).read_bytes())==x['sha256']
assert {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}=={x['path'] for x in files}|{'audit/DELIVERY_SHA256.json'}
print(json.dumps({'status':validation['status'],'checks':len(checks),'failed':len(failed),'assets_checked':len(snapshot),'old_files_modified':len(changed),'files_sealed':len(files),'final_decision':m['final_decision']},ensure_ascii=False))
