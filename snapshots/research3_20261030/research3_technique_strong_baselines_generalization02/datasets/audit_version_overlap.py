"""Compare frozen v1 sampled observations to authorized cleaned v2 full logs.
This cannot establish a complete v1-v2 content diff without v1 full archive.
"""
import json,collections,re,hashlib,csv
from pathlib import Path
from build_v2 import clean_log
R=Path(__file__).resolve().parents[1];O=R.parent/'research3_attack_technique_benchmark01';H=lambda t:hashlib.sha256(t.encode()).hexdigest()
p0=[json.loads(l) for l in (O/'STEP_LEVEL_DATASET.jsonl').open()]
refs={x['sample_id']:x for x in map(json.loads,(R/'datasets/p2_v2/reference_full.jsonl').open())}
prov={x['source_id']:x for x in map(json.loads,(R/'datasets/manifests/SOURCE_PROVENANCE.jsonl').open())}
v1=collections.defaultdict(list)
for x in p0:v1[(x['simulation_id'],x['step_id'])].append(x)
rows=[];runc=[];sets=[];p0_runc=collections.Counter()
for v in map(json.loads,(R/'datasets/p2_v2/prediction_full.jsonl').open()):
 ref=refs[v['sample_id']];pair=(ref['simulation_id'],ref['step_id']);index={}
 for s in v['sources']:
  meta=prov[s['source_id']];index[(meta['host'],meta['relative_path'])]=set(l['text_hash'] for l in s['lines'])
  if ref['scenario_id']=='7':
   for l in s['lines']:
    if re.search('runc',l['text'],re.I) and re.search('init',l['text'],re.I):
     runc.append({'logical_step_id':ref['logical_step_id'],'simulation_id':ref['simulation_id'],'source_type':s['source_type'],'line_id':l['line_id'],'text_hash':l['text_hash']})
 v2set=set((host,path,h) for (host,path),hashes in index.items() for h in hashes)
 v1set=set()
 for x in v1[pair]:
  host=path=None;found=total=unknown_source=0
  for line in x['visible_log_content'].splitlines():
   if line.startswith('        '):
    total+=1;key=(host,path);clean=clean_log(line[8:]);v1set.add((host,path,H(clean)))
    if ref['scenario_id']=='7' and re.search('runc',clean,re.I) and re.search('init',clean,re.I):p0_runc[ref['logical_step_id']]+=1
    if key not in index:unknown_source+=1
    elif H(clean_log(line[8:])) in index[key]:found+=1
   elif line.startswith('    ') and line.endswith(':'):path=line[4:-1]
   elif line and not line.startswith(' ') and line.endswith(':'):host=line[:-1]
  rows.append({'p0_sample_id':x['sample_id'],'scenario_id':x['scenario_id'],'step_id':x['step_id'],'simulation_id':x['simulation_id'],'p0_sampled_lines':total,'matched_clean_lines_in_v2_same_source':found,'unknown_source_lines':unknown_source,'not_exactly_matched_lines':total-found})
 sets.append({'simulation_id':ref['simulation_id'],'logical_step_id':ref['logical_step_id'],'p0_observed_unique_host_source_line_hashes':len(v1set),'v2_full_unique_host_source_line_hashes':len(v2set),'intersection':len(v1set&v2set),'union':len(v1set|v2set),'p0_observed_only':len(v1set-v2set),'v2_full_unobserved_in_p0_samples':len(v2set-v1set),'jaccard_observed_vs_full':len(v1set&v2set)/max(1,len(v1set|v2set))})
with (R/'datasets/manifests/P0_V2_SAMPLED_LINE_OVERLAP.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
result={'qualification':'OBSERVED_LINE_OVERLAP_ONLY_NOT_COMPLETE_VERSION_DIFF','p0_queries':len(rows),'p0_sampled_lines':sum(r['p0_sampled_lines'] for r in rows),'matched_clean_lines_in_v2_same_source':sum(r['matched_clean_lines_in_v2_same_source'] for r in rows),'unknown_source_lines':sum(r['unknown_source_lines'] for r in rows),'queries_with_all_lines_matching':sum(r['p0_sampled_lines']==r['matched_clean_lines_in_v2_same_source'] for r in rows),'queries_with_some_nonmatching_line':sum(r['p0_sampled_lines']!=r['matched_clean_lines_in_v2_same_source'] for r in rows),'v2_scenario7_runc_and_init_lines':len(runc),'v2_scenario7_runc_init_logical_steps':sorted(set(x['logical_step_id'] for x in runc)),'warning':'A v1 sampled line not matched in v2 can reflect content change, normalization, source filtering, or matching limitations; v2 runc-init presence alone does not prove new-v2 addition without v1 full logs.'}
(R/'datasets/manifests/VERSION_OVERLAP_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
with (R/'datasets/manifests/V2_RUNC_INIT_LINE_INDEX.jsonl').open('w') as f:
 for x in runc:f.write(json.dumps(x)+'\n')
result['execution_step_hash_sets']=sets
result['scenario7_event_counts']={step:{'v2_full_runc_init_lines':sum(x['logical_step_id']==step for x in runc),'p0_sampled_runc_init_occurrences':p0_runc[step]} for step in ['7-3','7-6','7-8','7-10','7-13']}
result['set_comparison_warning']='Union compares sparse sampled v1 observations versus full v2; v2-only counts are not newly added-v2 events.'
(R/'datasets/manifests/VERSION_CONTENT_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='execution_step_hash_sets'},indent=2))
