"""Run fixed label-blind baseline matrix; evaluation is a separate later process."""
import concurrent.futures,json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1];OLD=R.parent/'research3_attack_technique_benchmark01'
BASEPY=OLD/'venvs/Benchmark/bin/python'
ENVS={'char':R/'venvs/CharacterNgramTFIDF/bin/python','word':OLD/'venvs/TFIDFTechniqueRetrieval/bin/python','bm25':OLD/'venvs/BM25TechniqueRetrieval/bin/python','hybrid':R/'venvs/WordCharacterHybrid/bin/python'}

def execute(job):
 protocol,inp,kname,mode,view=job[:5]
 reference=job[5] if len(job)>5 else R/"datasets/p0_reference.jsonl"
 tag=f'{protocol}_{mode}_{kname}_{view}';out=R/'experiments'/(tag+'.jsonl');receipt=R/'experiments'/(tag+'_receipt.json')
 command=[str(ENVS[mode]),'-B',str(R/'baselines/engine.py'),'--inputs',str(inp),'--knowledge',str(R/'knowledge'/(kname+'.json')),'--representation',mode,'--output',str(out)]
 start=time.perf_counter();p=subprocess.run(command,capture_output=True,text=True)
 data={'protocol':protocol,'input_view':view,'knowledge_view':kname,'representation':mode,'method':{'word':'TFIDF','bm25':'BM25','char':'CharacterNgramTFIDF','hybrid':'WordCharacterHybrid'}[mode],'command':command,'output':str(out),'exit_code':p.returncode,'seconds':time.perf_counter()-start,'stdout':p.stdout,'stderr':p.stderr,'execution_status':'PROJECT_NEW_INFERENCE','reference_path':str(reference)}
 receipt.write_text(json.dumps(data,indent=2));return data

def run(jobs):
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for r in pool.map(execute,jobs):
   print(r['method'],r['protocol'],r['knowledge_view'],r['input_view'],r['exit_code'],round(r['seconds'],2),flush=True)
   if r['exit_code']:raise RuntimeError(r['stderr'])
if __name__=='__main__':
 for name in ['WordCharacterHybrid']:
  if not (R/'venvs'/name/'bin/python').exists():subprocess.run([str(BASEPY),'-m','venv',str(R/'venvs'/name)],check=True)
 keys=['K0_NAMES_ONLY','K1_NAMES_AND_TACTICS','K2_DESCRIPTION_16_1','K3_DESCRIPTION_16_1_WITHOUT_TITLES','K4_COMMON_COVERAGE_203']
 jobs=[('P0',R/'datasets/p0_prediction.jsonl',k,mode,'all') for k in keys for mode in ['word','char','bm25','hybrid']]
 run(jobs)
