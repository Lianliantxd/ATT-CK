import concurrent.futures,json,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]

def execute(job):
 prot,inp,mode,view=job
 k='K2_DESCRIPTION_16_1';results=[]
 for candidate in [False,True]:
  env='EvidenceLineFusion' if candidate else ('SourceWiseBM25' if mode=='bm25' else 'SourceWiseTFIDF')
  directory=f'fusion_{prot}_{mode}' if prot!='P0' else f'fusion_P0_{view}_{mode}'
  if candidate:directory+='_candidate'
  cmd=[str(R/'venvs'/env/'bin/python'),'-B',str(R/'baselines/source_fusion.py'),'--inputs',str(inp),'--knowledge',str(R/'knowledge'/(k+'.json')),'--representation',mode,'--output',str(R/'experiments'/directory),'--skip-evidence','--only-candidate' if candidate else '--only-fixed-fusions']
  start=time.perf_counter();run=subprocess.run(cmd,capture_output=True,text=True);receipt={'command':cmd,'exit_code':run.returncode,'seconds':time.perf_counter()-start,'stdout':run.stdout,'stderr':run.stderr}
  (R/'experiments'/(directory+'_process_receipt.json')).write_text(json.dumps(receipt,indent=2));results.append((directory,run.returncode,round(receipt['seconds'],2)))
  if run.returncode:raise RuntimeError(run.stderr)
 return results
if __name__=='__main__':
 assert (R/'datasets/manifests/STABLE_CLEANED.json').exists()
 jobs=[]
 for prot,inp in [('P1','datasets/p1_resampled/prediction.jsonl'),('P1_FIXED','datasets/p1_resampled/prediction_fixed_variant.jsonl'),('P2','datasets/p2_v2/prediction_sampled.jsonl')]:
  for mode in ['bm25','word']:jobs.append((prot,R/inp,mode,'sampled'))
 for view in ['native','records40','tokens2048']:
  jobs.append(('P0',R/'datasets'/('p0_'+view+'.jsonl'),'bm25',view))
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for result in pool.map(execute,jobs):print(result,flush=True)
