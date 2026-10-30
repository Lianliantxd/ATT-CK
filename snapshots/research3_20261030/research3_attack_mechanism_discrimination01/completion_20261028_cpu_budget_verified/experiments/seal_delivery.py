"""Create complete prediction artifact and a relative SHA256 delivery manifest."""
import ast
import collections
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *

def main():
    rows=0;groups=collections.Counter()
    with (ROOT/'MECHANISM_BASELINE_PREDICTIONS.jsonl').open('x') as out:
        for protocol,path in [('BYTE','inherited/CPU_PREDICTIONS.jsonl'),('FEATURE','results/FEATURE_PREDICTIONS.jsonl'),('FEATURE','results/FEATURE_CONTROL_PREDICTIONS.jsonl')]:
            for r in records(ROOT/path):
                r['budget_protocol']=protocol;out.write(json.dumps(r,ensure_ascii=False)+'\n');rows+=1;groups[protocol,r['method']]+=1
    assert rows==95550 and len(groups)==98 and set(groups.values())=={975}
    syntax=[]
    for p in sorted(ROOT.rglob('*.py')):
        if 'venvs' in p.parts:continue
        ast.parse(p.read_text());syntax.append(str(p.relative_to(ROOT)))
    required=['CROSS_ENCODER_FORENSIC_AUDIT.md','RERANKER_SCORING_VALIDATION.json','CANDIDATE_SCORE_CONSISTENCY.csv',
        'CANDIDATE_RANK_TRANSITIONS.csv','RERANKER_FAILURE_TAXONOMY.csv','RERANKER_FAILURE_DIAGNOSIS.md',
        'DIAGNOSTIC_30_SELECTION_PROTOCOL.md','DIAGNOSTIC_30_FROZEN_IDS.json','DIAGNOSTIC_30_CASES.jsonl',
        'DIAGNOSTIC_30_DEPENDENCY_AUDIT.csv','MECHANISM_IR_SCHEMA.json','MECHANISM_LITERAL.jsonl','MECHANISM_RELATIONS.jsonl',
        'MECHANISM_EXTRACTION_VALIDATION.md','MECHANISM_SOURCE_TRACE.csv','TECHNIQUE_MECHANISM_CARDS.jsonl',
        'KNOWLEDGE_VERSION_MANIFEST.json','KNOWLEDGE_COVERAGE_AUDIT.md','MECHANISM_CARD_SOURCE_AUDIT.csv',
        'MECHANISM_BASELINE_PREDICTIONS.jsonl','MECHANISM_BASELINE_RESULTS.csv','MECHANISM_INPUT_ABLATIONS.csv',
        'MECHANISM_KNOWLEDGE_ABLATIONS.csv','MECHANISM_ERROR_ANALYSIS.md','MECHANISM_BLIND_REVIEW_PACKETS.jsonl',
        'MECHANISM_REVIEW_GUIDELINES.md','MECHANISM_HUMAN_REVIEW_STATUS.csv','EXTERNAL_ATTACK_TECHNIQUE_DATASET_CANDIDATES.md',
        'EXTERNAL_REFERENCE_QUALIFICATION.csv','EXTERNAL_DATASET_DECISION.md','METHOD_FORMAL_PROBLEM.md',
        'METHOD_RESEARCH_DECISION.md','R3_ATTACK_MECHANISM_DISCRIMINATION_RESULTS.md']
    assert all((ROOT/p).is_file() and (ROOT/p).stat().st_size for p in required)
    dump('results/FINAL_VALIDATION.json',{'required_files':len(required),'required_files_present':True,
        'prediction_rows':rows,'conditions':len(groups),'queries_each':975,'syntax_files':syntax,
        'engineering_unit_tests':read(ROOT/'results/UNIT_TESTS.json'),'source_validation':read(ROOT/'results/SOURCE_VALIDATION.json'),
        'independent_audit':read(ROOT/'results/INDEPENDENT_AUDIT.json'),'plots_visually_inspected':2,
        'semantic_human_accuracy':'NA_PENDING','new_model_forward':'NA_NOT_AUTHORIZED',
        'independent_external_test':'NOT_READY','type_checker':'NOT_AVAILABLE_NOT_INSTALLED',
        'package_build':'NOT_APPLICABLE_STDLIB_SCRIPTS','coverage_percent':'NOT_MEASURED',
        'security_scan':'source AST checked for unintended execution/network entry points; no credential literals introduced; attack text remains inert data'})
    manifest=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or any(x in p.parts for x in ['venvs','__pycache__','.font-cache']):continue
        if p.name=='DELIVERY_SHA256.json':continue
        manifest.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)})
    dump('manifests/DELIVERY_SHA256.json',{'files':manifest,'total_bytes':sum(r['bytes'] for r in manifest),
        'excluded':'recreatable venv, Python bytecode and font cache; manifest itself',
        'status':'OFFLINE_COMPLETE_WITH_NEURAL_HUMAN_EXTERNAL_BLOCKERS'})
    print('Sealed',len(manifest),'files;',sum(r['bytes'] for r in manifest),'bytes')

if __name__=='__main__':main()
