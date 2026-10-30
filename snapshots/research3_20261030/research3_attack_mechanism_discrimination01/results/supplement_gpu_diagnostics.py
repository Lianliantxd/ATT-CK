"""Descriptive case/scene/fixed-candidate diagnostics. No new inference or human labels."""
import collections,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def read(n):return list(csv.DictReader((ROOT/n).open()))
def main():
 rows=read('results/NEURAL_PER_SAMPLE.csv');cases=json.loads((ROOT/'DIAGNOSTIC_30_FROZEN_IDS.json').read_text())['cases'];lookup={x['sample_id']:x for x in cases};selected=[]
 for r in rows:
  if r['sample_id'] in lookup:selected.append({**r,'old_stratum':lookup[r['sample_id']]['stratum'],'reference_qualification':'EXPOSED_DEVELOPMENT_DIAGNOSTIC','semantic_error_cause':'UNRESOLVED_HUMAN_PENDING'})
 assert len(selected)==480;csvout('diagnostic_30/NEURAL_CASE_ANALYSIS.csv',selected)
 ds=read('results/NEURAL_CANDIDATE_DIAGNOSTICS.csv');summary=[]
 for method in sorted({x['method'] for x in ds}):
  rr=[x for x in ds if x['method']==method];taxonomy=collections.Counter()
  for x in rr:
   if x['candidate_hit20']=='0':cat='CANDIDATE_NOT_RETRIEVED_FIXED_TOP20'
   elif x['transition_vs_fixed_pool_order']=='DEMOTED':cat='CANDIDATE_DEMOTED'
   elif x['transition_vs_fixed_pool_order']=='PROMOTED':cat='CANDIDATE_PROMOTED'
   elif x['final_top10_hit']=='1':cat='BOTH_HIT'
   else:cat='CANDIDATE_RETRIEVED_BUT_RANKED_LOW'
   taxonomy[cat]+=1
  if method.startswith('GTE_CE'):assert sum(taxonomy.values())==975;summary.append({'method':method,'N':975,**taxonomy})
 csvout('results/NEW_CE_FAILURE_TAXONOMY.csv',summary)
 allsc=read('results/NEURAL_SCENARIO_RESULTS.csv');sc={(x['method'],x['scenario']):x for x in allsc};scenes=sorted({x['scenario'] for x in allsc});out=[]
 for model in ['GTE_EMBEDDING','GTE_CE']:
  for k in ['K2_DESCRIPTION_16_1','MECHANISM_CARD']:
   for v,b in [('LITERAL','RAW'),('LITERAL_PLUS_RELATIONS','LITERAL'),('RAW_PLUS_LITERAL','RAW')]:
    for scene in scenes:
     a,z=sc[f'{model}__{v}__{k}',scene],sc[f'{model}__{b}__{k}',scene];out.append({'model':model,'knowledge':k,'view':v,'baseline':b,'scenario':scene,'N':a['N'],'top10_delta':float(a['top10'])-float(z['top10']),'mrr_delta':float(a['mrr'])-float(z['mrr']),'qualification':'DESCRIPTIVE_SHARED_SCRIPT_NOT_INDEPENDENT_REPLICATION'})
 csvout('results/NEURAL_SCENARIO_DELTAS.csv',out)
 native=read('frozen_inputs/INPUT_BUDGETS.csv');tokens=json.loads((ROOT/'results/gpu/ACTUAL_MODEL_INPUT_TOKENS.json').read_text());tl={(x['sample_id'],x['view']):x for x in tokens};matched=[]
 for x in native:
  if (x['sample_id'],x['view']) in tl:
   t=tl[x['sample_id'],x['view']];assert t['text_sha256']==x['text_sha256'];matched.append({**x,'actual_model_tokens':t['actual_token_counts']['embedding'],'embedding_tokens':t['actual_token_counts']['embedding'],'reranker_tokens':t['actual_token_counts']['reranker'],'current_status':'ACTUALLY_MEASURED_FIXED_TOKENIZERS'})
 assert len(matched)==3900;csvout('results/ACTUAL_GPU_INPUT_BUDGETS.csv',matched)
 ref=load(BASELINES/'datasets/p0_reference.jsonl');save('results/DATASET_QUALIFICATION.json',{'queries':975,'logical_steps':195,'scenarios':7,'simulation_identifiers':34,'multi_label_queries':sum(len(set(x['ground_truth']))>1 for x in ref),'multi_label_fraction':sum(len(set(x['ground_truth']))>1 for x in ref)/975,'split':'P0_EXPOSED_DEV'})
 print('480 frozen diagnostic cases,8CE taxonomies,84scene contrasts,3900actual budget matches')
if __name__=='__main__':main()
