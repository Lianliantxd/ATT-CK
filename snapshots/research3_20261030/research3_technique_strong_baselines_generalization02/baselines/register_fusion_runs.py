import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def register(directory,protocol,knowledge,view,reference):
 p=R/'experiments'/directory
 if not (p/'run.json').exists():return
 run=json.loads((p/'run.json').read_text())
 if protocol=='P0':inp=R/'datasets'/('p0_prediction.jsonl' if view=='sourcewise_same_native_content' else 'p0_'+view+'.jsonl')
 elif protocol=='P1':inp=R/'datasets/p1_resampled/prediction.jsonl'
 elif protocol=='P1_FIXED':inp=R/'datasets/p1_resampled/prediction_fixed_variant.jsonl'
 else:inp=R/'datasets/p2_v2/prediction_sampled.jsonl'
 assert hashlib.sha256(inp.read_bytes()).hexdigest()==run['input_sha256'],'Fusion input checksum changed'
 assert hashlib.sha256((R/'knowledge'/(knowledge+'.json')).read_bytes()).hexdigest()==run['knowledge_sha256'],'Fusion knowledge checksum changed'
 family='SourceWiseBM25' if run['representation']=='bm25' else 'SourceWiseTFIDF'
 for method in run['methods']:
  output=p/(method+'.jsonl')
  with output.open() as f:actual_n=sum(1 for line in f if line.strip())
  assert actual_n==run['n'],'Incomplete fusion output'
  process_receipt=R/'experiments'/(directory+'_process_receipt.json')
  exitcode=json.loads(process_receipt.read_text())['exit_code'] if process_receipt.exists() else None
  name=(family+'_'+method) if not method.startswith('EvidenceLineFusion') else (method+'_'+run['representation'])
  obj={'protocol':protocol,'input_view':view,'knowledge_view':knowledge,'representation':run['representation'],'method':name,'command':run.get('command','see fusion run.json'),'output':str(output),'exit_code':exitcode,'completion_verified':True,'actual_prediction_count':actual_n,'input_sha256':run['input_sha256'],'knowledge_sha256':run['knowledge_sha256'],'execution_success_basis':'completed run summary, exact output count, input/knowledge hash verified; original exitcode NOT_CAPTURED where null','seconds':run['seconds'],'InferenceTimeQualification':'shared batch time, not additive per-method runtime','reference_path':str(reference),'execution_status':'PROJECT_NEW_INFERENCE' if method.startswith('Evidence') else 'ADAPTED_BASELINE','source_directory':str(p)}
  (R/'experiments'/('registered_'+directory+'_'+method+'_receipt.json')).write_text(json.dumps(obj,indent=2))
if __name__=='__main__':
 for knowledge in ['K2','K3']:
  k='K2_DESCRIPTION_16_1' if knowledge=='K2' else 'K3_DESCRIPTION_16_1_WITHOUT_TITLES'
  modes=['bm25','word'] if knowledge=='K2' else ['bm25']
  for mode in modes:
   for suffix in ['','_candidate']:
    register(f'fusion_{knowledge}_{mode}'+suffix,'P0',k,'sourcewise_same_native_content',R/'datasets/p0_reference.jsonl')
 # Bounded generalization followups, not external tests.
 for protocol,ref,view in [('P1','datasets/p1_resampled/reference.jsonl','fresh_windows_v2'),('P1_FIXED','datasets/p1_resampled/reference_fixed_variant.jsonl','fixed_variant_fresh_windows_v2'),('P2','datasets/p2_v2/reference_sampled.jsonl','sampled10_per_source')]:
  for mode in ['bm25','word']:
   for suffix in ['','_candidate']:
    register(f'fusion_{protocol}_{mode}'+suffix,protocol,'K2_DESCRIPTION_16_1',view,R/ref)
 for view in ['records40','tokens2048','native']:
  for suffix in ['','_candidate']:
   register('fusion_P0_'+view+'_bm25'+suffix,'P0','K2_DESCRIPTION_16_1',view,R/'datasets/p0_reference.jsonl')
