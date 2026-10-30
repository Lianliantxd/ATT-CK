"""Predeclared format ablations and a knowledge-budget-matched literal control."""
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *
from frozen_engine import Index
from frozen_extractor import parse,relations,render

def main():
    names=['CLEAN_FIELDS','ROLE_LABELS_REMOVED','NO_RESULT','NO_ACTION_NORMALIZATION']
    dump('manifests/FEATURE_CONTROL_PREREGISTRATION.json',{'controls':names,'knowledge':'same feature-clipped K2',
        'literal_match':'same common native fragments, generic equal-weight action/object Jaccard; mentions extracted from same clipped K2',
        'Gold_or_new_feature_metrics_seen':False,'chosen_from_existing_task_controls':True})
    with (ROOT/'results/FEATURE_INPUT_BUDGETS.csv').open() as f:
        lengths={r['sample_id']:int(r['common_native_characters']) for r in csv.DictReader(f)}
    controls=[];vocab=read(ROOT/'inherited/KNOWLEDGE_MANIFEST.json')['neutral_concept_vocabulary']
    docs=read(ROOT/'frozen_inputs/FEATURE_KNOWLEDGE.json')['K2_DESCRIPTION_16_1']
    for row in records(ROOT/'frozen_inputs/LITERAL_EVENTS.jsonl'):
        left=lengths[row['sample_id']];events=[]
        for old in row['events']:
            if left<=0:break
            source=old['evidence_source'];text=source['native_fragment'];n=min(left,len(text));left-=n
            fragment={'text':text[:n],'char_start':source['char_range'][0],'source_id':old['source_id'],
                'source_type':old['source_type'],'line_id':source['line_id'],'text_hash':source['native_line_sha256'],
                'fragment_truncated':n<len(text) or 'NATIVE_FRAGMENT_TRUNCATED' in old['uncertainty']}
            events.append(parse(fragment,source['input_file_sha256']))
        rels=relations(events);views={v:render(events,rels,v) for v in names}
        actions={e['action']['concept'] for e in events}-{None};objects=set()
        for e in events:
            if e['object']['type']=='FILE_PATH_ROLE_UNRESOLVED':objects.add('file')
            if e['object']['type']=='NETWORK_ENDPOINT_ROLE_UNCONFIRMED':objects.update(['network','address'])
            if e['object']['type']=='DOMAIN_NAME':objects.add('domain')
        controls.append({'sample_id':row['sample_id'],'views':views,'actions':actions,'objects':objects})
    with (ROOT/'results/FEATURE_CONTROL_PREDICTIONS.jsonl').open('x') as f:
        for mode in ['char','bm25']:
            idx=Index(docs,mode)
            for name in names:
                for r in controls:
                    score=idx.score(r['views'][name]);order=sorted(range(216),key=lambda i:(-score[i],idx.ids[i]))
                    f.write(json.dumps({'sample_id':r['sample_id'],'method':mode.upper()+'__'+name+'__K2_DESCRIPTION_16_1',
                        'algorithm':mode,'input_view':name,'knowledge':'K2_DESCRIPTION_16_1','predictions':[idx.ids[i] for i in order]})+'\n')
        features={t:({a for a,p in vocab['actions'].items() if re.search(p,doc,re.I)},
                     {o for o in vocab['objects'] if re.search(r'\b'+o+r's?\b',doc,re.I)}) for t,doc in docs.items()}
        for r in controls:
            scores={t:len(r['actions']&a)/max(1,len(r['actions']|a))+len(r['objects']&o)/max(1,len(r['objects']|o)) for t,(a,o) in features.items()}
            ranking=sorted(scores,key=lambda t:(-scores[t],t))
            f.write(json.dumps({'sample_id':r['sample_id'],'method':'LiteralMechanismMatching_MATCHED_K2',
                'algorithm':'literal_jaccard','input_view':'LITERAL','knowledge':'K2_DESCRIPTION_16_1',
                'predictions':ranking,'score_top10':[scores[t] for t in ranking[:10]]})+'\n')
    dump('manifests/FEATURE_CONTROL_FREEZE.json',{'sha256':sha(ROOT/'results/FEATURE_CONTROL_PREDICTIONS.jsonl'),
        'conditions':9,'queries_each':975,'neural_calls':0})
    dump('manifests/PREFIX_SELECTION_SCOPE_NOTE.json',{'clarification':'binary prefix feasibility search is deterministic and budget-checked, but normalization and partial fields may be nonmonotone; global maximality is not certified',
        'all_saved_texts_within_budget':True,'predictions_or_inputs_changed':False,'no_posthoc_retuning':True})
    print('Nine additional fixed CPU controls completed.')

if __name__=='__main__':main()
