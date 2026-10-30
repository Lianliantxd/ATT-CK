"""Snapshot existing authorized sanitized P0 artifacts, leave all old files intact."""
import datetime
import json
import shutil
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import *

def main():
    sources={
        'frozen_inputs/BYTE_VIEWS.jsonl':BASE/'frozen_inputs/PREDICTION_INPUTS.jsonl',
        'frozen_inputs/LITERAL_EVENTS.jsonl':BASE/'MECHANISM_LITERAL.jsonl',
        'frozen_inputs/RELATIONS.jsonl':BASE/'MECHANISM_RELATIONS.jsonl',
        'frozen_inputs/KNOWLEDGE.json':BASE/'attack_knowledge/KNOWLEDGE_TEXTS.json',
        'inherited/CPU_PREDICTIONS.jsonl':BASE/'MECHANISM_BASELINE_PREDICTIONS.jsonl',
        'inherited/CPU_RECEIPT.json':BASE/'results/CPU_RUN_RECEIPT.json',
        'inherited/DIAGNOSTIC_30.json':BASE/'DIAGNOSTIC_30_FROZEN_IDS.json',
        'inherited/CARDS.jsonl':BASE/'TECHNIQUE_MECHANISM_CARDS.jsonl',
        'inherited/KNOWLEDGE_MANIFEST.json':BASE/'KNOWLEDGE_VERSION_MANIFEST.json',
        'inherited/RERANKER_VALIDATION.json':BASE/'RERANKER_SCORING_VALIDATION.json',
        'inherited/NEURAL_RERANKER.jsonl':PREVIOUS/'RERANKER_REAL_PREDICTIONS.jsonl',
        'inherited/NEURAL_EMBEDDING.jsonl':PREVIOUS/'EMBEDDING_REAL_PREDICTIONS.jsonl',
        'inherited/REFERENCE.jsonl':STRONG/'datasets/p0_reference.jsonl',
        'src/frozen_engine.py':STRONG/'baselines/engine.py',
        'src/frozen_evaluator.py':BENCH/'evaluate_techniques.py',
        'src/frozen_extractor.py':BASE/'mechanism_ir/extractor.py'}
    inherited=[]
    for target,p in sources.items():
        q=ROOT/target;q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists()
        before=sha(p);shutil.copyfile(p,q);assert sha(q)==before==sha(p)
        inherited.append({'source':str(p),'snapshot':target,'sha256':before,'bytes':q.stat().st_size})
    refs=list(records(ROOT/'inherited/REFERENCE.jsonl'));allowed={r['sample_id'] for r in refs}
    assert len(allowed)==len(refs)==975
    assert len({(r['scenario_id'],r['step_id']) for r in refs})==195
    assert not any(r['scenario_id']=='1' and str(r['step_id']) in ['35','36','37'] for r in refs)
    assert set(r['sample_id'] for r in records(ROOT/'frozen_inputs/BYTE_VIEWS.jsonl'))==allowed
    # Both previous view manifests certify exclusion before body parsing. No raw archive is opened here.
    dump('manifests/INPUT_SNAPSHOT.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':inherited,
        'allowed_P0_samples':975,'logical_steps':195,'restricted_steps_body_reads':0,
        'access':'existing sanitized allowlisted derived files only; no raw archives or alias copies',
        'new_model_forwards':0,'all_parent_predictions_unchanged':True,
        'completion_strategy':'isolated continuation because requested root already has partial artifacts; preserve concurrent work'})
    dump('manifests/FEATURE_BUDGET_PREREGISTRATION.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'input_scope':'same existing common P0 native fragments; further shared-prefix reduction only',
        'algorithms':['CHAR','BM25'],'views':['RAW','LITERAL','LITERAL_PLUS_RELATIONS','RAW_PLUS_LITERAL'],
        'knowledge':['K0_NAMES_ONLY','K2_DESCRIPTION_16_1','K3_WITHOUT_TITLES','MECHANISM_CARD','K2_PLUS_CARD'],
        'log_caps':{'actual_character_ngram_occurrences_3_4_5':2048,'actual_BM25_word_tokens':256},
        'document_caps':{'actual_character_ngram_occurrences_3_4_5':1024,'actual_BM25_word_tokens':128},
        'same_common_observations_across_all_views':True,'new_GTE_token_lengths':'NOT_MEASURED; feature units are not GTE tokens',
        'selection':'deterministic maximum feasible native prefix, no Gold or score input',
        'no_tuning':True,'knowledge_version':'frozen16.1 with216-candidate policy, all13 fallback retained',
        'claim_limit':'CPU fairness sensitivity only, not neural mechanism effect or independent generalization'})
    print('Copied',len(inherited),'immutable sanitized artifacts; registered feature budget before new predictions.')

if __name__=='__main__':main()
