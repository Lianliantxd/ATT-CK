"""Independent saved-score, metric and inheritance checks; no model or archive access."""
import collections
import math
import shutil
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *
from frozen_engine import words

def main():
    copies=['CANDIDATE_SCORE_CONSISTENCY.csv','CANDIDATE_RANK_TRANSITIONS.csv',
        'DIAGNOSTIC_30_SELECTION_PROTOCOL.md','DIAGNOSTIC_30_FROZEN_IDS.json','DIAGNOSTIC_30_CASES.jsonl',
        'DIAGNOSTIC_30_DEPENDENCY_AUDIT.csv','MECHANISM_IR_SCHEMA.json','MECHANISM_SOURCE_TRACE.csv',
        'MECHANISM_CARD_SOURCE_AUDIT.csv','MECHANISM_BLIND_REVIEW_PACKETS.jsonl',
        'MECHANISM_HUMAN_REVIEW_STATUS.csv','MODEL_FORWARD_AUTHORIZATION_REQUEST.md']
    receipts=[]
    for name in copies:
        src=BASE/name;dst=ROOT/name;assert not dst.exists()
        shutil.copyfile(src,dst);receipts.append({'name':name,'source':str(src),'sha256':sha(dst)})
    for srcname,dstname in [('MECHANISM_LITERAL.jsonl','frozen_inputs/LITERAL_EVENTS.jsonl'),
        ('MECHANISM_RELATIONS.jsonl','frozen_inputs/RELATIONS.jsonl'),
        ('TECHNIQUE_MECHANISM_CARDS.jsonl','inherited/CARDS.jsonl'),
        ('KNOWLEDGE_VERSION_MANIFEST.json','inherited/KNOWLEDGE_MANIFEST.json')]:
        shutil.copyfile(ROOT/dstname,ROOT/srcname)
    for name in ['SCORER_CHANNEL_AUDIT.json','CARD_WORD_ORDER_INVARIANCE.csv']:
        shutil.copyfile(BASE/'results'/name,ROOT/'results'/('INHERITED_'+name))
    shutil.copyfile(BASE/'manifests/PROPOSED_GPU_TRANSFER.json',ROOT/'manifests/PROPOSED_GPU_TRANSFER.json')
    dump('manifests/SUPPLEMENTAL_COPIES.json',receipts)
    refs={r['sample_id']:r for r in records(ROOT/'inherited/REFERENCE.jsonl')}
    rows=list(records(ROOT/'inherited/NEURAL_RERANKER.jsonl'));pairs={};ties=0
    for row in rows:
        assert row['sample_id'] in refs
        order=row['predictions'];logits=row['raw_logits'];scores=dict(zip(order,logits))
        assert len(order)==row['candidate_k']==len(set(order))==len(logits)
        assert order==sorted(row['original_candidates'],key=lambda t:(-scores[t],t))
        assert all(math.isfinite(x) for x in logits)
        ties+=sum(logits[i]==logits[i+1] for i in range(len(logits)-1))
        for tid,score in scores.items():
            key=(row['sample_id'],tid)
            if key in pairs:assert pairs[key]==score
            pairs[key]=score
    audit=read(ROOT/'inherited/RERANKER_VALIDATION.json')
    audit.update({'independent_reconstruction_rows':len(rows),'independently_checked_unique_pairs':len(pairs),
        'adjacent_score_ties_over_saved_rows':ties,
        'num_labels_dimension':'fixed-revision official config: one LABEL_0, ModernBertForSequenceClassification; saved scalar logits consistent; no fresh runtime forward',
        'official_config_url':'https://huggingface.co/Alibaba-NLP/gte-reranker-modernbert-base/blob/f7481e6055501a30fb19d090657df9ec1f79ab2c/config.json',
        'config_check_scope':'formatted official fixed revision page; not an independent hash of downloaded config bytes',
        'tie_qualification':'descending raw score with technique ID tie-break; new candidates can displace through higher scores or ties',
        'current_continuation_model_forwards':0,'semantic_cause':'UNRESOLVED'})
    dump('RERANKER_SCORING_VALIDATION.json',audit)
    inherited=read(BASE/'manifests/INHERITED_ASSETS.json');checks=[]
    forbidden=('llm_queries','raw_archive','pwnkit','official_sources','conv-a01')
    for entry in inherited:
        p=Path(entry['source']);assert not any(s in str(p).lower() for s in forbidden),str(p)
        actual=sha(p);assert actual==entry['sha256'],str(p)
        checks.append({'source':str(p),'expected_sha256':entry['sha256'],'actual_sha256':actual,'match':True})
    csvout('results/INHERITED_HASH_VERIFICATION.csv',checks)
    metrics={(r['protocol'],r['method']):r for r in read(ROOT/'results/OFFLINE_SUMMARY.json')['metrics']}
    grouped=collections.defaultdict(list)
    for protocol,path in [('BYTE','inherited/CPU_PREDICTIONS.jsonl'),('FEATURE','results/FEATURE_PREDICTIONS.jsonl'),('FEATURE','results/FEATURE_CONTROL_PREDICTIONS.jsonl')]:
        for row in records(ROOT/path):grouped[protocol,row['method']].append(row)
    supplement=[]
    ids=set(next(iter(read(ROOT/'frozen_inputs/KNOWLEDGE.json').values())))
    for key,rs in grouped.items():
        ref=metrics[key];allgold={t.split('.')[0] for r in refs.values() for t in r['ground_truth']}
        for k in [1,5,10]:
            tp=collections.Counter();fp=collections.Counter();fn=collections.Counter();hits=0;rr=0
            for row in rs:
                g={t.split('.')[0] for t in refs[row['sample_id']]['ground_truth']};p=set(row['predictions'][:k])
                hits+=bool(g&p)
                for t in g&p:tp[t]+=1
                for t in p-g:fp[t]+=1
                for t in g-p:fn[t]+=1
                ranks=[i+1 for i,t in enumerate(row['predictions'][:10]) if t in g];rr+=1/min(ranks) if ranks else 0
            assert abs(hits/975-ref[f'top{k}_accuracy'])<1e-12
            assert abs(rr/975-ref['mrr'])<1e-12
            def f1(t):return 2*tp[t]/(2*tp[t]+fp[t]+fn[t]) if 2*tp[t]+fp[t]+fn[t] else 0
            micro=2*sum(tp.values())/(2*sum(tp.values())+sum(fp.values())+sum(fn.values()))
            macro=sum(f1(t) for t in ids)/216
            if k==5:assert abs(micro-ref['micro_f1_at_5'])<1e-12 and abs(macro-ref['macro_f1_at_5_all_candidates'])<1e-12
            supplement.append({'protocol':key[0],'method':key[1],'K':k,'micro_F1':micro,'macro_F1_all216':macro,'macro_F1_gold_present':sum(f1(t) for t in allgold)/len(allgold)})
    csvout('results/SUPPLEMENTARY_F1_AT_K.csv',supplement)
    dump('results/INDEPENDENT_AUDIT.json',{'inherited_assets_unchanged':len(checks),'CPU_conditions_recomputed':len(grouped),
        'prediction_rows':sum(map(len,grouped.values())),'saved_neural_rows':len(rows),'unique_saved_neural_pairs':len(pairs),
        'new_model_calls':0,'raw_archives_opened':0,'restricted_steps_read':0,'independent_semantic_accuracy':'NA_HUMAN_PENDING',
        'parent_directory':'read-only snapshot; concurrent new files do not change continuation scope'})
    print('PASS',len(checks),'inherited hashes;',len(grouped),'conditions;',len(pairs),'saved score pairs')

if __name__=='__main__':main()
