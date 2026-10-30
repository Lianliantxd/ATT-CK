"""Actual CPU ranking; model-visible inputs contain no reference labels."""
import collections,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
ENGINE=module(BASELINES/'baselines/engine.py','frozen_mechanism_cpu_index')
MAIN=['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']
CONTROLS=['CLEAN_FIELDS','ROLE_LABELS_REMOVED','NO_RESULT','NO_ACTION_NORMALIZATION']
def main()->None:
 if (ROOT/'MECHANISM_BASELINE_PREDICTIONS.jsonl').exists():raise RuntimeError('No overwrite or hidden tuning rerun')
 inputs=load(ROOT/'frozen_inputs/PREDICTION_INPUTS.jsonl');knowledge=json.loads((ROOT/'attack_knowledge/KNOWLEDGE_TEXTS.json').read_text());cards={x['technique_id']:x for x in load(ROOT/'TECHNIQUE_MECHANISM_CARDS.jsonl')};literal={x['sample_id']:x['events'] for x in load(ROOT/'MECHANISM_LITERAL.jsonl')};runtime=[];started=time.monotonic()
 with (ROOT/'MECHANISM_BASELINE_PREDICTIONS.jsonl').open('w') as out:
  for model in ['char','bm25']:
   for kname,docs in knowledge.items():
    idx=ENGINE.Index(docs,model)
    for view in MAIN+(CONTROLS if kname=='K2_DESCRIPTION_16_1' else []):
     begin=time.monotonic();method=f'{model.upper()}__{view}__{kname}'
     for record in inputs:
      text=record['views'][view];sc=idx.score(text);order=sorted(range(216),key=lambda i:(-sc[i],idx.ids[i]));ranking=[idx.ids[i] for i in order]
      out.write(canonical({'sample_id':record['sample_id'],'method':method,'algorithm':model,'input_view':view,'knowledge':kname,'predictions':ranking[:10],'ranking_all216':ranking,'scores_top10':[sc[i] for i in order[:10]],'log_sha256':hashlib.sha256(text.encode()).hexdigest(),'knowledge_sha256':digest(docs),'candidate_count':216,'model_calls':0,'qualification':'ACTUAL_CPU_RETRIEVAL_BYTE_BUDGET_DEV'})+'\n')
     out.flush();runtime.append({'method':method,'N':975,'seconds':time.monotonic()-begin});print(method,'DONE',flush=True)
  # One generic field-overlap baseline. No per-technique rule or missing-evidence penalty.
  begin=time.monotonic()
  for record in inputs:
   events=literal[record['sample_id']];a={e['action']['concept'] for e in events if e['action']['concept']};o=set()
   for e in events:
    typ=e['object']['type']
    if typ=='FILE_PATH_ROLE_UNRESOLVED':o.add('file')
    if typ=='NETWORK_ENDPOINT_ROLE_UNCONFIRMED':o.update(['network','address'])
    if typ=='DOMAIN_NAME':o.add('domain')
   scores={}
   for tid,card in cards.items():
    ka={x['concept'] for x in card['mechanism_actions']};ko={x['concept'] for x in card['mechanism_objects']}
    scores[tid]=len(a&ka)/max(1,len(a|ka))+len(o&ko)/max(1,len(o|ko))
   ranking=sorted(scores,key=lambda t:(-scores[t],t))
   out.write(canonical({'sample_id':record['sample_id'],'method':'LiteralMechanismMatching','algorithm':'generic_action_object_Jaccard_equal_weight','input_view':'LITERAL','knowledge':'MECHANISM_CARD','predictions':ranking[:10],'ranking_all216':ranking,'scores_top10':[scores[t] for t in ranking[:10]],'observed_action_concepts':sorted(a),'observed_object_concepts':sorted(o),'candidate_count':216,'model_calls':0,'qualification':'DESCRIPTIVE_LITERAL_KNOWLEDGE_OVERLAP_NOT_OBSERVATION_SUPPORT_VERDICT'})+'\n')
  runtime.append({'method':'LiteralMechanismMatching','N':975,'seconds':time.monotonic()-begin})
 csvout('results/CPU_RUNTIME.csv',runtime);save('results/CPU_RUN_RECEIPT.json',{'conditions':len(runtime),'queries_each':975,'prediction_rows':len(runtime)*975,'new_model_calls':0,'runtime_seconds':time.monotonic()-started,'predictor_source_sha256':sha256(Path(__file__)),'frozen_index_source_sha256':sha256(BASELINES/'baselines/engine.py'),'input_sha256':sha256(ROOT/'frozen_inputs/PREDICTION_INPUTS.jsonl'),'knowledge_sha256':sha256(ROOT/'attack_knowledge/KNOWLEDGE_TEXTS.json'),'new_neural_forward':'MODEL_FORWARD_NOT_AUTHORIZED','no_gold_input':True})
if __name__=='__main__':main()
