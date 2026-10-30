"""Check saved feature/input/knowledge IDs and hashes, without model computation."""
import json,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main():
 z=np.load(D/'embeddings/FROZEN_GTE_FEATURES.npz',allow_pickle=False);ids=z['sample_ids'].tolist();fhash=dict(zip(ids,z['input_hashes'].tolist()));tech=z['technique_ids'].tolist()
 assert len(ids)==len(set(ids))==975 and len(tech)==216
 assert not any(s.startswith(('1-35-','1-36-','1-37-')) or 'CONV-A01' in s for s in ids)
 inp={x['sample_id']:x for x in jl(D/'data/P0_INPUTS.jsonl')};assert set(inp)==set(ids)
 import hashlib
 for sid,x in inp.items():assert hashlib.sha256(x['input_log_text'].encode()).hexdigest()==x['input_hash']==fhash[sid]
 knowledge=json.loads((D/'data/KNOWLEDGE_K2.json').read_text());assert tech==sorted(knowledge)
 assert z['knowledge_hashes'].tolist()==[hashlib.sha256(knowledge[t].encode()).hexdigest() for t in tech]
 checked=0
 for p in sorted((P/'score_matrices').glob('*.json')):
  m=json.loads(p.read_text());f=m['fold_id'];source=D/'data/heldout'/f'{f}_inputs.jsonl'
  assert sha(source)==m['source_heldout_inputs_sha256']
  for x in jl(source):assert x['input_hash']==fhash[x['sample_id']] and x['input_view']==inp[x['sample_id']]['input_view'] and x['knowledge_version']==inp[x['sample_id']]['knowledge_version']
  checked+=1
 dump('results/SOURCE_INTERFACE_AUDIT.json',{'status':'PASS','feature_and_input_ids':975,'feature_and_input_hashes_equal':True,'candidate_description_hashes':216,'matrix_metadata_files_checked':checked,'same_prediction_input_view_across_methods':True,'ONE_MULTI_difference':'inherited head training augmentation only; same frozen query text','source_sha256':sha(Path(__file__)),'new_model_calls':0,'actual_per_query_truncation':'UNRESOLVED'})
 print('SOURCE_INTERFACE_AUDIT_PASS',975,216,checked)
if __name__=='__main__':main()
