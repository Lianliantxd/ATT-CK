import json,hashlib,re
from collections import Counter,defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def render(sources):
 return '\n'.join(x['text'] for s in sources for x in s['lines'])
def capped(sources,mode,budget):
 out=[{**s,'lines':[]} for s in sources];used=0;idx=0
 while True:
  found=False
  for n,source in enumerate(sources):
   if idx>=len(source['lines']):continue
   found=True;line=source['lines'][idx]
   if mode=='records':
    if used>=budget:return [s for s in out if s['lines']]
    out[n]['lines'].append(line);used+=1
   else:
    ts=list(re.finditer(r'\S+',line['text']))
    if used>=budget:return [s for s in out if s['lines']]
    remaining=budget-used
    if len(ts)>remaining:
     text=line['text'][:ts[remaining-1].end()] if remaining else ''
     out[n]['lines'].append({**line,'text':text,'text_hash':hashlib.sha256(text.encode()).hexdigest()});return [s for s in out if s['lines']]
    out[n]['lines'].append(line);used+=len(ts)
  if not found:return [s for s in out if s['lines']]
  idx+=1

def main():
 qs=[json.loads(x) for x in (R/'datasets/p0_prediction.jsonl').read_text().splitlines()]
 types=sorted({s['source_type'] for q in qs for s in q['sources']});views=['native','audit_only','non_audit_only','records40','tokens2048']+['type_'+t for t in types]
 stats=[]
 for view in views:
  with (R/'datasets'/('p0_'+view+'.jsonl')).open('w') as out:
   for q in qs:
    ss=q['sources']
    if view=='audit_only':ss=[s for s in ss if s['source_type']=='audit']
    elif view=='non_audit_only':ss=[s for s in ss if s['source_type']!='audit']
    elif view.startswith('type_'):ss=[s for s in ss if s['source_type']==view[5:]]
    elif view=='records40':ss=capped(ss,'records',40)
    elif view=='tokens2048':ss=capped(ss,'tokens',2048)
    out.write(json.dumps({'sample_id':q['sample_id'],'text':render(ss),'sources':ss})+'\n')
    stats.append({'sample_id':q['sample_id'],'view':view,'sources':len(ss),'records':sum(len(s['lines']) for s in ss),'regex_tokens':sum(len(re.findall(r'\S+',x['text'])) for s in ss for x in s['lines'])})
 (R/'datasets/manifests/P0_INPUT_COSTS.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in stats));print('views',views)
if __name__=='__main__':main()
