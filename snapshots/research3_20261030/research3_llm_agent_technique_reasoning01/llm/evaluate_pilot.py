"""Post-hoc frozen-evaluator scoring only. No inference/API/policy modifications.
V2_PRIMARY denotes the post-repair post-hoc delivery audit scope, registered
after V1 interruption; it is not preregistered or confirmatory validation.
"""
from __future__ import annotations
import csv
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'research3_technique_strong_baselines_generalization02'
METRICS=['top1_accuracy','top5_accuracy','top10_accuracy','precision_at_1','precision_at_5','precision_at_10',
         'recall_at_1','recall_at_5','recall_at_10','mrr','micro_f1_at_5','macro_f1_at_5_all_candidates','macro_f1_at_5_gold_present']

def load(path):
    if not path.exists():return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]

def write(name,rows):
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with (ROOT/name).open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=keys);out.writeheader();out.writerows(rows)

def main():
    # Predictions must already exist before reference access. Never fed back to models.
    v2=load(ROOT/'LLM_TECHNIQUE_PREDICTIONS.jsonl')
    v1=load(ROOT/'experiments/PILOT_V1_INVALID_AGENT/LLM_TECHNIQUE_PREDICTIONS.jsonl')
    reg=json.loads((ROOT/'manifests/EXPERIMENT_REGISTRATION_V2.json').read_text())
    expected={(x['sample_id'],m) for x in reg['primary_episodes'] for m in reg['primary_conditions']}
    assert {(x['sample_id'],x['method']) for x in v2}==expected and len(v2)==len(expected)
    refs={x['sample_id']:x for x in load(OLD/'datasets/p2_v2/reference_sampled.jsonl')}
    universe=list(json.loads((OLD/'knowledge/K2_DESCRIPTION_16_1.json').read_text()))
    spec=importlib.util.spec_from_file_location('frozen_eval',OLD/'frozen_p0/evaluate_techniques.py')
    evaluator=importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluator)

    def status(row):
        value=row.get('execution_status','FAILED' if row.get('failure') else 'COMPLETED')
        # No inference was initiated when budget precluded it; do not score as model failure.
        return value
    def scoreable(row):return status(row) in {'COMPLETED','FAILED','INCOMPLETE_BUDGET','INTERRUPTED'} and row.get('model_calls',0)>0
    def records(rows):
        return [{'ground_truth':refs[x['sample_id']]['ground_truth'],
                 'predictions':x.get('predictions',[]) if status(x)=='COMPLETED' else []} for x in rows]
    def metrics(rows):
        if not rows:return {k:'N/A' for k in METRICS}
        z=evaluator.summarize(records(rows),universe=universe)
        return {k:z.get(k,0.0) for k in METRICS}
    def groups(rows,kind):
        g=defaultdict(list)
        for x in rows:
            r=refs[x['sample_id']]
            key={'QUERY':x['sample_id'],'LOGICAL_STEP':r['logical_step_id'],'SCENARIO':str(r['scenario_id']),
                 'EXECUTION':str(r['simulation_id']),'SCENARIO_EXECUTION':str(r['scenario_id'])+'|'+str(r['simulation_id'])}[kind]
            g[key].append(x)
        return g

    result=[];grouped=[];errors=[];costs=[];agent=[]
    sets=[('V2_PRIMARY_RESOURCE_LIMITED',v2,len(reg['primary_episodes'])),('V1_EXPLORATORY_NONADAPTIVE',v1,14)]
    for protocol,rows,planned in sets:
        for method in sorted({x['method'] for x in rows}):
            rr=[x for x in rows if x['method']==method]
            invalid=protocol.startswith('V1') and method.startswith('ADAPTIVE')
            executed=[x for x in rr if scoreable(x)]
            eligible=[] if invalid else executed
            failures=sum(status(x)=='FAILED' for x in executed)
            base={'protocol':protocol,'method':method,'qualification':'INVALID_TOOL_RESULT_FORWARDING' if invalid else 'RELATED_DEVELOPMENT_PILOT_ONLY',
                  'model_id':rr[0]['model_id'],'N_planned':planned,'N_executed':len(executed),'N_completed':sum(status(x)=='COMPLETED' for x in executed),
                  'N_failed':failures,'N_incomplete_budget':sum(status(x)=='INCOMPLETE_BUDGET' for x in executed),
                  'N_not_executed':planned-len(executed),'N_scored':len(eligible),'failure_denominator_policy':'called failures empty; never-called excluded',
                  'inference_scope':'cached original inference reused' if protocol.startswith('V2') else 'original V1 local inference'}
            query={**base,'analysis_unit':'QUERY_EXECUTED',**metrics(eligible)}
            result.append(query)
            if method.startswith('ADAPTIVE'):agent.append(query)
            stepgroups=groups(eligible,'LOGICAL_STEP')
            macro={k:sum(metrics(g)[k] for g in stepgroups.values())/len(stepgroups) if stepgroups else 'N/A' for k in METRICS}
            result.append({**base,'analysis_unit':'LOGICAL_STEP_MACRO','N_groups':len(stepgroups),**macro})
            for kind in ['QUERY','LOGICAL_STEP','SCENARIO','EXECUTION','SCENARIO_EXECUTION']:
                for gid,g in groups(eligible,kind).items():
                    grouped.append({'protocol':protocol,'method':method,'group_type':kind,'group_id':gid,'n_executed':len(g),**metrics(g)})
            for x in rr:
                ref=refs[x['sample_id']];eligible_row=scoreable(x) and not invalid
                pred=x.get('predictions',[]) if status(x)=='COMPLETED' else []
                gold=set(ref['ground_truth']);candidates=x.get('initial_candidate_top100',[])
                # KNOWLEDGE20 supplies partial top20 knowledge but still permits all216 IDs.
                # Missing Gold from those descriptions is not a hard candidate retrieval failure.
                n=20 if method=='RETRIEVAL20' else 50 if method=='RETRIEVAL50' else 100 if method=='RETRIEVAL100' else 216
                has_gold=bool(gold&set(candidates[:n])) if n<216 else True
                hit=bool(gold&set(pred[:10]))
                attribution='INVALID_TOOL_RESULT_FORWARDING' if invalid else 'NOT_EXECUTED_BUDGET' if not scoreable(x) else 'OUTPUT_FORMAT_OR_CALL_FAILURE' if status(x)=='FAILED' else 'CORRECT_TOP10' if hit else 'RETRIEVAL_FAILURE' if not has_gold else 'UNRESOLVED'
                errors.append({'protocol':protocol,'method':method,'sample_id':x['sample_id'],'scenario_id':ref['scenario_id'],
                    'simulation_id':ref['simulation_id'],'logical_step_id':ref['logical_step_id'],'execution_status':status(x),
                    'qualification':base['qualification'],'scored':eligible_row,'ground_truth':json.dumps(ref['ground_truth']),
                    'predictions_used':json.dumps(pred) if eligible_row else 'N/A','error_source':attribution,
                    'candidate_hit':has_gold,'knowledge_top20_gold_covered':bool(gold&set(candidates[:20])) if method=='KNOWLEDGE20' else 'N/A',
                    'raw_errors':json.dumps(x.get('errors',[])),**metrics([x] if eligible_row else [])})
            def known_sum(key,subset=rr):
                known=[x[key] for x in subset if isinstance(x.get(key),(int,float))]
                return sum(known) if known else 'N/A'
            costs.append({**base,'analysis_unit':'CONDITION_COST','model_call_attempts':sum(x.get('model_calls',0) for x in rr),
                'new_V2_call_attempts':sum(x.get('new_model_call_attempts',0) for x in rr) if protocol.startswith('V2') else 'N/A',
                'cache_reused_conditions':sum(bool(x.get('cache_reused')) for x in rr),
                'actual_API_prompt_tokens_known_sum':known_sum('model_prompt_tokens'),
                'actual_API_output_tokens_known_sum':known_sum('model_output_tokens'),
                'actual_API_token_unknown_executed_conditions':sum(x.get('model_prompt_tokens') is None or x.get('model_output_tokens') is None for x in executed),
                'model_seconds_known_sum':known_sum('model_seconds'),'model_seconds_unknown_executed_conditions':sum(x.get('model_seconds') is None for x in executed),
                'current_pass_wall_seconds':known_sum('wall_seconds'),
                'cached_original_cost_included':'YES_DO_NOT_ADD_V1_AND_V2' if protocol.startswith('V2') else 'ORIGINAL_COST',
                'rendered_log_regex_proxy_tokens_sum':sum(x.get('rendered_log_proxy_tokens',0) for x in executed),
                'visible_added_regex_proxy_tokens_sum':sum(x.get('visible_additional_text_proxy_tokens',0) for x in executed),
                'environment_returned_regex_proxy_tokens_sum':sum(x.get('cost',{}).get('returned_log_proxy_tokens',0) for x in executed),
                'cost_units_note':'API counts vs regex proxy distinct; unknown is N/A, cache reuse is not new inference; invalid adaptive costs remain actual costs'})

    # Strict matched executed intersection, never substitute unexecuted model runs.
    by={m:{x['sample_id']:x for x in v2 if x['method']==m and scoreable(x)} for m in ['STATIC_EVIDENCE_S','ADAPTIVE_AGENT_S']}
    shared=sorted(set(by['STATIC_EVIDENCE_S'])&set(by['ADAPTIVE_AGENT_S']))
    a=metrics([by['ADAPTIVE_AGENT_S'][x] for x in shared]);s=metrics([by['STATIC_EVIDENCE_S'][x] for x in shared])
    delta={k:a[k]-s[k] if shared else 'N/A' for k in METRICS}
    agent.append({'protocol':'V2_PRIMARY_RESOURCE_LIMITED','method':'ADAPTIVE_MINUS_STATIC_STRICT_MATCHED','analysis_unit':'MATCHED_EXECUTED_POINT_DIFFERENCE',
                  'qualification':'NO_VALID_AGENT_EXECUTED' if not shared else 'DEVELOPMENT_POINT_ESTIMATE_NO_SIGNIFICANCE',
                  'N_planned':len(reg['primary_episodes']),'N_executed':len(shared),'N_failed':'N/A','N_not_executed':len(reg['primary_episodes'])-len(shared),
                  'N_scored':len(shared),'matched_sample_ids':json.dumps(shared),**delta})
    # Actual unique native receipts: avoids double-counting cached V1 responses in V2 totals.
    receipts=list((ROOT/'experiments').glob('PILOT_*.json'))
    native=[]
    for p in receipts:
        x=json.loads(p.read_text())
        if isinstance(x.get('response'),dict) and 'prompt_eval_count' in x['response']:native.append((p,x))
    costs.append({'protocol':'ALL_ORIGINAL_UNIQUE_NATIVE_RECEIPTS','method':'ALL_METHODS_INCLUDING_INVALID_V1_AGENT',
                  'analysis_unit':'DEDUP_NATIVE_RECEIPTS','N_executed':len(native),
                  'actual_API_prompt_tokens_known_sum':sum(x['response']['prompt_eval_count'] for _,x in native),
                  'actual_API_output_tokens_known_sum':sum(x['response'].get('eval_count',0) for _,x in native),
                  'model_seconds_known_sum':sum(x.get('wall_seconds',0) for _,x in native),
                  'cached_original_cost_included':'ONCE_PER_NATIVE_RECEIPT','cost_units_note':'Counts real completed API receipts; failed attempts lacking receipt cost unknown; includes protocol-invalid V1 inference cost'})
    interruption=json.loads((ROOT/'results/V1_INTERRUPTION.json').read_text())
    costs.append({'protocol':'INTERRUPTED_REQUEST_UNKNOWN_COST','method':'V1_IN_FLIGHT_REQUEST',
                  'analysis_unit':'REQUEST_ATTEMPT_UNCERTAINTY','model_call_attempts':'0..'+str(interruption['interrupted_request_count_upper_bound']),
                  'actual_API_prompt_tokens_known_sum':'N/A','actual_API_output_tokens_known_sum':'N/A',
                  'model_seconds_known_sum':'N/A','cost_units_note':'Upper bound from interrupted client; no native response, unknown tokens and service time are not zero; do not add as a completed response'})
    write('LLM_TECHNIQUE_RESULTS.csv',result);write('LLM_TOKEN_AND_RUNTIME_REPORT.csv',costs)
    write('AGENT_TECHNIQUE_RESULTS.csv',agent);write('results/LLM_GROUPED_RESULTS.csv',grouped);write('results/LLM_ERROR_DETAILS.csv',errors)
    print(json.dumps({'v2':[{k:x[k] for k in ['method','N_planned','N_executed','N_failed','N_not_executed','top1_accuracy','top10_accuracy','mrr']} for x in result if x['protocol'].startswith('V2') and x['analysis_unit']=='QUERY_EXECUTED'],
                      'strict_matched_agent_static_n':len(shared),'native_API_receipts':len(native)},indent=2))
if __name__=='__main__':main()
