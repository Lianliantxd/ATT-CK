"""Post-hoc engineering control: fit static tool metadata; no Gold-driven changes."""
import copy,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.path.insert(0,str(Path(__file__).resolve().parent))
from project import ROOT,sha256,canonical
import run_pilot as original
from agent_transport.transport import Transport
from llm.gguf_tokenizer import templated_ids
class StaticContextTransport(Transport):
 def execute(self,action:dict)->dict:
  action=copy.deepcopy(action)
  if action['tool']=='search_events':
   n=action['arguments'].get('max_results')
   if n==20:action['arguments']['max_results']=10
   elif n==10:action['arguments']['max_results']=5
  return super().execute(action)
def main()->None:
 prior=ROOT/'results/AGENT_RUN_STATUS.json'
 if not prior.exists():raise RuntimeError('Wait for original registered matrix to finish')
 register=ROOT/'manifests/STATIC_CONTEXT_FIT_V4.json'
 if register.exists():raise RuntimeError('Already registered; no hidden restart')
 roster=json.loads((ROOT/'manifests/PAIRED_PILOT_REGISTRATION.json').read_text())['selected_episodes']
 register.write_text(json.dumps({'protocol':'STATIC_CONTEXT_FIT_V4','reason':'V3 complete untrimmed event envelopes overflowed 8192 context before some static calls; engineering change only, no Gold/outcome inspection used to choose it','status':'POSTHOC_EXPOSED_DEVELOPMENT_NOT_CONFIRMATORY','source_sha256':sha256(Path(__file__)),'unchanged_shared_model_initial_knowledge_context_and_evidence_caps':True,'A1_max_results':10,'A2_each_max_results':5,'A3_V3_each_max_results':5,'maximum_possible_returned_rows_A1_A2_A3':10,'all12_cases_fixed_before_any_V4_result':roster,'rerun_scope':'ALL static cases, not selected failures; V3 output/failures retained; no Agent/A0 reruns','new_budget_reset':False},indent=2))
 original.Transport=StaticContextTransport
 for item in roster:
  for method in ['A1_STATIC_BM25_LLM','A2_FIXED_QUERY_LLM']:
   row=original.execute(item['episode_index'],method,'CONTEXT_FIT_STATIC_V4')
   if row['status']=='STOPPED_BUDGET_OR_RUNTIME':return
 print('STATIC_CONTEXT_FIT_FINISHED',flush=True)
if __name__=='__main__':main()
