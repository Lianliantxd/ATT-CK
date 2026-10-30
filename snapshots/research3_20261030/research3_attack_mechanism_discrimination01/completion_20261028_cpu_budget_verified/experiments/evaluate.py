"""Independent reference evaluation of two frozen CPU protocols and old neural scores."""
import collections
import itertools
import math
import random
import statistics
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *
from frozen_evaluator import summarize

def main():
    refs={r['sample_id']:r for r in records(ROOT/'inherited/REFERENCE.jsonl')}
    ids=sorted(next(iter(read(ROOT/'frozen_inputs/KNOWLEDGE.json').values())))
    assert len(ids)==216 and len(refs)==975
    groups=collections.defaultdict(list);detail={};metrics=[]
    files=[('BYTE',ROOT/'inherited/CPU_PREDICTIONS.jsonl'),('FEATURE',ROOT/'results/FEATURE_PREDICTIONS.jsonl'),('FEATURE',ROOT/'results/FEATURE_CONTROL_PREDICTIONS.jsonl')]
    assert sha(files[1][1])==read(ROOT/'manifests/FEATURE_PREDICTION_FREEZE.json')['prediction_sha256']
    assert sha(files[2][1])==read(ROOT/'manifests/FEATURE_CONTROL_FREEZE.json')['sha256']
    for protocol,path in files:
        for r in records(path):
            assert r['sample_id'] in refs
            allrank=r.get('ranking_all216',r['predictions']);assert len(allrank)==216 and set(allrank)==set(ids)
            key=(protocol,r['method']);groups[key].append(r)
    for (protocol,method),rows in sorted(groups.items()):
        assert len(rows)==975 and len({r['sample_id'] for r in rows})==975
        score=summarize([{'ground_truth':refs[r['sample_id']]['ground_truth'],'predictions':r['predictions'][:10]} for r in rows],ids)
        first=rows[0];out={'protocol':protocol,'method':method,'algorithm':first['algorithm'],'input_view':first['input_view'],
            'knowledge':first['knowledge'],'logical_steps':195,'scenarios':7,'simulations':34,'multilabel_queries':285,**score}
        metrics.append(out)
        for r in rows:
            g={x.split('.')[0] for x in refs[r['sample_id']]['ground_truth']};p=r['predictions'][:10]
            rank=min((i+1 for i,t in enumerate(p) if t in g),default=0)
            detail[protocol,method,r['sample_id']]={'top1':int(p[0] in g),'top10':int(rank>0),'mrr':1/rank if rank else 0}
    csvout('MECHANISM_BASELINE_RESULTS.csv',metrics)
    scen=[]
    for protocol,method in groups:
        for scene in sorted({r['scenario_id'] for r in refs.values()}):
            rs=[detail[protocol,method,s] for s,r in refs.items() if r['scenario_id']==scene]
            scen.append({'protocol':protocol,'method':method,'scenario':scene,'n_queries':len(rs),
                **{k:statistics.mean(x[k] for x in rs) for k in ['top1','top10','mrr']}})
    csvout('results/SCENARIO_METRICS.csv',scen)
    contrasts=[];rng=random.Random(42)
    for protocol in ['BYTE','FEATURE']:
        for alg in ['CHAR','BM25']:
            for knowledge in ['K2_DESCRIPTION_16_1','MECHANISM_CARD']:
                for view,baseline in [('LITERAL','RAW'),('LITERAL_PLUS_RELATIONS','LITERAL'),('RAW_PLUS_LITERAL','RAW')]:
                    contrasts.append((protocol,f'{alg}__{view}__{knowledge}',f'{alg}__{baseline}__{knowledge}','INPUT'))
            for knowledge in ['K0_NAMES_ONLY','K3_WITHOUT_TITLES','MECHANISM_CARD','K2_PLUS_CARD']:
                for view in ['RAW','LITERAL']:
                    contrasts.append((protocol,f'{alg}__{view}__{knowledge}',f'{alg}__{view}__K2_DESCRIPTION_16_1','KNOWLEDGE'))
            for v in ['CLEAN_FIELDS','ROLE_LABELS_REMOVED','NO_RESULT','NO_ACTION_NORMALIZATION']:
                contrasts.append((protocol,f'{alg}__LITERAL__K2_DESCRIPTION_16_1',f'{alg}__{v}__K2_DESCRIPTION_16_1','FORMAT_CONTROL'))
    stats=[]
    for protocol,a,b,kind in contrasts:
        for metric in ['top10','mrr']:
            grouped=collections.defaultdict(list)
            for sid,r in refs.items():grouped[r['scenario_id']].append(detail[protocol,a,sid][metric]-detail[protocol,b,sid][metric])
            blocks=[(sum(v),len(v)) for k,v in sorted(grouped.items())];point=sum(s for s,n in blocks)/975
            bootstrap=[]
            for _ in range(2000):
                sampled=[blocks[rng.randrange(7)] for _ in range(7)]
                bootstrap.append(sum(s for s,n in sampled)/sum(n for s,n in sampled))
            bootstrap.sort();null=[sum(sign*s for sign,(s,n) in zip(signs,blocks))/975 for signs in itertools.product([-1,1],repeat=7)]
            p=sum(abs(t)>=abs(point)-1e-14 for t in null)/128
            per_scene=[s/n for s,n in blocks]
            stats.append({'protocol':protocol,'method':a,'baseline':b,'contrast':kind,'metric':metric,
                'delta_query_weighted':point,'scenario_blocks':7,'logical_steps':195,
                'positive_scenarios':sum(v>1e-14 for v in per_scene),'negative_scenarios':sum(v< -1e-14 for v in per_scene),
                'scenario_effect_SD':statistics.stdev(per_scene),'conditional_block_bootstrap_95_low':bootstrap[49],
                'conditional_block_bootstrap_95_high':bootstrap[1949],'exact_scenario_signflip_p':p,
                'inference_scope':'exploratory only; seven scenario blocks not certified independent population samples; no generalization claim'})
    order=sorted(range(len(stats)),key=lambda i:stats[i]['exact_scenario_signflip_p']);running=0
    for j,i in enumerate(order):
        running=max(running,min(1,stats[i]['exact_scenario_signflip_p']*(len(stats)-j)));stats[i]['Holm_p']=running
    csvout('MECHANISM_INPUT_ABLATIONS.csv',[r for r in stats if r['contrast']!='KNOWLEDGE'])
    csvout('MECHANISM_KNOWLEDGE_ABLATIONS.csv',[r for r in stats if r['contrast']=='KNOWLEDGE'])
    dump('results/OFFLINE_SUMMARY.json',{'conditions':len(metrics),'prediction_rows':sum(len(v) for v in groups.values()),
        'metrics':metrics,'contrasts':len(stats),'queries_each':975,'logical_steps':195,'scenarios':7,
        'MRR':'frozen evaluator MRR@10, not unrestricted MRR','new_model_forwards':0,'neural_new_views':'MODEL_FORWARD_NOT_AUTHORIZED'})
    diagnostics=[];old_emb={r['sample_id']:r for r in records(ROOT/'inherited/NEURAL_EMBEDDING.jsonl') if r['method']=='E1_NATIVE_PREFIX'}
    old_ce={(r['sample_id'],r['candidate_pool'],r['candidate_k']):r for r in records(ROOT/'inherited/NEURAL_RERANKER.jsonl')}
    percase=[]
    for pool in ['embedding','lexical']:
        for k in [20,50,100]:
            rows=[];category=collections.Counter();recalls=[];first_rank=[];cors=[];inversions=[]
            for sid,ref in refs.items():
                ce=old_ce[sid,pool,k];before=ce['original_candidates'];after=ce['predictions'];g={t.split('.')[0] for t in ref['ground_truth']}
                assert len(before)==k==len(after)==len(set(after)) and set(before)==set(after)
                scores=dict(zip(after,ce['raw_logits']));assert after==sorted(before,key=lambda t:(-scores[t],t))
                rb=min((i+1 for i,t in enumerate(before) if t in g),default=0);ra=min((i+1 for i,t in enumerate(after) if t in g),default=0)
                a10=bool(set(after[:10])&g);b10=bool(set(before[:10])&g)
                cat='CANDIDATE_NOT_RETRIEVED' if not rb else 'CANDIDATE_DEMOTED_BY_RERANKER' if b10 and not a10 else 'CANDIDATE_PROMOTED_BY_RERANKER' if a10 and not b10 else 'CANDIDATE_RETRIEVED_BUT_RANKED_LOW' if not a10 else 'BOTH_TOP10'
                category[cat]+=1;recalls.append(len(set(before)&g)/len(g))
                if ra:first_rank.append(ra)
                ranks={t:i+1 for i,t in enumerate(after)};seq=[ranks[t] for t in before]
                rho=1-6*sum((i+1-ranks[t])**2 for i,t in enumerate(before))/(k*(k*k-1));cors.append(rho)
                inv=sum(seq[i]>seq[j] for i in range(k) for j in range(i+1,k));inversions.append(inv/(k*(k-1)/2))
                rows.append({'ground_truth':ref['ground_truth'],'predictions':after})
                percase.append({'sample_id':sid,'pool':pool,'K':k,'category':cat,'first_gold_before':rb or 'NA','first_gold_after':ra or 'NA',
                    'candidate_recall':recalls[-1],'rank_inversion_ratio':inversions[-1],'semantic_cause':'UNRESOLVED_NO_INDEPENDENT_EVENT_REFERENCE'})
            diagnostics.append({'pool':pool,'K':k,'queries':975,'candidate_hit':1-category['CANDIDATE_NOT_RETRIEVED']/975,
                'candidate_recall_macro':statistics.mean(recalls),'first_gold_rank_mean_given_retrieved':statistics.mean(first_rank),
                'Spearman_mean':statistics.mean(cors),'inversion_ratio_mean':statistics.mean(inversions),
                **{key:category[key] for key in ['CANDIDATE_NOT_RETRIEVED','CANDIDATE_DEMOTED_BY_RERANKER','CANDIDATE_PROMOTED_BY_RERANKER','CANDIDATE_RETRIEVED_BUT_RANKED_LOW','BOTH_TOP10']},
                **summarize(rows,ids)})
    csvout('results/NEURAL_CANDIDATE_DIAGNOSTICS.csv',diagnostics);csvout('RERANKER_FAILURE_TAXONOMY.csv',percase)
    lookup={(p,m):{r['sample_id']:r for r in rs} for (p,m),rs in groups.items()}
    for case in read(ROOT/'inherited/DIAGNOSTIC_30.json')['cases']:
        sid=case['sample_id'];gold={t.split('.')[0] for t in refs[sid]['ground_truth']}
        comparisons=[]
        for protocol in ['BYTE','FEATURE']:
            for alg in ['CHAR','BM25']:
                for view in ['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']:
                    method=f'{alg}__{view}__K2_DESCRIPTION_16_1';r=lookup[protocol,method][sid]
                    comparisons.append({'protocol':protocol,'method':method,'top10':r['predictions'][:10],**detail[protocol,method,sid]})
        percase_record={'sample_id':sid,'scenario':case['scenario_id'],'step':case['step_id'],'simulation':case['simulation_id'],
            'stratum':case['stratum'],'author_step_labels':refs[sid]['ground_truth'],'classification_results':comparisons,
            'mechanism_semantic_support':'NOT_EVALUATED_HUMAN_REFERENCE_PENDING','limitations':['step labels do not prove visible evidence sufficiency','historically exposed development selection']}
        # Separate from review packets; no agent-filled human decision.
        with (ROOT/'results/DIAGNOSTIC_30_ANALYSIS.jsonl').open('a' if percase_record['sample_id']!=read(ROOT/'inherited/DIAGNOSTIC_30.json')['cases'][0]['sample_id'] else 'x') as f:
            f.write(json.dumps(percase_record,ensure_ascii=False)+'\n')
    print('Recomputed',len(metrics),'CPU conditions,',sum(len(v) for v in groups.values()),'predictions;',len(stats),'block-aware contrasts.')
    for m in metrics:
        if m['knowledge']=='K2_DESCRIPTION_16_1' and m['input_view'] in ['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL']:
            print(m['protocol'],m['method'],'Top1',round(m['top1_accuracy']*100,3),'Top10',round(m['top10_accuracy']*100,3),'MRR',round(m['mrr'],4))

if __name__=='__main__':main()
