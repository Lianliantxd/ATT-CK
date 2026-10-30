"""Validate the actually saved group boundaries and model-input/reference isolation."""
import hashlib,json
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1]
def read(p):return [json.loads(x) for x in (ROOT/p).open() if x.strip()]
protocol=json.loads((ROOT/'GROUPED_TRAIN_VALIDATION_SPLITS.json').read_text())
manifest=json.loads((ROOT/'TRAINING_DATA_MANIFEST.json').read_text())
refs=read('data/P0_REFERENCE.jsonl');inp=read('data/P0_INPUTS.jsonl');allgold={r['sample_id']:r['gold_technique_ids'] for r in refs}
assert len(refs)==len(inp)==975 and len({r['logical_step_id'] for r in refs})==195
assert sum(len(r['gold_technique_ids'])>1 for r in refs)==285
assert len({a for r in refs for a in r['gold_technique_ids']})==79
assert all('gold_technique_ids' not in x for x in inp)
heldout=[];results=[]
audit=json.loads((ROOT/'data/manifests/SHARED_CONTENT_AUDIT.json').read_text())
shared=[set(x['logical_steps']) for x in audit['normalized_cross_scenario_groups']]
for f in protocol['folds']:
 train=read(f['paths']['train']);vi=read(f['paths']['validation_inputs']);hi=read(f['paths']['heldout_inputs']);vr=read(f['paths']['validation_reference']);hr=read(f['paths']['heldout_reference']);one=read(f['one_view_train_path'])
 sets=[{r['logical_step_id'] for r in a} for a in [train,vi,hi]]
 assert not(sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2])
 for group in shared:assert sum(bool(group&s) for s in sets)<=1
 for a in [train,vi,hi]:
  assert all(v==5 for v in Counter(x['logical_step_id'] for x in a).values())
  assert all(hashlib.sha256(x['input_log_text'].encode()).hexdigest()==x['input_hash'] for x in a)
 assert len(one)==len(sets[0]) and all(x['sampling_replica_id']==0 for x in one)
 assert all('gold_technique_ids' not in x for x in vi+hi)
 assert all(x['gold_technique_ids']==allgold[x['sample_id']] for x in train+vr+hr)
 assert set(x['sample_id'] for x in vi)==set(x['sample_id'] for x in vr)
 assert set(x['sample_id'] for x in hi)==set(x['sample_id'] for x in hr)
 assert all(x['scenario_id']==f['heldout_scenario'] for x in hi)
 heldout.extend(x['sample_id'] for x in hi);results.append({'fold_id':f['fold_id'],'train':len(train),'validation':len(vi),'heldout':len(hi),'status':'PASS'})
assert Counter(heldout)==Counter(x['sample_id'] for x in refs)
for x in manifest['source_files']+manifest['fold_file_manifest']:
 p=Path(x['path']);p=p if p.is_absolute() else ROOT/p
 assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256'],str(p)
receipt={'status':'PASS','query_count':975,'logical_steps':195,'parent_multilabel_queries':285,'all_outer_heldout_queries_evaluated_once':True,'gold_absent_from_input_files':True,'actual_fold_boundaries_disjoint':True,'shared_full_window_overlap_across_roles':False,'source_and_generated_manifest_hashes_verified':True,'folds':results,'script_independence':'UNKNOWN_EXACT_SCRIPT; this validation does not establish script identity'}
(ROOT/'data/manifests/GROUPED_DATA_VALIDATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps(receipt,indent=2))
