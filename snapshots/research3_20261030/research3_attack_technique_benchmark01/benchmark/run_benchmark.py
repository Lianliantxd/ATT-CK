"""Reproduce with: venvs/Benchmark/bin/python benchmark/run_benchmark.py"""
import ast
import csv
import gzip
import hashlib
import importlib.util
import json
import random
import re
import subprocess
import sys
import time
from collections import Counter,defaultdict,deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'baselines')]
from evaluate_techniques import summarize,normalize_technique_id,normalize_ranked
from retrieval import Retriever
SRC=ROOT/'official_sources'

def dump(name,obj):
    (ROOT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def csvout(name,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with (ROOT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def jsonl(name,rows):
    with (ROOT/name).open('w') as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def allowed(line):
    # Official JSONL serializes metadata first. Reject forbidden steps before parsing body.
    h=re.match(r'\{"scenario": "([^"]*)", "variant": "([^"]*)", "step": "([^"]*)"',line)
    if h is None:raise ValueError('Unknown JSONL header: stop before body processing')
    sc,va,st=h.groups()
    return not(sc=='1' and st.split('_')[0] in {'35','36','37'})
def body(prompt):
    lines=prompt.splitlines();start=next((i for i,x in enumerate(lines) if x and not x.startswith(' ') and x.endswith(':')),None)
    if start is None:raise ValueError('Missing host header')
    return '\n'.join(lines[start:])
def official_clean(text):
    # Exact regex literals copied from get_llm_responses.py, never import its API code.
    for pattern in [r'\s*key="[^"]*"',r'\s*key=\\"[^"]*\\"',r'\s*"key"\s*:\s*"[^"]*"',r',?\s*"mitre_tactic_id"\s*:\s*\[[^\]]*\]',r',?\s*"mitre_tactic_name"\s*:\s*\[[^\]]*\]',r',?\s*"mitre_technique_id"\s*:\s*\[[^\]]*\]',r',?\s*"mitre_technique_name"\s*:\s*\[[^\]]*\]',r',?\s*"mitre"\s*:\s*\{[^{}]*\}']:
        text=re.sub(pattern,'',text)
    return text
def max_sampled_records_per_source(text):
    counts=[];current=0
    for line in text.splitlines():
        if line.startswith('    ') and not line.startswith('        ') and line.endswith(':'):
            counts.append(current);current=0
        elif line.startswith('        '):current+=1
    return max(counts+[current])

def strict(text):
    # Preserve commands, objects, ports and path strings. Remove direct ATT&CK IDs and annotation fields.
    text=re.sub(r'(?i)\bT\d{4}(?:\.\d{3})?\b','[LABEL_REMOVED]',text)
    text=re.sub(r'(?i)"(?:mitre|techniques?|tactics?)"\s*:\s*(?:\[[^\]]*\]|\{[^}]*\}|"[^"]*")','"label_removed":null',text)
    return text

def main():
    started=time.perf_counter()
    labels=json.loads((SRC/'labels.json').read_text())
    # Only metadata keys are used; commands, full_path, attackmate and descriptions never enter views.
    matrix=json.loads((SRC/'mitre_matrix.json').read_text())
    universe=sorted({normalize_technique_id(x) for x in matrix})
    docs={key:[] for key in universe}
    for key,v in matrix.items():docs[normalize_technique_id(key)].append(v['name']+' '+' '.join(v['tactics']))
    docs={k:' '.join(v) for k,v in docs.items()}
    dump('datasets/official_knowledge_documents.json',docs)
    queries=[];counts=Counter();bad=[];mismatches=[];line_audit=[]
    for line in (SRC/'llm_queries.json').open():
        if not allowed(line):continue
        j=json.loads(line);key=j['scenario']+('_'+j['variant'] if j['variant'] else '')+'-'+j['step'].split('_')[0]
        if key not in labels:bad.append(key);continue
        gold=list(labels[key]['metadata'])
        if set(gold)!=set(j['ground_truth']):mismatches.append(key)
        group=j['scenario']+'-'+j['step'];rep=counts[group];counts[group]+=1
        raw_body=body(j['prompt']); cleaned_prompt=official_clean(j['prompt']);text=body(cleaned_prompt);clean=strict(text)
        loglines=[x.strip() for x in text.splitlines() if x.startswith('        ')]
        sources=[x.strip()[:-1] for x in text.splitlines() if x.startswith('    ') and not x.startswith('        ') and x.endswith(':')]
        q={'sample_id':group+'-r'+str(rep),'scenario_id':j['scenario'],'variant_id':j['variant'],'simulation_id':j['scenario']+('_'+j['variant'] if j['variant'] else ''),'step_id':j['step'],'sampling_replica_id':rep,'log_source_ids':sources,'visible_log_content':text,'strict_log_content':clean,'log_line_count':len(loglines),'official_technique_labels':gold,'normalized_technique_labels':sorted({normalize_technique_id(x) for x in gold}),'tactic_labels':sorted({t for x in gold for t in matrix.get(x,{}).get('tactics',[])}),'attack_knowledge_version':'official-matrix-sha256:'+sha(SRC/'mitre_matrix.json'),'source_hash':hashlib.sha256(cleaned_prompt.encode()).hexdigest(),'raw_query_hash':hashlib.sha256(j['prompt'].encode()).hexdigest(),'label_source':key,'input_view':'official persisted query body; v1'}
        queries.append(q)
        line_audit.append({'sample_id':q['sample_id'],'direct_ids':len(re.findall(r'\bT\d{4}(?:\.\d{3})?\b',text)),'annotation_fields':len(re.findall(r'(?i)"(?:mitre|techniques?|tactics?)"\s*:',text)),'raw_direct_ids':len(re.findall(r'T\d{4}',raw_body)),'official_clean_changed':raw_body!=text,'strict_changed':text!=clean,'max_lines_per_source':max_sampled_records_per_source(text)})
    if bad or mismatches:raise ValueError({'missing':bad,'mismatch':mismatches})
    jsonl('STEP_LEVEL_DATASET.jsonl',queries)
    jsonl('datasets/prediction_view_official.jsonl',[{'sample_id':q['sample_id'],'text':q['visible_log_content']} for q in queries])
    jsonl('datasets/prediction_view_strict.jsonl',[{'sample_id':q['sample_id'],'text':q['strict_log_content']} for q in queries])
    jsonl('datasets/reference_view.jsonl',[{'sample_id':q['sample_id'],'ground_truth':q['official_technique_labels']} for q in queries])
    lookup=defaultdict(deque)
    for q in queries:lookup[(q['scenario_id'],q['variant_id'],q['step_id'],q['source_hash'])].append(q['sample_id'])
    response_counts=Counter();response_sets=defaultdict(set);hist=defaultdict(list);sanitized=[];raw_diagnostics=defaultdict(Counter)
    for line in (SRC/'llm_responses.json').open():
        if not allowed(line):continue
        j=json.loads(line);model=j['canonical_slug'];h=hashlib.sha256(j['prompt'].encode()).hexdigest();key=(j['scenario'],j['variant'],j['step'],h)
        idx=response_counts[(model,key)];response_counts[(model,key)]+=1
        ids=list(lookup[key])
        if idx>=len(ids):raise ValueError(('Unmatched historical prediction',model,key[:3],idx,len(ids)))
        sid=ids[idx];q=next(q for q in queries if q['sample_id']==sid)
        pred=j.get('response',{}).get('techniques',[]) if isinstance(j.get('response'),dict) else []
        if not isinstance(pred,list):raise ValueError('Malformed historical list')
        hist[model].append({'sample_id':sid,'ground_truth':q['official_technique_labels'],'predictions':pred})
        response_sets[model].add(sid)
        raw_diagnostics[model]['raw_prediction_items']+=len(pred)
        normalized=normalize_ranked(pred,universe)
        raw_diagnostics[model]['invalid_items']+=normalized.count('__INVALID__')
        raw_diagnostics[model]['duplicate_parent_items']+=len(pred)-len(normalized)
        raw_diagnostics[model]['empty_predictions']+=int(not pred)
        sanitized.append({k:j[k] for k in ['scenario','variant','step','canonical_slug','response']})
    jsonl('datasets/eligible_author_responses.jsonl',sanitized)
    # Execute untouched official CLI on eligible response subset; 5 random trials only,
    # which does not change the deterministic author-model metric rows.
    command=[sys.executable,str(SRC/'get_statistics.py'),'--labels',str(SRC/'labels.json'),'--responses',str(ROOT/'datasets/eligible_author_responses.jsonl'),'--mitre-matrix',str(SRC/'mitre_matrix.json'),'--out-prefix',str(ROOT/'results/official'),'--random-trials','5']
    run=subprocess.run(command,capture_output=True,text=True)
    (ROOT/'results/official_stdout.txt').write_text(run.stdout);(ROOT/'results/official_stderr.txt').write_text(run.stderr)
    dump('results/OFFICIAL_RUN.json',{'command':command,'exit_code':run.returncode,'random_trials':5})
    if run.returncode:raise RuntimeError('Official evaluator failed')
    official=list(csv.DictReader((ROOT/'results/official_model_metrics.csv').open()))
    checks=[];recalc=[];prediction_counts=[]
    for m,records in hist.items():
        score=summarize(records,universe,official_compat=True)
        row=next(r for r in official if r['model_id']==m)
        deltas={k:abs(score[k]-float(row[k])) for k in score if k in row and k!='n_records'}
        checks.append({'model':m,'max_abs_delta':max(deltas.values()),'n':len(records)})
        recalc.append({'method':m,'status':'AUTHOR_PREDICTION_METRIC_RECALCULATION','denominator':'available eligible responses',**score})
        complete=records+[{'sample_id':q['sample_id'],'ground_truth':q['official_technique_labels'],'predictions':[]} for q in queries if q['sample_id'] not in response_sets[m]]
        recalc.append({'method':m,'status':'AUTHOR_PREDICTION_METRIC_RECALCULATION','denominator':'all eligible queries; missing=zero',**summarize(complete,universe,official_compat=True)})
        prediction_counts.append({'model':m,'available':len(records),'expected':len(queries),'missing':len(queries)-len(records),**raw_diagnostics[m]})
    csvout('OFFICIAL_METRIC_RECALCULATION.csv',recalc);csvout('OFFICIAL_PREDICTION_COUNTS.csv',prediction_counts);dump('results/evaluator_deltas.json',checks)
    if any(r['max_abs_delta']>1e-12 for r in checks):raise ValueError('Evaluator mismatch')
    csvout('datasets/manifests/input_leakage.csv',line_audit)
    results=[];all_predictions=[];runtimes=[]
    def execute(name,runner,view,knowledge):
        begin=time.perf_counter();preds=[]
        # The predictor receives a text-only projection, never the reference objects.
        inputs=[{'sample_id':q['sample_id'],'text':q['strict_log_content'] if view=='strict' else q['visible_log_content']} for q in queries]
        family = 'Random' if name.startswith('Random_') else ('KnowHow' if name.startswith('KnowHow') else name.split('_')[0])
        envname={'Random':'RandomRanking','Lexical':'LexicalTechniqueMatching','TFIDF':'TFIDFTechniqueRetrieval','BM25':'BM25TechniqueRetrieval','KnowHow':'KnowHow'}[family]
        outpath=ROOT/'experiments'/(name+'_'+view+'.jsonl')
        inputpath=ROOT/'datasets'/('prediction_view_'+view+'.jsonl')
        docpath=ROOT/'datasets'/('extended_knowledge_documents.json' if 'K16_1' in name else 'official_knowledge_documents.json')
        cmd=[str(ROOT/'venvs'/envname/'bin/python'),str(ROOT/'baselines/predict.py'),'--method',family,'--inputs',str(inputpath),'--documents',str(docpath),'--output',str(outpath)]
        if family=='Random':cmd+=['--seed',name.split('seed')[1]]
        if family=='KnowHow':cmd+=['--dictionary',str(ROOT.parent/'research3_baseline_reproduction01/algorithms/KnowHow/original_source/tech_dic.txt')]
        inference=subprocess.run(cmd,capture_output=True,text=True)
        dump('experiments/'+name+'_'+view+'_receipt.json',{'command':cmd,'exit_code':inference.returncode,'stdout':inference.stdout,'stderr':inference.stderr,'seconds':time.perf_counter()-begin})
        if inference.returncode:raise RuntimeError(name+' predictor failed')
        preds=[{**json.loads(line),'method':name,'input_view':view,'knowledge':knowledge} for line in outpath.read_text().splitlines()]
        byid={r['sample_id']:r['predictions'] for r in preds}
        records=[{'sample_id':q['sample_id'],'ground_truth':q['official_technique_labels'],'predictions':byid[q['sample_id']]} for q in queries]
        results.append({'method':name,'input_view':view,'knowledge':knowledge,'status':'PROJECT_NEW_OFFLINE_INFERENCE',**summarize(records,universe)})
        all_predictions.extend(preds);runtimes.append({'method':name,'view':view,'knowledge':knowledge,'seconds':time.perf_counter()-begin,'n':len(inputs)})
        return records
    for seed in [13,42,2026,2718,31415]:
        rng=random.Random(seed);execute('Random_seed'+str(seed),lambda text:rng.sample(universe,10),'official','fixed candidate IDs only')
    retrieval=Retriever(docs)
    for view in ['official','strict']:
        for method in ['Lexical','TFIDF','BM25']:
            execute(method,lambda text,m=method:retrieval.rank(text,m),view,'official_names_subnames_tactics')
    # Frozen local description extension: candidate universe unchanged; no modern replacement of author knowledge.
    stixpath=ROOT.parent/'provenance_baserepro_04/data/enterprise-attack-16.1.json.gz'
    stix=json.load(gzip.open(stixpath,'rt'));extended=dict(docs);mapped=Counter();revoked=Counter()
    for obj in stix['objects']:
        if obj.get('type')!='attack-pattern':continue
        ids=[x.get('external_id','') for x in obj.get('external_references',[]) if x.get('source_name')=='mitre-attack']
        for key in ids:
            parent=normalize_technique_id(key)
            if parent not in extended:continue
            if obj.get('revoked') or obj.get('x_mitre_deprecated'):
                revoked[parent]+=1;continue
            extended[parent]+=' '+obj.get('name','')+' '+obj.get('description','');mapped[parent]+=1
    dump('datasets/extended_knowledge_documents.json',extended)
    dump('ATTACK_KNOWLEDGE_VERSION.json',{'official_commit':json.loads((SRC/'commit.json').read_text())['sha'],'official_matrix_sha256':sha(SRC/'mitre_matrix.json'),'raw_ids':len(matrix),'parent_candidates':len(universe),'official_release_version':'not encoded in matrix; cannot certify exact ATT&CK release','descriptions_in_official_matrix':False,'extension_source':str(stixpath),'extension_sha256':sha(stixpath),'extension_version':'16.1 (existing filename/provenance)','extended_parents':len(mapped),'no_extension_parents':sorted(set(universe)-set(mapped)),'extension_is_not_author_original_knowledge':True})
    retrieval_ext=Retriever(extended)
    for method in ['Lexical','TFIDF','BM25']:
        execute(method+'_K16_1',lambda text,m=method:retrieval_ext.rank(text,m),'strict','MITRE16.1_description_extension')
    # Safe KnowHow dictionary adaptation, no executing upstream eval or scripts/log commands.
    kp=ROOT.parent/'research3_baseline_reproduction01/algorithms/KnowHow/original_source/tech_dic.txt'
    kd=ast.literal_eval(kp.read_text());phrases=defaultdict(list)
    for key,value in kd.items():
        parent=normalize_technique_id(key)
        if parent not in universe:continue
        if isinstance(value,list):phrases[parent].extend(x.lower() for x in value if isinstance(x,str) and x)
    dump('manifests/KNOWHOW_ADAPTATION.json',{'source':str(kp),'sha256':sha(kp),'parents_covered':len(phrases),'phrase_count':sum(map(len,phrases.values())),'adaptation':'count phrase substrings over unified strict raw text; parent merge; top10; ascending ID ties; not official KnowHow score or full model'})
    if phrases:
        def knowhow(text):
            text=text.lower()
            return sorted(universe,key=lambda k:(-sum(x in text for x in phrases[k]),k))[:10]
        execute('KnowHowDictionaryAdaptation',knowhow,'strict','existing official dictionary; project ranking adaptation')
    csvout('BASELINE_RESULTS_P0.csv',results);jsonl('BASELINE_PREDICTIONS.jsonl',all_predictions);csvout('results/runtimes.csv',runtimes)
    # Diagnostic intentionally uses only metadata, labels remain evaluator-only.
    meta=[]
    for q in queries:
        text=q['simulation_id']+' '+q['step_id'];pred=retrieval.rank(text,'BM25')
        meta.append({'ground_truth':q['official_technique_labels'],'predictions':pred})
    csvout('METADATA_ONLY_DIAGNOSTIC.csv',[{'method':'BM25_metadata_only','interpretation':'diagnostic only; not label-key oracle',**summarize(meta,universe)}])
    # Per-technique and observability summaries; inspection is descriptive, no method tuning.
    predindex={(r['method'],r['input_view'],r['sample_id']):r['predictions'] for r in all_predictions}
    err=[];strata=[]
    for method in ['TFIDF_K16_1','BM25_K16_1']:
        for technique in sorted({t for q in queries for t in q['normalized_technique_labels']}):
            qs=[q for q in queries if technique in q['normalized_technique_labels']]
            err.append({'method':method,'technique':technique,'n_records':len(qs),'n_steps':len({(q['scenario_id'],q['step_id']) for q in qs}),'label_recall_at_10':sum(technique in predindex[(method,'strict',q['sample_id'])] for q in qs)/len(qs)})
        for group,qs in [('single_gold',[q for q in queries if len(q['normalized_technique_labels'])==1]),('multi_gold',[q for q in queries if len(q['normalized_technique_labels'])>1]),('audit_source',[q for q in queries if any('audit' in s for s in q['log_source_ids'])]),('no_audit_source',[q for q in queries if not any('audit' in s for s in q['log_source_ids'])])]:
            if qs:strata.append({'method':method,'group':group,**summarize([{'ground_truth':q['official_technique_labels'],'predictions':predindex[(method,'strict',q['sample_id'])]} for q in qs],universe)})
    csvout('results/per_technique_errors.csv',err);csvout('results/observable_strata.csv',strata)
    # Grouping is fixed before development. Entire public P0 remains descriptive benchmark.
    split={'P0':{'type':'public zero-shot evaluation','sample_ids':[q['sample_id'] for q in queries]},'METHOD_DEV':{'scenarios':['7'],'sample_ids':[q['sample_id'] for q in queries if q['scenario_id']=='7']},'METHOD_TEST_LOCKED_FOR_TUNING':{'scenarios':['1','2','3','4','5','6'],'sample_ids':[q['sample_id'] for q in queries if q['scenario_id']!='7']},'warning':'No supervised training split; P0 result tables are public descriptive baselines, not unseen test proof.'}
    dump('DATASET_SPLITS.json',split)
    # Fixed first mechanism: descriptions vs names, analyzed on predeclared development scenario only.
    dev=[q for q in queries if q['scenario_id']=='7'];devresults=[]
    for m in ['BM25','BM25_K16_1','TFIDF','TFIDF_K16_1']:
        devresults.append({'method':m,'split':'scenario7_dev','view':'strict',**summarize([{'ground_truth':q['official_technique_labels'],'predictions':predindex[(m,'strict',q['sample_id'])]} for q in dev],universe)})
    csvout('METHOD_DEV_EXPERIMENTS.csv',devresults);csvout('METHOD_ABLATION_RESULTS.csv',devresults)
    # Counts and immutable provenance
    labelcounts=Counter(t for q in queries for t in q['normalized_technique_labels'])
    csvout('OFFICIAL_SAMPLE_LABEL_COUNTS.csv',[{'technique':t,'sample_count':n,'step_count':len({(q['scenario_id'],q['step_id']) for q in queries if t in q['normalized_technique_labels']})} for t,n in sorted(labelcounts.items())])
    prompt_hashes=Counter(q['source_hash'] for q in queries)
    summary={'eligible_queries':len(queries),'unique_scenario_steps':len(counts),'selected_simulations':len({q['simulation_id'] for q in queries}),'scenarios':len({q['scenario_id'] for q in queries}),'parent_gold_classes':len(labelcounts),'raw_gold_classes':len({t for q in queries for t in q['official_technique_labels']}),'multi_label_records':sum(len(q['normalized_technique_labels'])>1 for q in queries),'multi_label_steps':len({(q['scenario_id'],q['step_id']) for q in queries if len(q['normalized_technique_labels'])>1}),'missing_labels':len(bad),'query_label_disagreements':len(mismatches),'empty_log_samples':sum(q['log_line_count']==0 for q in queries),'distinct_prompts':len(prompt_hashes),'duplicate_records_beyond_first':sum(n-1 for n in prompt_hashes.values()),'excluded_queries':15,'excluded_steps':3,'history_records_eligible':sum(map(len,hist.values())),'direct_id_occurrences':sum(x['direct_ids'] for x in line_audit),'strict_changed_records':sum(x['strict_changed'] for x in line_audit),'elapsed_seconds':time.perf_counter()-started,'external_model_calls':0}
    dump('results/SUMMARY.json',summary)
    assets=[];commit=json.loads((SRC/'commit.json').read_text())['sha']
    for p in sorted(SRC.iterdir()):
        if p.is_file():assets.append({'local_path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'source_url':f'https://github.com/ait-aecid/attack-manifestations-interpretation/blob/{commit}/{p.name}' if p.suffix in ['.py','.json','.md'] and p.name not in ['zenodo_v2.json','commit.json','repo_metadata.json'] else 'see DATA_ACQUISITION_LOG.md','git_commit':commit,'method':'HTTPS public download; pinned source files'})
    archive=ROOT.parent/'rp3_existing_data/cam_lds_zenodo_v2/manifestations_filtered.zip'
    assets.append({'local_path':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),'source_url':'https://zenodo.org/records/18861762','method':'existing local archive reused; no member bodies accessed'})
    dump('OFFICIAL_DATA_MANIFEST.json',assets)
    print(json.dumps(summary,indent=2));print('BASELINES',[(r['method'],r['input_view'],round(r['top1_accuracy'],4),round(r['top10_accuracy'],4)) for r in results])
if __name__=='__main__':main()
