"""Freeze metadata-only candidate pilot. Not an authorization or executed result."""
import csv,datetime,json,sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from project import ROOT,BASELINES,fingerprint,sha256
def main()->None:
 path=ROOT/'manifests/PAIRED_PILOT_REGISTRATION.json'
 if path.exists():raise SystemExit('Already registered; do not choose again')
 source=BASELINES/'P2_AUTHORIZED_STEP_MANIFEST.csv';rows=list(csv.DictReader(source.open()));groups=defaultdict(list)
 for i,r in enumerate(rows):
  if r['simulation_id'].split('_')[0]=='1' and int(r['step_id']) in (35,36,37):raise ValueError('Forbidden scope')
  key=fingerprint(['VALIDATION02_FIXED_METADATA_SELECTION',r['scenario_id'],r['simulation_id'],r['step_id']]);groups[r['scenario_id']].append((key,i,r))
 assert len(rows)==385 and len(groups)==7
 selected=[]
 for scene in sorted(groups,key=lambda x:fingerprint(['scene-order',x])):
  _,i,r=sorted(groups[scene])[0];selected.append({'episode_index':i,'sample_id':f'v2_sampled_{i:04d}','scenario_id':r['scenario_id'],'simulation_id':r['simulation_id'],'step_id':r['step_id']})
 for scene in sorted(groups,key=lambda x:fingerprint(['scene-order',x]))[:5]:
  _,i,r=sorted(groups[scene])[1];selected.append({'episode_index':i,'sample_id':f'v2_sampled_{i:04d}','scenario_id':r['scenario_id'],'simulation_id':r['simulation_id'],'step_id':r['step_id']})
 data={'protocol':'VALIDATION02_FUTURE_PAIRED_PILOT','registration_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registration_scope':'Metadata selected before any new method result; awaiting authorization; not an executed pilot','metadata_source':str(source),'metadata_source_sha256':sha256(source),'selected_episodes':selected,'selection':'SHA256 sort of authorized metadata, 1 per7scenes + second in5 fixed scene-order groups; no Gold or old outcomes used; known related dev, not independent test','minimal_gate_episode_index':0,'minimal_gate_note':'Already-exposed development step; native transport replay exists but no new model episode; excluded from quality claims about unseen cases','methods':['A0_DIRECT','A1_STATIC_BM25_LLM','A2_FIXED_QUERY_LLM','A3_ADAPTIVE_LLM_AGENT'],'candidate_count':216,'knowledge_version':'K2_DESCRIPTION_16_1','initial_regex_proxy_limit':256,'extra_log_caps':{'read_attempts':2,'new_unique_rows':20,'regex_proxy_tokens':2048},'actual_model_token_accounting':'Native API counts separately; regex proxy is not exact model tokens','current_authorized_new_model_call_limit':0,'proposed_new_model_call_limit':80,'proposed_elapsed_minutes':90,'proposed_API_prompt_token_cap':500000,'proposed_API_output_token_cap':45000,'minimal_gate_required_before_pilot':True,'prompt_and_runtime_version_freeze_required_before_calls':True,'formal_pilot_started':False}
 path.write_text(json.dumps(data,indent=2));print(json.dumps({'registered_cases':len(selected),'new_model_calls':0,'status':'AWAITING_AUTHORIZATION'}))
if __name__=='__main__':main()
