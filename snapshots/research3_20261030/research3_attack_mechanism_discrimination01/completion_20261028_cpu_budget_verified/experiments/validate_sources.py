"""Independent complete source-span checks against allowlisted cleaned records."""
import collections
import csv
from decimal import Decimal
import json
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *
from frozen_extractor import TECHNIQUE

def main():
    original=PREVIOUS/'embedding/server_inputs/P0_PREDICTION_ONLY.jsonl'
    digest=sha(original);allowed={r['sample_id'] for r in records(ROOT/'inherited/REFERENCE.jsonl')}
    native={}
    with original.open() as f:
        for line in f:
            match=re.search(r'"sample_id"\s*:\s*"([^"\\]+)"',line);assert match and match[1] in allowed
            row=json.loads(line);assert set(row)=={'sample_id','text','sources'};native[row['sample_id']]=row
    rels={r['sample_id']:r['relations'] for r in records(ROOT/'frozen_inputs/RELATIONS.jsonl')}
    fields=0;events=0;status=collections.Counter();relation_types=collections.Counter();retention=collections.Counter();trace=[]
    for sample in records(ROOT/'frozen_inputs/LITERAL_EVENTS.jsonl'):
        sid=sample['sample_id'];lines={(s['source_id'],l['line_id']):l for s in native[sid]['sources'] for l in s['lines']}
        lookup={e['event_id']:e for e in sample['events']}
        for event in sample['events']:
            events+=1;s=event['evidence_source'];line=lines[event['source_id'],s['line_id']];a,b=s['char_range'];raw=line['text'][a:b]
            assert raw==s['native_fragment'] and hashlib.sha256(raw.encode()).hexdigest()==s['fragment_sha256']
            assert digest==s['input_file_sha256'] and hashlib.sha256(line['text'].encode()).hexdigest()==s['native_line_sha256']
            accepted={f['field_id'] for f in event['native_fields']}
            for component in [event['subject'],event['action'],event['object'],event['result']]+event['observed_state']:
                assert set(component['field_refs'])<=accepted
            for field in event['native_fields']:
                fields+=1
                if 'span' in field:
                    value=line['text'][field['span'][0]:field['span'][1]];assert value==field['raw_value']
                    decoded=value[1:-1] if len(value)>1 and value[0]==value[-1] and value[0] in ['"',"'"] else value
                    assert decoded==field['value']
                else:
                    value=json.loads(raw)
                    for key in field['json_pointer'].split('/')[1:]:value=value[key]
                    assert str(value)==field['value']
                retention[field['locator']]+=1
                trace.append({'sample_id':sid,'event_id':event['event_id'],'field_id':field['field_id'],'locator':field['locator'],
                              'source_verified':True,'source_hash':s['native_line_sha256']})
            if event['result']['status'].startswith('REPORTED_SYSCALL'):
                assert any(f['key']=='success' and f['value'] in ['yes','no'] for f in event['native_fields'])
            status[event['result']['status']]+=1
            assert 'NO_CAUSAL_OR_STATE_CHANGE_INFERENCE' in event['uncertainty']
        for relation in rels[sid]:
            a,b=lookup[relation['from']],lookup[relation['to']];assert a['source_id']==b['source_id'];relation_types[relation['type']]+=1
            if relation['type']=='SAME_NATIVE_AUDIT_EVENT':
                assert a['temporal_scope']['native_epoch']==b['temporal_scope']['native_epoch']
                assert a['temporal_scope']['native_event_serial']==b['temporal_scope']['native_event_serial']
            elif relation['type']=='NATIVE_TIMESTAMP_BEFORE':assert Decimal(a['temporal_scope']['native_epoch'])<Decimal(b['temporal_scope']['native_epoch'])
            else:raise AssertionError('unsupported relation')
    cards=list(records(ROOT/'inherited/CARDS.jsonl'));k2=read(STRONG/'knowledge/K2_DESCRIPTION_16_1.json');mentions=0
    for card in cards:
        assert card['state_requirements']==card['temporal_requirements']==card['result_requirements']==[]
        for f in card['mechanism_actions']+card['mechanism_objects']:
            a,b=f['source_span'];assert k2[card['technique_id']][a:b]==f['literal'];mentions+=1
    for row in records(ROOT/'frozen_inputs/BYTE_VIEWS.jsonl'):
        assert set(row)=={'sample_id','views'} and all(not TECHNIQUE.search(t) for t in row['views'].values())
    packets=list(records(BASE/'MECHANISM_BLIND_REVIEW_PACKETS.jsonl'))
    assert len(packets)==30
    for packet in packets:
        assert not set(packet)&{'sample_id','ground_truth','stratum','predictions','scores'}
        assert packet['human_reference_status']=='PENDING'
    csvout('results/INDEPENDENT_FIELD_TRACE_CHECKS.csv',trace)
    dump('results/SOURCE_VALIDATION.json',{'queries':len(native),'IR_events':events,'native_fields_checked':fields,
        'source_mismatches':0,'card_mentions_checked':mentions,'card_count':len(cards),'relation_counts':dict(relation_types),
        'result_status_counts':dict(status),'field_locator_counts':dict(retention),'blind_packets_pending':30,
        'process_lifecycle_identity_certified':0,'observed_state_to_change_inferences':0,
        'semantic_mechanism_accuracy':'NA_HUMAN_REFERENCE_PENDING','raw_archives_opened':0,
        'scope':'complete selected-field trace validity; unrecognized prose is not claimed preserved in model views; full selected native fragment retained in IR provenance'})
    print('Verified',events,'events,',fields,'fields,',sum(relation_types.values()),'relations and',mentions,'knowledge mentions.')

if __name__=='__main__':main()
