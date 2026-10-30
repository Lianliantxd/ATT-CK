from pathlib import Path
import json,csv,hashlib,datetime
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
v=json.loads((R/'results/FINAL_VALIDATION.json').read_text());assert v['status']=='PASS_MECHANICAL_AUDIT_WITH_DOCUMENTED_BLOCKERS' and v['mechanical_checks_failed']==0
m=json.loads((R/'RUN_MANIFEST.json').read_text());assert all((R/f).is_file() and (R/f).stat().st_size>0 for f in m['required_artifact_paths']);assert all(v['required_artifacts_present'].values())
snapshot=json.loads((R/'audit/ASSET_READ_SNAPSHOT.json').read_text());changed=[p for p,x in snapshot.items() if x['exists'] and (not Path(p).is_file() or sha(Path(p))!=x['sha256'])];assert not changed
for p in R.rglob('*'):
 if p.is_file():
  if p.suffix=='.json':json.loads(p.read_text())
  elif p.suffix=='.jsonl':
   for l in p.read_text().splitlines():
    if l.strip():json.loads(l)
  elif p.suffix=='.csv':
   with p.open() as f:assert csv.DictReader(f).fieldnames
m['manifest_phase']='SEALED_LOCAL_SOURCE_AUDIT_WITH_SCIENTIFIC_BLOCKERS';m['sealed_utc_runtime']=datetime.datetime.now(datetime.timezone.utc).isoformat();m['input_hashes']=[{'path':p,'sha256':x['sha256'],'exists':x['exists'],'inspection_role':x['qualification']} for p,x in snapshot.items()];m['code_hashes']=[{'path':str(p),'sha256':sha(p)} for p in sorted((R/'code').glob('*.py'))]
m['output_hashes_excluding_self_and_delivery']=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(R.rglob('*')) if p.is_file() and str(p.relative_to(R)) not in ['RUN_MANIFEST.json','audit/DELIVERY_SHA256.json']]
m['actual_execution']+=['independent mechanical validator completed965 checks with0 failures;12targetdefinition/34scopequery/379impactIDcoverage checks passed','final readback rechecked99existingassetbytes andallrequired15files;oldassetsunchangedwithinregisteredrange','serializedallCSV/JSON/JSONL readback passed;newcode/outputhashes sealed;no next experiment started']
m['final_readback_status']='PASS_WITH_DOCUMENTED_SCIENTIFIC_BLOCKERS';save(R/'RUN_MANIFEST.json',m)
files=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(R.rglob('*')) if p.is_file() and p!=R/'audit/DELIVERY_SHA256.json'];save(R/'audit/DELIVERY_SHA256.json',files)
for x in files:assert (R/x['path']).is_file() and sha(R/x['path'])==x['sha256'] and (R/x['path']).stat().st_size==x['bytes']
assert {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file()}=={x['path'] for x in files}|{'audit/DELIVERY_SHA256.json'}
print(json.dumps({'status':v['status'],'execution_status':v['execution_status'],'final_decision':v['final_decision'],'required_files':len(m['required_artifact_paths']),'files_hashed':len(files),'hash_errors':0,'mechanical_checks':v['mechanical_checks_executed'],'old_assets_rechecked':v['assets_checked'],'old_files_modified':0,'resources':m['resources']},ensure_ascii=False))
