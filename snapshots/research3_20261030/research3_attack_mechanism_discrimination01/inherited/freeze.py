"""Freeze and verify explicitly inherited assets; read existing sanitized inputs only."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main()->None:
 p=ROOT/'manifests/INHERITED_ASSETS.json'
 if p.exists():raise RuntimeError('Already frozen; use final verification without replacing hashes')
 expected={}
 for x in json.loads((PREVIOUS/'manifests/DELIVERY_SHA256.json').read_text()):expected[str(PREVIOUS/x['path'])]=x['sha256']
 expected[str(PREVIOUS/'manifests/DELIVERY_SHA256.json')]=sha256(PREVIOUS/'manifests/DELIVERY_SHA256.json')
 for x in json.loads((PREVIOUS/'manifests/INHERITED_ASSETS.json').read_text()):expected[x['source']]=x['sha256']
 paths=[BASELINES/'datasets'/n for n in ['p0_native.jsonl','p0_reference.jsonl','p1_resampled/prediction.jsonl','p1_resampled/reference.jsonl','p2_v2/prediction_sampled.jsonl','p2_v2/reference_sampled.jsonl','p2_v2/prediction_full.jsonl','p2_v2/reference_full.jsonl']]
 paths += list((BASELINES/'knowledge').glob('*.json'))+[BASELINES/'baselines/engine.py',BENCHMARK/'evaluate_techniques.py']
 dg=Path('/Users/tianxd/Documents/ChatGPT/4/dgpr_frontier_development_20261027/reports/RESEARCH_DECISION.md');paths.append(dg)
 for path in paths:expected.setdefault(str(path),sha256(path))
 assets=[]
 for name,h in expected.items():
  source=Path(name);assert sha256(source)==h,name
  assets.append({'source':name,'sha256':h,'bytes':source.stat().st_size,'access':'READ_ONLY_FROZEN_INHERITANCE'})
 save('manifests/INHERITED_ASSETS.json',assets)
 save('manifests/AUTHORIZATION_SCOPE.json',{'new_task':'R3_ATTACK_MECHANISM_DISCRIMINATION01','offline_local_work':True,'new_GPU_forward':False,'new_server_write':False,'new_data_upload':False,'new_model_download':False,'new_LLM_budget':0,'previous_task_grant':'NOT_EXTENDED','CONV-A01':'NOT_AUTHORIZED','PwnKit_scenario1_steps35_37_and_aliases':'EXCLUDED_NO_BODY_READ'})
 save('manifests/EXPERIMENT_REGISTRATION.json',{'name':'Attack Mechanism IR v1','namespace_note':'not NLP Abstract Meaning Representation','selection_before_new_mechanism_predictions':True,'input_views':['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL'],'cleaning_controls':['CLEAN_FIELDS','ROLE_LABELS_REMOVED','NO_RESULT','NO_ACTION_NORMALIZATION'],'knowledge':['K0_NAMES_ONLY','K2_DESCRIPTION_16_1','K3_WITHOUT_TITLES','MECHANISM_CARD','K2_PLUS_CARD'],'candidate_count':216,'CPU_methods':['char','bm25','LiteralMechanismMatching'],'no_hyperparameter_search':True,'same_native_pool':'previous V2 prefix fragments only; no P2 full pool expansion','budget':'main: shared UTF8 byte cap2000 for log views; knowledge cap1000 bytes; actual GTE tokens measured only if tokenizer/model access authorized; byte cap is NOT actual token count','selection_rule':'largest positive feasible common prefix fragment pool, deterministic; no Gold','MRR':'frozen V1 truncated at10','split':'P0_EXPOSED_DEV','neural_new_views_status':'MODEL_FORWARD_NOT_AUTHORIZED'})
 print(json.dumps({'verified_frozen_assets':len(assets),'new_GPU_calls':0}))
if __name__=='__main__':main()
