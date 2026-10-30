import csv,json,re,sys,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from evaluate_techniques import summarize
qs=[json.loads(x) for x in (ROOT/'STEP_LEVEL_DATASET.jsonl').read_text().splitlines() if json.loads(x)['scenario_id']=='7']
docs=json.loads((ROOT/'datasets/extended_knowledge_documents.json').read_text());rows=[];predictions=[]
def decode(text):
    def sub(m):
        try:
            value=bytes.fromhex(m.group(1)).decode('utf-8').replace('\x00',' ')
            return m.group(0)+' decoded_literal='+value if value.isprintable() else m.group(0)
        except (ValueError,UnicodeDecodeError):return m.group(0)
    return re.sub(r'\b(?:proctitle|a\d+)=([0-9a-fA-F]{8,})\b',sub,text)
def sources(text,audit):
    out=[];keep=False
    for line in text.splitlines():
        if line.startswith('    ') and not line.startswith('        ') and line.endswith(':'):keep=('audit' in line)==audit
        if keep:out.append(line)
    return '\n'.join(out)
for case in ['all','hexdecoded','native','audit_only','non_audit_only']:
    inp=[]
    for q in qs:
        text=q['strict_log_content']
        if case=='hexdecoded':text=decode(text)
        elif case=='native':text='\n'.join(line.strip() for line in text.splitlines() if not ((line and not line.startswith(' ') and line.endswith(':')) or (line.startswith('    ') and not line.startswith('        ') and line.endswith(':'))))
        elif case.endswith('_only'):text=sources(text,case=='audit_only')
        inp.append({'sample_id':q['sample_id'],'text':text})
    ip=ROOT/'method'/('input_'+case+'.jsonl');op=ROOT/'method'/('predictions_'+case+'.jsonl')
    ip.write_text(''.join(json.dumps(x)+'\n' for x in inp))
    cmd=[str(ROOT/'venvs/BM25TechniqueRetrieval/bin/python'),str(ROOT/'baselines/predict.py'),'--method','BM25','--inputs',str(ip),'--documents',str(ROOT/'datasets/extended_knowledge_documents.json'),'--output',str(op)]
    run=subprocess.run(cmd,capture_output=True,text=True);run.check_returncode()
    preds={x['sample_id']:x['predictions'] for x in map(json.loads,op.read_text().splitlines())}
    metrics=summarize([{'ground_truth':q['official_technique_labels'],'predictions':preds[q['sample_id']]} for q in qs],docs)
    rows.append({'case':case,'split':'scenario7_dev','protocol':'P1_OFFICIAL_SAMPLED_VIEW_ABLATION_NOT_V2_FULL_LOGS','empty_inputs':sum(not x['text'] for x in inp),**metrics})
    predictions.extend({'case':case,'sample_id':q['sample_id'],'predictions':preds[q['sample_id']]} for q in qs)
for name in ['METHOD_ABLATION_RESULTS.csv','BASELINE_RESULTS_P1.csv']:
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(ROOT/'method/DEV_PREDICTIONS.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in predictions))
print(json.dumps(rows,indent=2))
