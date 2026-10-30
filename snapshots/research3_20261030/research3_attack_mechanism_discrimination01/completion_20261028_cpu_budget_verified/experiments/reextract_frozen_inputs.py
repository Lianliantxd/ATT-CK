"""Rebuild IR from the authorized sanitized fragment snapshot, never raw archives."""
import argparse
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *
from frozen_extractor import parse,relations

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args()
    source=ROOT/'frozen_inputs/LITERAL_EVENTS.jsonl'
    expected=next(r['sha256'] for r in read(ROOT/'manifests/INPUT_SNAPSHOT.json')['sources'] if r['snapshot']=='frozen_inputs/LITERAL_EVENTS.jsonl')
    assert sha(source)==expected
    target=Path(args.output);assert not target.exists()
    count=0
    with source.open() as inp,target.open('x') as out:
        for line in inp:
            # Identity gate before parsing any record body. The snapshot hash is also allowlisted above.
            sid=re.search(r'"sample_id"\s*:\s*"([0-9]+-[0-9]+-r[0-9]+)"',line)
            assert sid
            scene,step,rep=sid[1].split('-');assert not (scene=='1' and step in {'35','36','37'})
            row=json.loads(line);events=[]
            for old in row['events']:
                s=old['evidence_source']
                fragment={'source_id':old['source_id'],'source_type':old['source_type'],'line_id':s['line_id'],
                    'text':s['native_fragment'],'text_hash':s['native_line_sha256'],'char_start':s['char_range'][0],
                    'fragment_truncated':'NATIVE_FRAGMENT_TRUNCATED' in old['uncertainty']}
                events.append(parse(fragment,s['input_file_sha256']))
            assert events==row['events'],'deterministic extraction drift'
            out.write(json.dumps({'sample_id':sid[1],'events':events,'relations':relations(events)},ensure_ascii=False)+'\n');count+=len(events)
    print('Re-extracted',count,'events from authorized frozen snapshot')

if __name__=='__main__':main()
