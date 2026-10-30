"""Independent mechanical validation of gate deliverables and read-only scope."""
import ast
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parents[1]
B = R.parent
V = B / 'research3_open_vocab_384_case_blind_review01'
A = B / 'research3_domain_adaptive_contrastive_learning01'


def load(p):
    return json.loads(Path(p).read_text())


def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def rows(p):
    with Path(p).open(newline='') as f:
        return list(csv.DictReader(f))


def main():
    details = []

    def check(name, result):
        details.append({'check': name, 'passed': bool(result)})

    inventory = rows(R / 'ASSET_INVENTORY.csv')
    baselines = rows(R / 'EXISTING_BASELINE_AUDIT.csv')
    cases = rows(R / 'CASE_QUALIFICATION_MATRIX.csv')
    source_reviews = [json.loads(s) for s in (V / 'review/QUERY_EVIDENCE_REVIEWS.jsonl').read_text().splitlines()]
    source_byid = {x['sample_id']: x for x in source_reviews}
    author = {x['sample_id']: x for x in map(json.loads, (A / 'data/P0_REFERENCE.jsonl').read_text().splitlines())}
    inputs = {x['sample_id']: x for x in map(json.loads, (A / 'data/P0_INPUTS.jsonl').read_text().splitlines())}
    counts = load(R / 'audit/CASE_QUALIFICATION_COUNTS.json')
    snapshot = load(R / 'audit/INPUT_HASH_SNAPSHOT.json')
    audit = load(R / 'audit/ASSET_AUDIT_SUMMARY.json')
    register = load(R / 'METHOD_HYPOTHESIS_REGISTER.json')
    manifest = load(R / 'RUN_MANIFEST.json')

    missing = []
    changed = []
    for x in inventory:
        p = Path(x['path'])
        if not p.is_file():
            missing.append(x['path'])
        else:
            check('asset_current_hash:' + x['artifact_id'], sha(p) == x['sha256'])
    for x in snapshot['files']:
        p = Path(x['path'])
        if not p.is_file() or sha(p) != x['sha256']:
            changed.append(x['path'])
    check('no checked old files changed', not changed)
    check('asset inventory and source snapshot counts', len(inventory) == audit['assets_checked'] == len(snapshot['files']) and not missing)
    mismatches = [x for x in inventory if x['legacy_hash_status'] == 'MISMATCH']
    previous = load(V / 'results/OLD_ASSET_INTEGRITY_AUDIT.json')
    preexisting = {x['path']: x for g in previous['legacy_manifest_comparisons'] for x in g['mismatches']}
    check('legacy mismatches match documented earlier exception exactly', len(mismatches) == 1 and all(
        x['path'] in preexisting and x['sha256'] == preexisting[x['path']]['current_sha256'] and
        x['expected_sha256'] == preexisting[x['path']]['legacy_expected_sha256'] for x in mismatches))
    check('complete384 in exact frozen order without duplicates', len(cases) == len({x['sample_id'] for x in cases}) == 384 and
          [x['sample_id'] for x in cases] == [x['sample_id'] for x in source_reviews])
    allowed = {'CANDIDATE_FOR_HUMAN_ADJUDICATION', 'OBSERVATION_INSUFFICIENT', 'LABEL_SCOPE_UNRESOLVED',
               'REFERENCE_MISSING', 'NOT_ELIGIBLE_FOR_CURRENT_HYPOTHESIS'}
    for x in cases:
        old = source_byid[x['sample_id']]
        check(x['sample_id'] + ':source identity and Gold scope',
              x['logical_step_id'] == old['logical_step_id'] and x['scenario_id'] == old['scenario_id'] and
              x['input_view_hash'] == old['input_view_hash'] == inputs[x['sample_id']]['input_hash'] and
              json.loads(x['gold_technique_ids']) == old['gold_technique_ids'] and
              set(old['gold_technique_ids']) <= set(author[x['sample_id']]['gold_technique_ids']))
        check(x['sample_id'] + ':AI not promoted to human Gold',
              x['AI_review_status'] == 'AI_PRE_REVIEW_NOT_GOLD' and
              x['source_AI_status_literal'] == 'AI_BLIND_PRE_REVIEW_NOT_GOLD' and
              x['observable_evidence_status'] == 'INHERITED_AI_' + old['overall_evidence_assessment'] and
              x['independent_reference_status'] == 'INDEPENDENT_SEMANTIC_REFERENCE_NOT_AVAILABLE' and
              x['blinding_status'] == 'PREDICTION_BLINDING_NOT_ENFORCED' and
              x['new_semantic_review_performed'] == 'False')
        check(x['sample_id'] + ':unknown distinction not zero;no test fabrication',
              x['distinguishing_evidence_status'] == 'NOT_AVAILABLE_NO_INDEPENDENT_PAIRWISE_ADJUDICATION' and
              x['independent_test_status'] == 'INDEPENDENT_TEST_NOT_AVAILABLE')
        check(x['sample_id'] + ':no automatic eligibility from AI',
              x['eligible_for_primary_metric'] == 'False' and x['human_adjudication_required'] == 'True' and
              x['primary_blocker'] in allowed and bool(x['blocker_reason']) and
              set(json.loads(x['qualification_states'])) <= allowed)
    check('counts preserve units and missing-reference unknowns',
          counts['original_queries'] == 384 and counts['logical_steps'] == 80 and
          counts['query_target_Gold_assignments'] == 520 and counts['inherited_condition_records'] == 2618 and
          counts['queries_with_qualified_candidate_distinction'] == 'NOT_AVAILABLE' and
          counts['actual_queries_with_qualified_independent_reference'] == 'NOT_AVAILABLE' and
          counts['actual_queries_with_independent_test_qualification'] == 'NOT_AVAILABLE')
    check('primary blockers reproducible', dict(Counter(x['primary_blocker'] for x in cases)) == counts['primary_blocker_counts_exclusive'])
    check('direct AI clues remain ineligible', sum(x['any_target_direct_AI_clue'] == 'True' for x in cases) == 31 and all(x['eligible_for_primary_metric'] == 'False' for x in cases if x['any_target_direct_AI_clue'] == 'True'))
    check('baseline conditions preserved', len(baselines) == audit['baseline_audit_rows'] and len({x['baseline_id'] for x in baselines}) == len(baselines) and
          sum(x['baseline_id'].startswith('LEXICAL_CONDITION_') for x in baselines) == 100 and
          sum(x['baseline_id'].startswith('OPEN_') for x in baselines) == 11 and
          sum(x['baseline_id'].startswith('VALIDATION02_') for x in baselines) == 14)
    methods = {x['method'] for x in baselines}
    check('strong baselines not reduced to weak lexical only', {'BM25', 'CharacterNgramTFIDF', 'TFIDF', 'WordCharacterHybrid',
          'Z0', 'S0', 'C4', 'C3', 'C0', 'M0_MATCHED_E1_NATIVE_PREFIX'} <= methods)
    for x in baselines:
        check(x['baseline_id'] + ':no historical score presented as new result', x['new_experiment_result'] == 'False')
        for key in ['input_asset', 'knowledge_asset', 'source_asset', 'prediction_asset']:
            value = x[key]
            if value.startswith('/'):
                check(x['baseline_id'] + ':' + key + ':exists', Path(value).is_file())
    check('current real-model milestones supersede old blocked ones', (R / 'audit/BASELINE_STATUS_SUPERSESSION.json').is_file())
    check('saved exports valid without model execution', audit['prediction_export_schema_invalid_rows'] == 0 and
          audit['referenced_source_checkpoints_hash_only'] == 126 and audit['checkpoint_deserialization_or_execution'] is False)
    parity = audit['input_parity']
    check('parity limitations explicit,not a fair-comparison claim', parity['query_id_sets_equal'] is True and parity['candidate_ids_equal'] is True and
          parity['identical_query_texts'] == 30 and parity['identical_knowledge_documents'] == 41 and
          parity['comparison_status'] == 'HISTORICAL_INPUT_BUDGET_PARITY_NOT_ESTABLISHED_NO_REINFERENCE')
    h = register['primary_hypothesis']
    required_h = ['hypothesis_id', 'hypothesis_statement', 'mechanism', 'expected_effect', 'expected_failure_modes',
                  'strongest_baselines', 'required_reference', 'required_inputs', 'primary_metric', 'secondary_metrics',
                  'falsification_criterion', 'current_evidence', 'missing_evidence', 'go_no_go_status']
    check('one populated conditional hypothesis,not admitted', register['primary_hypothesis_count'] == 1 and
          all(h.get(k) for k in required_h) and h['admission_status'] == 'NOT_ADMITTED_CONDITIONAL_DESIGN_ONLY' and
          register['method_experiment_admitted'] is False and register['new_method_implemented'] is False)
    check('single reference-first decision consistent', register['final_decision'] == manifest['final_decision'] == h['go_no_go_status'] == 'GO_AFTER_REFERENCE_QUALIFICATION')
    check('no current method experiment or resource execution claimed', register['experiment_executed'] is False and
          manifest['experiment_executed'] is False and manifest['new_model_calls'] == manifest['new_agent_calls'] == manifest['new_training_runs'] == manifest['downloads'] == manifest['GPU_tasks'] == 0 and
          manifest['server_access'] is False and manifest['external_network_access'] is False)
    root_required = ['METHOD_HYPOTHESIS_GATE_REPORT.md', 'ASSET_INVENTORY.csv', 'EXISTING_BASELINE_AUDIT.csv',
                     'CASE_QUALIFICATION_MATRIX.csv', 'REFERENCE_REQUIREMENTS.md', 'METHOD_HYPOTHESIS_REGISTER.json',
                     'MINIMAL_EXPERIMENT_PROTOCOL.md', 'GO_NO_GO_DECISION.md', 'RUN_MANIFEST.json', 'FINAL_VALIDATION.json']
    presence = {n: (R / n).is_file() and (R / n).stat().st_size > 60 for n in root_required if n != 'FINAL_VALIDATION.json'}
    check('all nine other required populated artifacts exist', all(presence.values()))
    report = (R / 'METHOD_HYPOTHESIS_GATE_REPORT.md').read_text()
    reference = (R / 'REFERENCE_REQUIREMENTS.md').read_text()
    protocol = (R / 'MINIMAL_EXPERIMENT_PROTOCOL.md').read_text()
    check('report has ten substantive gate answers', all(f'## {i}.' in report for i in range(1, 11)))
    check('reference contract separates truth sources and independent humans', all(s in reference for s in ['作者标签', '可见行为', '人工语义充分性', '完整攻击目标', '第三位仲裁者', 'CONTRADICTED', 'NOT_ESTABLISHED', 'NOT_EVALUABLE']))
    check('protocol protects Unseen and Seen and records nonexecutable blockers', all(s in protocol for s in ['DESIGN_ONLY_NOT_EXECUTABLE', 'MRR@10', 'Top10', 'Seen', 'Unseen', '.005', '.02', '尚未选择、实现、验证或定版', '样本量']))
    parsed = {}
    for p in sorted(R.rglob('*')):
        if not p.is_file() or p.name in {'FINAL_VALIDATION.json', 'VALIDATION_CHECKS.json'}:
            continue
        if p.suffix == '.json':
            load(p)
            parsed[str(p.relative_to(R))] = 'JSON_OK'
        elif p.suffix == '.csv':
            z = rows(p)
            check(str(p.relative_to(R)) + ':complete CSV rows', all(None not in x for x in z))
            parsed[str(p.relative_to(R))] = len(z)
        elif p.suffix == '.py':
            tree = ast.parse(p.read_text())
            check(str(p.relative_to(R)) + ':no model/server runtime imports', not any(
                isinstance(n, ast.Import) and any(x.name.split('.')[0] in {'torch', 'transformers', 'paramiko', 'requests', 'subprocess'} for x in n.names) or
                isinstance(n, ast.ImportFrom) and (n.module or '').split('.')[0] in {'torch', 'transformers', 'paramiko', 'requests', 'subprocess'} for n in ast.walk(tree)))
            parsed[str(p.relative_to(R))] = 'AST_OK_NOT_OLD_CODE_EXECUTION'
    failed = [x['check'] for x in details if not x['passed']]
    (R / 'audit/VALIDATION_CHECKS.json').write_text(json.dumps(details, ensure_ascii=False, indent=2) + '\n')
    result = {
        'status': 'PASS_METHOD_GATE_WITH_DOCUMENTED_BLOCKERS' if not failed else 'FAIL_GATE_VALIDATION',
        'execution_status': 'COMPLETED_METHOD_GATE' if not failed else 'PARTIAL_WITH_BLOCKERS',
        'validation_scope': 'independent deterministic file/schema/qualification/decision audit;not independent semantic Gold or proof of algorithm efficacy',
        'assets_checked': len(inventory), 'missing_assets': missing,
        'hash_mismatches': [{k: x[k] for k in ['path', 'expected_sha256', 'sha256', 'qualification']} for x in mismatches],
        'hash_mismatch_interpretation': 'documented pre-existing report drift;not silently repaired or reported as all legacy versions matching',
        'baseline_qualification': {'registered_audit_rows': len(baselines), 'saved_main_schema_invalid_rows': audit['prediction_export_schema_invalid_rows'],
            'selected_native_lexical_prediction_conditions_checked': 2, 'fair_confirmatory_comparison_ready': False,
            'query_text_parity': '30/975', 'knowledge_text_parity': '41/216',
            'earlier_model_blocked_status_not_used_as_current_absence': True},
        'reference_status': 'INDEPENDENT_SEMANTIC_REFERENCE_NOT_AVAILABLE',
        'independent_test_status': 'INDEPENDENT_TEST_NOT_AVAILABLE',
        'hypothesis_registered': True, 'hypothesis_id': h['hypothesis_id'],
        'hypothesis_admission_status': h['admission_status'],
        'experiment_executed': False, 'new_model_calls': 0, 'new_agent_calls': 0, 'new_training_runs': 0,
        'downloads': 0, 'GPU_tasks': 0, 'server_access': False, 'network_access': False,
        'old_files_modified': len(changed), 'old_modified_paths': changed,
        'old_integrity_scope': 'all checked snapshot assets;no old checkpoint or script was loaded/executed;all write tools targeted new run directory',
        'required_artifacts_present': presence,
        'final_decision': register['final_decision'], 'case_counts': counts,
        'check_count': len(details), 'failed_check_count': len(failed), 'failed_checks': failed,
        'parsed_artifacts': parsed,
        'limitations': ['attachment ends7.1;message begins8;intervening rules not provided',
            'one pre-existing legacy report hash mismatch',
            '384 AI pre-reviews not independent human Gold;no new semantic review',
            'independent distinguishing and behavior countsNOT_AVAILABLE;documented qualified records0 does not prove global absence',
            'all materials inspected are exposed development or related pilot;not independent test',
            'not all lexical conditions had native predictions individually revalidated;full saved conditions retained',
            'conditional verifier not implemented/frozen;sample-size justification unavailable;protocol not executable',
            'new algorithm/literature novelty unconfirmed;reference-first decision not method authorization'],
        'delivery_hash_seal': 'performed separately by finalize_gate.py after this audit;manifest self-hash excluded conventionally'}
    path = R / 'FINAL_VALIDATION.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    result['required_artifacts_present']['FINAL_VALIDATION.json'] = path.is_file() and path.stat().st_size > 60
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['status', 'assets_checked', 'old_files_modified', 'check_count', 'failed_check_count', 'final_decision', 'experiment_executed']}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
