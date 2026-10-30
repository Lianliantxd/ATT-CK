"""Authorized local CPU heads only. Authentic frozen feature extraction is separate."""
import os,sys,time,json,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main():
 assert (ROOT/'embeddings/FROZEN_GTE_FEATURES.npz').exists(),'Missing authentic frozen GTE feature cache; never fabricate vectors'
 control=ROOT/'results/HEADS_TRAINING_RUN_CONTROL.json';assert not control.exists(),'Do not reset global budget on hidden rerun';dump('results/HEADS_TRAINING_RUN_CONTROL.json',{'start_unix':time.time(),'wall_cap_seconds':5400,'disk_cap_bytes':2000000000,'protocol_sha256':sha(ROOT/'manifests/TRAINING_PROTOCOL.json'),'controller_source_sha256':sha(Path(__file__))})
 groups=[('FrozenGTE-Linear',['B3']),('GTE-Projection',['B4']),('GTE-StandardContrastive',['B5']),('GTE-HardNegative',['B6','B7','B8','B9','B9_CONST'])];count=0
 for fold in range(1,8):
  for seed in [17,42,73]:
   for augmentation in ['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']:
    for env,methods in groups:
     cmd=[str(ROOT/'venvs'/env/'bin/python'),'-B',str(ROOT/'contrastive/train_heads.py'),'--fold',f'fold_heldout_{fold}','--seed',str(seed),'--augmentation',augmentation,'--methods',*methods]
     control_data=json.loads(control.read_text());remaining=5400-(time.time()-control_data['start_unix']);assert remaining>1,'Global wall budget exhausted'
     p=subprocess.run(cmd,cwd=ROOT,timeout=min(1800,remaining))
     if p.returncode:dump('results/HEADS_TRAINING_FAILURE.json',{'command':cmd,'returncode':p.returncode,'no_automatic_hyperparameter_changes':True});raise RuntimeError('Training subprocess failed')
     count+=len(methods)
 dump('results/HEADS_MATRIX_COMPLETE.json',{'status':'ALL_REGISTERED_HEADS_TRAINED','configurations':count,'total_optimizer_updates':count*120,'new_GPU_training':False})
if __name__=='__main__':main()
