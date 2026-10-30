"""Gather real checkpoint receipts. Missing experiments stay explicitly unrun."""
import collections,csv,json,sys,platform
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
def main():
 receipts=[]
 for directory in ['runs_B2','runs_heads']:
  for p in sorted((ROOT/'results'/directory).glob('*_receipt.json')):
   r=json.loads(p.read_text());r['receipt_file']=str(p.relative_to(ROOT));receipts.append(r)
 with (ROOT/'MODEL_TRAINING_RECEIPTS.jsonl').open('w') as f:
  for r in receipts:f.write(json.dumps(r)+'\n')
 checkpoint=[];logs=[]
 for r in receipts:
  method=r['method'];cp=r.get('checkpoint_path')
  if not cp:
   name=f"{method}_{r['fold_id']}_seed{r['seed']}_{r['augmentation']}.npz";cp='checkpoints/heads/'+name
  checkpoint.append({'method':method,'fold_id':r['fold_id'],'seed':r['seed'],'augmentation':r['augmentation'],'checkpoint_path':cp,'bytes':(ROOT/cp).stat().st_size,'sha256':sha(ROOT/cp),'trainable_parameters':r['trainable_parameters'],'parameters_changed':r.get('parameters_changed',r.get('train_parameters_updated')),'reload_max_abs_diff':r.get('reload_max_abs_diff',r.get('checkpoint_reload_score_max_abs_delta'))})
  hist=r.get('training_logs')
  if hist is None:
   p=ROOT/'results/runs_heads'/f"{method}_{r['fold_id']}_seed{r['seed']}_{r['augmentation']}_training.json";hist=json.loads(p.read_text())
  for l in hist:logs.append({'method':method,'fold_id':r['fold_id'],'seed':r['seed'],'augmentation':r['augmentation'],**l})
 dump('CONTRASTIVE_CHECKPOINT_MANIFEST.json',{'checkpoints':checkpoint,'missing_standard_contrastive_checkpoint_status':'ACTUALLY_TRAINED' if any(x['method']=='B5' for x in checkpoint) else 'NOT_TRAINED_MISSING_GTE_FEATURES','GTE_backbone_updated':False})
 csvout('CONTRASTIVE_TRAINING_LOGS.csv',logs)
 count=0;negative_files=sorted((ROOT/'results/runs_heads').glob('*_negatives.jsonl'))
 with (ROOT/'NEGATIVE_SAMPLE_QUALIFICATION.csv').open('w') as output:
  writer=None
  for p in negative_files:
   with p.open() as f:
    for line in f:
     record=json.loads(line)
     if writer is None:writer=csv.DictWriter(output,fieldnames=list(record));writer.writeheader()
     writer.writerow(record);count+=1
  if not count:output.write('status,candidate_id\nNOT_MINED_REAL_FEATURES_PENDING_AUTHORIZATION,NA\n')
 csvout('HARD_NEGATIVE_ABLATION.csv',[x for x in csv.DictReader((ROOT/'results/OVERALL_RESULTS.csv').open()) if x['method'] in ['B6','B7','B8','B9','B9_CONST']] or [{'status':'NOT_TRAINED_MISSING_AUTHENTIC_GTE_FEATURES','mrr':'NA'}])
 write('FALSE_NEGATIVE_RISK_AUDIT.md','''# 假负例风险\n\n训练标签来自作者步骤注释，不是观察范围内逐技术反证。所有标准BCE/softmax负项均只是未标注补集。GTE困难负例未实际运行前不制造挖掘结果；实际运行后的逐候选表必须包含全部已知正例屏蔽和训练内共现来源。\n\n父子ID通过冻结父技术规范化合并；两个T1056子技术不能互作负例。未声明不同父ID等价；共现不自动合并技术或认定必然共同发生。可靠性权重只表示训练内风险代理，无人工或原始互斥认证，不存在EVIDENCE_CERTIFIED_NEGATIVE。全量P0共现矩阵不得用于每折训练。模型挖掘只对本折训练步骤，不能将保留组错误反馈训练。''')
 envs=json.loads((ROOT/'manifests/LOCAL_ENVIRONMENTS_CREATED.json').read_text());dump('TRAINING_ENVIRONMENT_MANIFEST.json',{'Python':platform.python_version(),'platform':platform.platform(),'numpy':np.__version__,'algorithm_environments':envs,'system_python_modified':False,'new_packages_downloaded':False,'new_GPU_training_authorized':False,'new_feature_extraction_authorized':(ROOT/'manifests/FEATURE_EXTRACTION_AUTHORIZATION.json').exists(),'new_LLM_calls':0})
 summary=[]
 for method in sorted({r['method'] for r in receipts}):
  rr=[r for r in receipts if r['method']==method];summary.append({'method':method,'configurations':len(rr),'updates':sum(r.get('updates',r.get('optimizer_updates',0)) for r in rr),'epochs_each':120,'CPU_seconds_sum':sum(r.get('cpu_method_seconds',r.get('cpu_seconds',0)) for r in rr),'wall_seconds_config_sum':sum(r.get('seconds',r.get('wall_seconds',0)) for r in rr),'peak_process_rss_bytes_max':max(r.get('peak_rss_bytes',r.get('peak_process_rss_bytes',0)) for r in rr),'checkpoint_bytes_sum':sum(x['bytes'] for x in checkpoint if x['method']==method),'trainable_parameters_min':min(r['trainable_parameters'] for r in rr),'trainable_parameters_max':max(r['trainable_parameters'] for r in rr)})
 csvout('results/TRAINING_COSTS.csv',summary);write('TRAINING_RESOURCE_REPORT.md','# 真实训练成本\n\n'+str(summary)+'\n\nB2逐配置时间不含每折共用词表/特征构建；进程RSS为累计峰值，不是每模型增量。CPU头不消耗模型Tokenizer，训练Token为N/A，而非0；视图/更新曝光次数另存收据。GTE原始特征前向的Token成本应与CPU训练单独报告。投影训练不是GTE主干微调。新GPU训练和LoRA始终不得由旧前向权限推定。')
 print('ACTUAL_TRAINED_CONFIGURATIONS',len(receipts),'CHECKPOINTS',len(checkpoint),'NEGATIVE_ROWS',count)
if __name__=='__main__':main()
