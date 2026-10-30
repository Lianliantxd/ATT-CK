"""One registered post-hoc confound diagnostic; never updates main/GPU input files."""
import collections,re,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
from mechanism_ir.build_inputs import VERBS,OBJECTS,clip
ENGINE=module(BASELINES/'baselines/engine.py','frozen_cpu_control_index')
VIEWS=['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']
def main()->None:
 marker=ROOT/'manifests/POSTHOC_KNOWLEDGE_CONTROLS.json';assert not marker.exists()
 save(str(marker.relative_to(ROOT)),{'classification':'POSTHOC_EXPOSED_DEV_CONFOUND_DIAGNOSTIC','reason':'main card may select facts beyond original visible description prefix; bag-of-word models cannot establish role/order reasoning','main_results_already_seen':True,'controls_fixed_before_control_predictions':True,'variants':['CARD_PREFIX_ONLY','CARD_WORD_ORDER_CONTROL'],'same_fixed_thirty_IDs':True,'main_input_and_GPU_upload_hashes_unchanged':True,'no_weight_or_parameter_search':True,'only_one_additional_control_round':True,'source_sha256':sha256(Path(__file__))})
 full=json.loads((BASELINES/'knowledge/K2_DESCRIPTION_16_1.json').read_text());names=json.loads((BASELINES/'knowledge/K0_NAMES_ONLY.json').read_text());main=json.loads((ROOT/'attack_knowledge/KNOWLEDGE_TEXTS.json').read_text());control={k:{} for k in ['CARD_PREFIX_ONLY','CARD_WORD_ORDER_CONTROL']}
 for tid,doc in full.items():
  visible=main['K2_DESCRIPTION_16_1'][tid];acts=[];objects=[];excerpts=[]
  for concept,pattern in VERBS.items():
   m=re.search(pattern,visible,re.I)
   if m:
    acts.append(concept)
    if len(excerpts)<4:excerpts.append(visible[max(0,m.start()-35):min(len(visible),m.end()+110)])
  for obj in OBJECTS:
   if re.search(r'\b'+obj+r's?\b',visible,re.I):objects.append(obj)
  control['CARD_PREFIX_ONLY'][tid]=clip(names[tid]+'\nKnowledge descriptive examples; requirements UNRESOLVED. actions='+','.join(acts)+' objects='+','.join(objects)+'\n'+' '.join(excerpts),1000)
  text=main['MECHANISM_CARD'][tid];words=ENGINE.words(text);shuffled=sorted(words,key=lambda w:digest('fixed_word_order_'+w));control['CARD_WORD_ORDER_CONTROL'][tid]=' '.join(shuffled)
  assert collections.Counter(ENGINE.words(control['CARD_WORD_ORDER_CONTROL'][tid]))==collections.Counter(words)
 save('attack_knowledge/POSTHOC_KNOWLEDGE_TEXTS.json',control)
 inputs=load(ROOT/'frozen_inputs/PREDICTION_INPUTS.jsonl');n=0;started=time.monotonic()
 with (ROOT/'experiments/KNOWLEDGE_CONTROL_PREDICTIONS.jsonl').open('w') as out:
  for model in ['char','bm25']:
   for k,docs in control.items():
    idx=ENGINE.Index(docs,model)
    for v in VIEWS:
     for row in inputs:
      sc=idx.score(row['views'][v]);order=sorted(range(216),key=lambda i:(-sc[i],idx.ids[i]));ranking=[idx.ids[i] for i in order]
      out.write(canonical({'sample_id':row['sample_id'],'method':f'{model.upper()}__{v}__{k}','algorithm':model,'input_view':v,'knowledge':k,'predictions':ranking[:10],'ranking_all216':ranking,'scores_top10':[sc[i] for i in order[:10]],'candidate_count':216,'qualification':'POSTHOC_CONFOUND_DIAGNOSTIC_NOT_NEW_MECHANISM','model_calls':0})+'\n');n+=1
     out.flush()
 save('results/KNOWLEDGE_CONTROL_RECEIPT.json',{'conditions':16,'rows':n,'seconds':time.monotonic()-started,'new_model_calls':0,'main_input_sha256':sha256(ROOT/'frozen_inputs/PREDICTION_INPUTS.jsonl'),'main_knowledge_sha256':sha256(ROOT/'attack_knowledge/KNOWLEDGE_TEXTS.json'),'same_word_multiset_in_word_order_control':True})
 print({'control_conditions':16,'rows':n})
if __name__=='__main__':main()
