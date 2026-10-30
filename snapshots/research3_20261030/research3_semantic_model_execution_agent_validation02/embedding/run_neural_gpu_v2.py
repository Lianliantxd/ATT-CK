"""Bounded engineering repair ONLY of empty input variants. No Gold is available."""
import copy,hashlib,json,time
from pathlib import Path
import run_neural_gpu as base
views=base.views
original_rebuild=views.rebuild_with_tokenizers
prior={};audit=[]
def variant(rows,n,rule,total):
 fs=views.select(rows,n,rule);texts=views.render(fs)
 mappings=[{**{k:v for k,v in f.items() if k!='text'},'literal_fields':views.fields(f)} for f in fs]
 chunkmap=[]
 for fi,f in enumerate(fs):
  spans=list(views.TOKEN.finditer(f['text']))
  for i in range(0,len(spans),256):
   a,b=spans[i].start(),spans[min(i+256,len(spans))-1].end()
   chunkmap.append({'fragment_index':fi,'source_id':f['source_id'],'line_id':f['line_id'],'char_start':f['char_start']+a,'char_end':f['char_start']+b,'chunk_hash':views.digest(f['text'][a:b])})
 return {'views':texts,'view_proxy_counts':{k:views.count(v) for k,v in texts.items()},'selected_native_proxy_tokens':n,'omitted_native_proxy_tokens':total-n,'truncated':n<total,'line_mappings':mappings,'V2_chunk_mappings':chunkmap,'source_groups':{s:[i for i,f in enumerate(fs) if f['source_type']==s] for s in sorted({f['source_type'] for f in fs})}}
def repaired(record,tokenizers,budget=2048):
 out=original_rebuild(record,tokenizers,budget);old=prior[record['sample_id']]
 rows=views.native_lines(record);total=sum(views.count(r['text']) for r in rows)
 for rule in ['prefix','window']:
  assert out['variants'][rule]['views']==old['variants'][rule]['views']
  if out['variants'][rule]['views']['V0']:continue
  if not total:raise ValueError('Genuinely empty source input, cannot fabricate observations')
  def fits(n):
   v=variant(rows,n,rule,total)
   counts={name:{k:len(tok.encode(text,add_special_tokens=False)) for k,text in v['views'].items()} for name,tok in tokenizers.items()}
   ok=max(v['view_proxy_counts'].values())<=budget and max(x for m in counts.values() for x in m.values())<=budget
   return ok,v,counts
  ok,v,counts=fits(1)
  if not ok:raise ValueError('Even one native token plus literal metadata cannot fit; explicit failure')
  lo,hi=1,min(total,budget)
  while lo<hi:
   mid=(lo+hi+1)//2
   if fits(mid)[0]:lo=mid
   else:hi=mid-1
  ok,v,counts=fits(lo);assert ok and v['views']['V0']
  out['variants'][rule]=v
  for name in tokenizers:out['actual_tokenizer_counts_by_model'][name][rule]=counts[name]
  audit.append({'sample_id':record['sample_id'],'rule':rule,'old_empty':True,'new_selected_native_proxy_tokens':lo,'view_sha256':{k:views.digest(t) for k,t in v['views'].items()},'actual_token_counts':counts,'Gold_used':False})
 out['input_engineering_protocol']='V2_EMPTY_VARIANTS_ONLY_NONEMPTY_UNCHANGED'
 return out
def main():
 r=base.R;marker=r/'manifests/EMPTY_INPUT_REPAIR_V2_STARTED.json'
 with marker.open('x') as f:json.dump({'time_unix':time.time(),'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'base_runner_sha256':hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest(),'reason':'empty input variants despite nonempty source; repair selection without Gold','only_empty_variants_change':True,'not_selected_by_metric':True,'one_bounded_full_rerun':True,'same_models_candidates_budgets_and_evaluator':True},f,indent=2)
 status=json.loads((r/'results/NEURAL_RUN_STATUS.json').read_text());assert status['status']=='BOTH_MODELS_FULL_P0_COMPLETE'
 assert not (r/'results_v1').exists()
 (r/'results').rename(r/'results_v1');(r/'results').mkdir()
 old_protocol=r/'manifests/NEURAL_RUNTIME_PROTOCOL.json';(r/'manifests/NEURAL_RUNTIME_PROTOCOL_V1.json').write_text(old_protocol.read_text())
 prior.update({x['sample_id']:x for x in base.load(r/'results_v1/NEURAL_INPUTS.jsonl')})
 views.rebuild_with_tokenizers=repaired
 old_prepare=base.prepare
 def prepare():
  result=old_prepare()
  assert len(audit)==17 and sum(x['rule']=='prefix' for x in audit)==10 and sum(x['rule']=='window' for x in audit)==7
  base.js(r/'results/EMPTY_INPUT_REPAIR_AUDIT.json',{'changed_variants':audit,'variant_count':1950,'unchanged_nonempty_variants':1933,'changed_empty_variants':17,'all_previously_nonempty_views_exactly_unchanged':True,'zero_remaining_empty_native_views':all(s['variants'][rule]['views']['V0'] for s in result[2] for rule in ['prefix','window']),'Gold_used':False})
  return result
 base.prepare=prepare;base.main()
if __name__=='__main__':main()
