"""Descriptive class-support associations after prediction; never selects parameters."""
import csv,json,math,statistics
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(n):return list(csv.DictReader((R/n).open()))
def ranks(xs):
 order=sorted(range(len(xs)),key=xs.__getitem__);out=[0.]*len(xs);i=0
 while i<len(order):
  j=i+1
  while j<len(order) and xs[order[j]]==xs[order[i]]:j+=1
  for k in range(i,j):out[order[k]]=(i+j-1)/2+1
  i=j
 return out
def corr(x,y):
 x=ranks(x);y=ranks(y);a=statistics.mean(x);b=statistics.mean(y);den=math.sqrt(sum((v-a)**2 for v in x)*sum((v-b)**2 for v in y))
 return sum((v-a)*(w-b) for v,w in zip(x,y))/den if den else 'NA'
def main():
 groups=defaultdict(list)
 for r in read('results/PER_CLASS_RESULTS.csv'):
  if r['class_mrr']!='NA':groups[r['method'],r['view_id'],r['fold_id'],r['technique_id']].append(r)
 agg={k:{'support':int(v[0]['training_class_support']),'mrr':statistics.mean(float(r['class_mrr']) for r in v),'recall10':statistics.mean(float(r['class_recall10']) for r in v)} for k,v in groups.items()}
 rows=[]
 for view in ['ONE_VIEW_PER_STEP','MULTI_VIEW_AUGMENTATION']:
  for method,base in [('S0','Z0'),('C4','Z0'),('C4','S0'),('C0','Z0')]:
   for scope in ['ALL_TARGET_CLASSES','SEEN_TARGET_CLASSES']:
    keys=[k for k in agg if k[0]==method and k[1]==view and (scope=='ALL_TARGET_CLASSES' or agg[k]['support']>0)]
    for metric in ['mrr','recall10']:
     x=[agg[k]['support'] for k in keys];delta=[agg[k][metric]-agg[base,*k[1:]][metric] for k in keys]
     rows.append({'method':method,'baseline':base,'view_id':view,'scope':scope,'metric':metric,'unit':'fold_technique_pair_with_Gold; seeds_averaged','n_pairs':len(keys),'mean_delta_equal_pair':statistics.mean(delta),'spearman_support_vs_delta':corr(x,delta),'p_value':'NOT_COMPUTED_DEPENDENT_DESCRIPTIVE_ONLY','causal_interpretation':'NOT_IDENTIFIED'})
 with (R/'results/FREQUENCY_PERFORMANCE_ASSOCIATION.csv').open('w') as f:w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
 summary={r['method']:r for r in read('FUSION_RESULTS.csv') if r['view_id']=='ONE_VIEW_PER_STEP'}
 ratio=float(summary['C0']['mrr'])/float(summary['S0']['mrr'])
 body=f'''# 类别频率与识别收益

ONE主要协议：C0只按唯一训练步骤支持排序，MRR={float(summary['C0']['mrr']):.6f}；S0={float(summary['S0']['mrr']):.6f}，两者数值之比{ratio:.2%}。该比值不是“解释了多少方差”或因果贡献率。C0不用日志特征就可取得相当比例成绩，说明总体MRR受常见训练标签强烈影响；S0仍比C0高{float(summary['S0']['mrr'])-float(summary['C0']['mrr']):.6f}，不能把全部监督收益归为先验。

C0在SUPPORT_GE5目标的MRR=.550167，S0=.550887；但C0在one-shot为0、few-shot=.001667、unseen=0。频率表现集中于高支持类，不能代表普遍语义识别。C4在few-shot MRR=.157132高于S0的.137544；one-shot MRR=.033333高于S0 .015556，但Top10 .033333低于S0 .044444。不同指标不能互相替代。

C5(zGTE+训练先验)总体MRR=.143734，Unseen=.012296；P2(监督分数减训练先验)MRR=.174875、Unseen=0。它们说明频率修正改变排序，但不是对模型内部“理解”或遗忘的因果诊断。

下列Spearman仅描述每个有Gold的(fold,technique)在种子平均后的支持—性能增量关系。同一技术跨折重复、训练组重叠，不能将这些点当独立数据做p检验。全部32行相关性见results/FREQUENCY_PERFORMANCE_ASSOCIATION.csv；无保留分布进入预测先验，无关联结果用于参数选择。
'''
 body+='\n|方法−对照|目标范围|指标|pair数|Spearman|\n|---|---|---|---:|---:|\n'
 for r in rows:
  if r['view_id']=='ONE_VIEW_PER_STEP':body+=f"|{r['method']}−{r['baseline']}|{r['scope']}|{r['metric']}|{r['n_pairs']}|{r['spearman_support_vs_delta']:.4f}|\n"
 (R/'CLASS_FREQUENCY_ERROR_ANALYSIS.md').write_text(body)
 print('Frequency descriptive associations',len(rows))
if __name__=='__main__':main()
