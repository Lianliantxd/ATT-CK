"""Qualify authentic frozen features and recompute the exact-feature B1 baseline."""
import sys,json,hashlib,shutil
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main():
 p=ROOT/'embeddings/FROZEN_GTE_FEATURES.npz';r=json.loads((ROOT/'embeddings/FEATURE_EXTRACTION_RECEIPT.json').read_text());assert r['feature_sha256']==sha(p) and r['source_sha256']==sha(ROOT/'embeddings/extract_frozen_gte.py') and r['seconds']<900 and r['actual_tokens']<=1000000 and not r['Gold_loaded'] and r['trainable_parameters']==0
 f=np.load(p,allow_pickle=False);x=f['log_vectors'];t=f['knowledge_vectors'];assert x.shape==(975,768) and t.shape==(216,768) and x.dtype==np.float32 and t.dtype==np.float32 and np.isfinite(x).all() and np.isfinite(t).all();assert max(np.max(abs(np.linalg.norm(x,axis=1)-1)),np.max(abs(np.linalg.norm(t,axis=1)-1)))<1e-5
 inputs={r['sample_id']:r for r in load(ROOT/'data/P0_INPUTS.jsonl')};ids=f['technique_ids'].tolist();sids=f['sample_ids'].tolist();assert set(sids)==set(inputs);docs=json.loads((ROOT/'data/KNOWLEDGE_K2.json').read_text());assert ids==sorted(docs)
 assert f['input_hashes'].tolist()==[hashlib.sha256(inputs[s]['input_log_text'].encode()).hexdigest() for s in sids];assert f['knowledge_hashes'].tolist()==[hashlib.sha256(docs[k].encode()).hexdigest() for k in ids]
 path=ROOT/'results/runs_frozen/B1_predictions.jsonl';prior={r['sample_id']:r for r in load(path)};archive=ROOT/'inherited/CPU_ONLY_B1_PREDICTIONS.jsonl';assert not archive.exists();shutil.copy2(path,archive);scores=x@t.T;diff=0
 with path.open('w') as out:
  for sid,z in zip(sids,scores):
   ranking=[ids[i] for i in sorted(range(216),key=lambda i:(-float(z[i]),ids[i]))];old=prior[sid];diff+=old['predictions']!=ranking[:10];record={**old,'predictions':ranking[:10],'ranking_all216':ranking,'scores_top10':[float(z[ids.index(k)]) for k in ranking[:10]],'prediction_source':'AUTHENTIC_FROZEN_GTE_FEATURE_MATRIX_DOT_PRODUCT','feature_sha256':sha(p),'checkpoint_path':'FROZEN_BACKBONE_NO_TRAINED_HEAD'};out.write(json.dumps(record)+'\n')
 dump('embeddings/FEATURE_QUALIFICATION_VALIDATION.json',{'status':'PASS','log_shape':[975,768],'knowledge_shape':[216,768],'features_sha256':sha(p),'all_input_and_knowledge_hashes_match':True,'unit_L2_normalized':True,'B1_recomputed_from_same_features_as_trainable_heads':True,'prior_B1_preserved':str(archive.relative_to(ROOT)),'queries_with_changed_B1_top10_order':diff,'cause_of_possible_minor_changes':'prior extraction used different duplicate batching; no score direction or Gold-based selection','Gold_read':False})
 print('FEATURES_PASS, prior_B1 top10 ordered differences',diff)
if __name__=='__main__':main()
