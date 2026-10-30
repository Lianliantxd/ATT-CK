"""Independent source/field verification and delivery seal;no construction module imports."""
from pathlib import Path
import json,hashlib,gzip,csv,datetime
R=Path(__file__).resolve().parents[1];B=R.parent
H=lambda b:hashlib.sha256(b).hexdigest()
def j(p):return json.loads(Path(p).read_text())
def c(p):return list(csv.DictReader(Path(p).open()))
def save(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
checks=[]
def ck(n,v):checks.append({'check':n,'pass':bool(v)})
snapshot=j(R/'audit/INPUT_HASH_SNAPSHOT.json');changed=[]
for x in snapshot:
 p=Path(x['path']);ok=p.is_file() and H(p.read_bytes())==x['sha256'];ck('oldbytes:'+x['path'],ok)
 if not ok:changed.append(x['path'])
stix=json.loads(gzip.decompress((B/'provenance_baserepro_04/data/enterprise-attack-16.1.json.gz').read_bytes()));matrix=j(B/'research3_attack_technique_benchmark01/official_sources/mitre_matrix.json');old=j(B/'research3_domain_adaptive_contrastive_learning01/data/KNOWLEDGE_K2.json');oldfull=j(B/'research3_technique_strong_baselines_generalization02/knowledge/K2_DESCRIPTION_16_1.json');source={};byobject={};rels={}
for o in stix['objects']:
 if o.get('type')=='attack-pattern' and not o.get('revoked') and not o.get('x_mitre_deprecated'):
  for ref in o.get('external_references',[]):
   if ref.get('source_name')=='mitre-attack':source[ref['external_id']]=o;byobject[o['id']]=ref['external_id']
 if o.get('type')=='relationship' and o.get('relationship_type')=='subtechnique-of' and not o.get('revoked') and not o.get('x_mitre_deprecated'):rels[o['id']]=o
ids=sorted({t.split('.')[0] for t in matrix});knowledge=j(R/'knowledge/KNOWLEDGE_V1.json');records={x['candidate_id']:x for x in knowledge['records']};full=j(R/'knowledge/PARENT_ONLY_FULL.json');budget=j(R/'knowledge/PARENT_FIRST_1000B_DIAGNOSTIC.json');diff={x['candidate_id']:x for x in c(R/'KNOWLEDGE_DIFF.csv')};cover=c(R/'CANDIDATE_COVERAGE_AUDIT.csv');stats=j(R/'results/REPAIR_COUNTS.json');m=j(R/'RUN_MANIFEST.json')
ck('all216sameIDs',len(ids)==216 and set(ids)==set(records)==set(full)==set(budget)==set(diff)=={x['candidate_id'] for x in cover});ck('fixedsourcehash',knowledge['source_manifest']['source_STIX_sha256']==H((B/'provenance_baserepro_04/data/enterprise-attack-16.1.json.gz').read_bytes()))
missing=[];children=[]
for t in ids:
 rec=records[t];ob=source.get(t)
 ck('author_metadata_preserved:'+t,rec['author_matrix_metadata']['parent']==matrix.get(t))
 ck('olddiff_exact:'+t,diff[t]['old_text']==old[t] and diff[t]['old_sha256']==H(old[t].encode()) and old[t]==oldfull[t].encode()[:1000].decode('utf8',errors='ignore'))
 if ob and ob.get('description','').strip():
  text=ob['name']+'\n'+ob['description'];ck('sourceexactparent:'+t,rec['parent_description']==ob['description'] and rec['source_parent_name']==ob['name'] and full[t]==text and rec['parent_only_full_text']==text and rec['parent_description_sha256']==H(ob['description'].encode()) and rec['parent_source']['object_id']==ob['id']);ck('fulluntruncated:'+t,rec['full_text_truncated'] is False and diff[t]['new_full_parent_text']==text and diff[t]['new_sha256']==H(text.encode()))
  ck('budget_exact:'+t,budget[t]==text.encode()[:1000].decode('utf8',errors='ignore') and len(budget[t].encode())<=1000)
 else:
  missing.append(t);ck('missingnull_notfallback:'+t,full[t] is None and budget[t] is None and rec['parent_description'] is None and rec['parent_only_full_text'] is None and rec['qualification']=='BLOCKED_PARENT_BODY_SOURCE_NOT_AVAILABLE')
 expected_children={x for x in source if x.startswith(t+'.')};ck('separatechildren_complete:'+t,expected_children=={x['technique_id'] for x in rec['subtechniques']})
 for child in rec['subtechniques']:
  cid=child['technique_id'];co=source[cid];children.append(cid);ck('childliteral:'+cid,child['description']==co.get('description') and child['description_sha256']==H(co.get('description','').encode()))
  ck('childrelationship:'+cid,child['parent_relationship_ids'] and all(r in rels and rels[r]['source_ref']==co['id'] and rels[r]['target_ref']==ob['id'] for r in child['parent_relationship_ids']))
ck('13missingactual',missing==stats['missing_ids'] and len(missing)==13);ck('203available',len(ids)-len(missing)==203);ck('453childrenunique',len(children)==len(set(children))==453);ck('73oldparentstartsoutside',sum(x['old_parent_body_start_visible']=='False' for x in diff.values())==stats['old_parent_body_start_not_visible']==73);ck('164oldparentincomplete',sum(x['old_parent_body_fully_visible']=='False' for x in diff.values())==stats['old_parent_body_not_fully_visible']==164);ck('129budgettruncations',sum(full[t] is not None and len(full[t].encode())>1000 for t in ids)==stats['diagnostic1000B_texts_truncated']==129)
ck('T1574bodyrestored',full['T1574']=='Hijack Execution Flow\n'+source['T1574']['description'] and 'Adversaries' in full['T1574']);ck('twonamedifferences',sum(x['source_parent_name_differs_from_author_parent_name']=='True' for x in diff.values())==2)
for p in R.rglob('*'):
 if p.is_file():
  if p.suffix=='.json':j(p)
  elif p.suffix=='.csv':ck('nonempty_table:'+p.name,len(c(p))>0)
required=m['required_artifact_paths'];presence={x:(R/x).is_file() and (R/x).stat().st_size>0 for x in required if x!='results/FINAL_VALIDATION.json'};presence['results/FINAL_VALIDATION.json']=True
ck('required13',len(required)==13 and all(presence.values()));ck('no_model_experiment',m['experiment_executed'] is False and all(m[k]==0 for k in ['new_model_calls','new_agent_calls','new_training_runs','GPU_tasks','downloads','network_access','server_access','uploads','old_files_modified']));ck('no_causal_claim',stats['model_performance_change'] is None)
fail=[x for x in checks if not x['pass']];save('audit/VALIDATION_CHECKS.json',checks)
v={'status':'PASS_MECHANICAL_VALIDATION_WITH_SOURCE_BLOCKERS' if not fail else 'FAIL','execution_status':m['execution_status'],'assets_checked':len(snapshot),'old_files_modified':len(changed),'old_files_changed':changed,'candidate_count':216,'source_parent_bodies_available':203,'missing_source_techniques':missing,'new_full_parent_texts_truncated':0,'diagnostic1000B_texts_truncated':129,'parent_child_relationships_verified':453,'source_version_alignment':'NOT_AVAILABLE','independent_reference_status':'NOT_AVAILABLE','human_label_adjudication_executed':False,'old_gold_or_predictions_changed':False,'required_artifacts_present':presence,'mechanical_checks':len(checks),'failed_checks':fail,'new_model_calls':0,'new_agent_calls':0,'new_training_runs':0,'GPU_tasks':0,'network_access':0,'server_access':0,'downloads':0,'uploads':0,'experiment_executed':False,'model_performance_change':None,'final_decision':'GO_AFTER_SOURCE_RECOVERY','scientific_readiness':'NOT_READY_FOR_FULL216_MODEL_COMPARISON','limitations':['13compatibleparentbodiesmissing;IDsretainedwithnullbody.','AuthorcandidateexactATTCKreleaseunknown;2parentnamedifferencesnotsemanticallyadjudicated.','203sourcebodiesarenotindependentGold;34previouslabelscopequestionsunresolved.','1000bytebudgetstilltruncates129documents;diagnosticviewnotapprovedmodelinput.','Noqueryevaluation,modelmetricsorbenefitclaims.','PrecedingauditfileshashonlymayincludeGoldbytes;notclaimingOSbyteisolation.','Integrityonlycovers43registeredexistinginputs,notentireworkspace.']}
save('results/FINAL_VALIDATION.json',v);assert not fail,fail
m['manifest_phase']='SEALED_PARTIAL_KNOWLEDGE_VERSION';m['sealed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();m['actual_operations'].append('independent source/ID/string/relationship validation completed;no historical modules executed;deliveryhash readbacksealed');m['source_code_hashes']=[{'path':str(p.relative_to(R)),'sha256':H(p.read_bytes())} for p in sorted((R/'code').glob('*.py'))];m['output_hashes_excluding_self_and_delivery']=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':H(p.read_bytes())} for p in sorted(R.rglob('*')) if p.is_file() and p.name not in ['RUN_MANIFEST.json','DELIVERY_SHA256.json']];save('RUN_MANIFEST.json',m)
files=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':H(p.read_bytes())} for p in sorted(R.rglob('*')) if p.is_file() and p!=R/'audit/DELIVERY_SHA256.json'];save('audit/DELIVERY_SHA256.json',files)
assert {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}=={x['path'] for x in files}|{'audit/DELIVERY_SHA256.json'}
for x in files:assert H((R/x['path']).read_bytes())==x['sha256']
assert all((R/x).is_file() for x in required)
print(json.dumps({'status':v['status'],'execution_status':v['execution_status'],'mechanical_checks':len(checks),'failures':len(fail),'files_sealed':len(files),'old_assets_unchanged':len(snapshot),'old_files_modified':0,'final_decision':v['final_decision']},ensure_ascii=False))
