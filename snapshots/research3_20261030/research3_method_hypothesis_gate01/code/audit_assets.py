"""Read-only asset/contract audit. No inference, training or semantic re-review."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]
B = R.parent
P = B / 'research3_open_vocab_technique_generalization01'
D = B / 'research3_open_vocab_failure_mechanism_diagnosis01'
V = B / 'research3_open_vocab_384_case_blind_review01'
A = B / 'research3_domain_adaptive_contrastive_learning01'
S = B / 'research3_technique_strong_baselines_generalization02'
M = B / 'research3_attack_mechanism_discrimination01'
L = B / 'research3_llm_agent_technique_reasoning01'
E = B / 'research3_semantic_model_execution_agent_validation02'


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def load(p):
    return json.loads(Path(p).read_text())


def lines(p):
    with Path(p).open() as f:
        for s in f:
            if s.strip():
                yield json.loads(s)


def csvrows(p):
    with Path(p).open(newline='') as f:
        return list(csv.DictReader(f))


def dump(n, x):
    (R / n).write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def writecsv(n, rows, fields=None):
    fields = fields or list(rows[0])
    with (R / n).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(row.get(k), ensure_ascii=False) if isinstance(row.get(k), (list, dict)) else row.get(k) for k in fields})


def main():
    assets, expected, inspections = {}, {}, {}

    def add(p, role, version='FROZEN_HISTORICAL_ASSET', inspect='HASH_ONLY'):
        p = Path(p).resolve()
        key = str(p)
        if key not in assets:
            exists = p.is_file()
            assets[key] = {'artifact_id': f'ASSET_{len(assets)+1:04d}', 'path': key, 'exists': exists,
                           'sha256': sha(p) if exists else None, 'bytes': p.stat().st_size if exists else None,
                           'version': version, 'role': role, 'content_inspection': inspect,
                           'qualification': 'HASHED_NOT_SEMANTICALLY_CERTIFIED' if exists else 'MISSING',
                           'limitations': 'historical/development asset; a valid hash does not establish semantic truth or independent testing'}
        else:
            if role not in assets[key]['role']:
                assets[key]['role'] += ';' + role
            if inspect != 'HASH_ONLY':
                assets[key]['content_inspection'] = inspect
        return p

    # Freeze bytes before gate analysis. Legacy checksums are metadata only;
    # their prediction/checkpoint payloads are not executed.
    for root in [P, D, V]:
        mp = add(root / 'manifests/DELIVERY_SHA256.json', 'legacy delivery version manifest', inspect='METADATA_READ')
        for entry in load(mp):
            p = add(root / entry['path'], 'legacy delivery member')
            expected[str(p)] = entry['sha256']

    required_d = ['GTE_MISS_EVIDENCE_CARDS.jsonl', 'GTE_MISS_GOLD_DIAGNOSTICS.csv',
                  'UNSEEN_GOLD_TECHNIQUE_DIAGNOSTICS.csv', 'CANDIDATE_COMPARISON.csv.gz',
                  'QUERY_DIAGNOSTICS.csv', 'INDEPENDENT_HIT_RECOUNT.csv',
                  'COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv', 'LOST_CASES_FULL_ANALYSIS.md',
                  'DIAGNOSTIC_PROTOCOL.json', 'results/FINAL_VALIDATION.json']
    for n in required_d:
        add(D / n, 'user-specified diagnosis asset')
    for root, names in [
        (A, ['TRAINING_DATA_MANIFEST.json', 'TRAINING_ENVIRONMENT_MANIFEST.json',
             'STANDARD_CONTRASTIVE_PROTOCOL.md', 'GROUPED_TRAIN_VALIDATION_SPLITS.json',
             'METHOD_RESEARCH_DECISION.md', 'data/CANDIDATE_TECHNIQUE_IDS.json', 'data/KNOWLEDGE_K2.json',
             'data/P0_INPUTS.jsonl', 'data/P0_REFERENCE.jsonl', 'STANDARD_CONTRASTIVE_RESULTS.csv',
             'HARD_NEGATIVE_TRAINING_RESULTS.csv', 'EXTERNAL_DATASET_QUALIFICATION.md',
             'TRAINABLE_PROJECTION_RESULTS.csv', 'HARD_NEGATIVE_ABLATION.csv']),
        (S, ['STRONG_BASELINE_REGISTER_V2.csv', 'STRONG_BASELINE_RESULTS_P0.csv',
             'BASELINE_REPRODUCTION_STATUS_V2.csv', 'METHOD_HYPOTHESIS_V2.md', 'METHOD_RESEARCH_DECISION.md',
             'GENERALIZATION_LIMITATIONS.md', 'datasets/p0_native.jsonl', 'datasets/p0_reference.jsonl',
             'knowledge/K2_DESCRIPTION_16_1.json', 'baselines/engine.py', 'baselines/prepare_controls.py',
             'baselines/prepare_inputs.py', 'baselines/run_matrix.py', 'frozen_p0/evaluate_techniques.py']),
        (M, ['METHOD_RESEARCH_DECISION.md', 'MECHANISM_HUMAN_REVIEW_STATUS.csv', 'RERANKER_FAILURE_DIAGNOSIS.md']),
        (L, ['METHOD_RESEARCH_DECISION.md', 'METHOD_HYPOTHESIS_AND_FORMULATION.md', 'STATIC_RETRIEVAL_AGENT_CONTROLS.csv'])]:
        for n in names:
            add(root / n, 'linked historical baseline/input/reference/method asset')
    for n in ['METHOD_RESEARCH_DECISION.md', 'R3_SEMANTIC_MODEL_EXECUTION_AGENT_VALIDATION_RESULTS.md',
              'EMBEDDING_REAL_RESULTS.csv', 'RERANKER_REAL_RESULTS.csv', 'AGENT_PAIRED_COMPARISON.csv',
              'AGENT_EPISODE_PROTOCOL.md', 'INPUT_SELECTION_REPAIR.md']:
        add(E / n, 'later actual semantic-model/agent evidence;supersedes earlier blocked milestone', inspect='SAVED_REPORT_OR_TABLE_READ')
    add(B / 'research3_attack_technique_benchmark01/STRONG_BASELINE_REGISTER.csv',
        'earlier original9-method register;historical statuses only', inspect='SAVED_REGISTER_READ')

    # Expected versions for selected supplementary files where available.
    for root in [A, E]:
        mp = add(root / 'manifests/DELIVERY_SHA256.json', 'supplementary version manifest', inspect='METADATA_READ')
        for entry in load(mp):
            key = str((root / entry['path']).resolve())
            expected[key] = entry['sha256']
    txt = add(S / 'manifests/DELIVERY_SHA256SUMS.txt', 'lexical baseline version manifest', inspect='METADATA_READ')
    for line in txt.read_text().splitlines():
        bits = line.split(maxsplit=1)
        if len(bits) == 2:
            key = str((S / bits[1].lstrip('*')).resolve())
            expected[key] = bits[0]

    sm = load(P / 'FULL_216_SCORE_MATRIX_MANIFEST.json')
    for x in sm['matrices']:
        for model, s in x['source_models'].items():
            p = add(s['checkpoint_path'], 'source checkpoint ' + model + ';hash only;not loaded', 'ATTACK16.1_FIXED_GTE_TRAINED_HEAD')
            expected[str(p)] = s['checkpoint_sha256']
        p = add(P / x['path'], 'saved score matrix;hash only', 'ATTACK_16_1_216_COLUMNS')
        expected[str(p)] = x['sha256']
        add(P / Path(x['path']).with_suffix('.json'), 'score column/input/source provenance', inspect='METADATA_READ')

    candidate_ids = load(A / 'data/CANDIDATE_TECHNIQUE_IDS.json')
    kd, kl = load(A / 'data/KNOWLEDGE_K2.json'), load(S / 'knowledge/K2_DESCRIPTION_16_1.json')
    assert len(candidate_ids) == len(set(candidate_ids)) == 216
    qi = {x['sample_id']: x for x in lines(A / 'data/P0_INPUTS.jsonl')}
    ql = {x['sample_id']: x for x in lines(S / 'datasets/p0_native.jsonl')}
    qr = {x['sample_id']: x for x in lines(A / 'data/P0_REFERENCE.jsonl')}
    qlr = {x['sample_id']: x for x in lines(S / 'datasets/p0_reference.jsonl')}
    def digest(s):
        return hashlib.sha256(s.encode()).hexdigest()
    parity = {'query_id_sets_equal': set(qi) == set(ql) == set(qr) == set(qlr),
              'query_count_GTE': len(qi), 'query_count_lexical': len(ql),
              'candidate_ids_equal': set(candidate_ids) == set(kd) == set(kl),
              'identical_query_texts': sum(qi[k]['input_log_text'] == ql[k]['text'] for k in set(qi) & set(ql)),
              'identical_knowledge_documents': sum(kd[k] == kl[k] for k in set(kd) & set(kl)),
              'GTE_query_total_UTF8_bytes': sum(len(x['input_log_text'].encode()) for x in qi.values()),
              'lexical_query_total_UTF8_bytes': sum(len(x['text'].encode()) for x in ql.values()),
              'GTE_query_max_UTF8_bytes': max(len(x['input_log_text'].encode()) for x in qi.values()),
              'lexical_query_max_UTF8_bytes': max(len(x['text'].encode()) for x in ql.values()),
              'GTE_knowledge_total_UTF8_bytes': sum(len(x.encode()) for x in kd.values()),
              'lexical_knowledge_total_UTF8_bytes': sum(len(x.encode()) for x in kl.values()),
              'labels_equal_after_parent_normalization': sum(set(qr[k]['gold_technique_ids']) == {t.split('.')[0] for t in qlr[k]['ground_truth']} for k in set(qr) & set(qlr)),
              'comparison_status': 'HISTORICAL_INPUT_BUDGET_PARITY_NOT_ESTABLISHED_NO_REINFERENCE',
              'payload_policy': 'compared already-authorized frozen strings; no new semantic review or source expansion'}
    dump('audit/INPUT_AND_KNOWLEDGE_PARITY.json', parity)

    # Read current files, not just the report's claim about counts/schema.
    exports = []
    for filename, scorekey in [('FROZEN_GTE_SCORES.jsonl', 'frozen_gte_scores'),
                               ('B3_SUPERVISED_SCORES.jsonl', 'supervised_b3_scores'),
                               ('FUSION_PREDICTIONS.jsonl', 'scores_all216')]:
        path = add(P / filename, 'frozen score/prediction export', inspect='ALL_ROWS_SCHEMA_AND_COUNT_ONLY')
        n, invalid, nulls = 0, 0, 0
        groups = Counter()
        for x in lines(path):
            n += 1
            ids = x.get('technique_ids', x.get('ranking_all216'))
            sc = x[scorekey]
            valid = len(ids) == len(set(ids)) == len(sc) == 216 and set(ids) == set(candidate_ids)
            if filename == 'B3_SUPERVISED_SCORES.jsonl':
                valid &= all((v is not None) == available for v, available in zip(sc, x['supervised_score_available']))
                nulls += sum(v is None for v in sc)
            invalid += not valid
            groups[(str(x.get('method', 'score_export')), str(x['seed']), x['view_id'])] += 1
        exports.append({'path': str(path), 'rows': n, 'schema_invalid_rows': invalid,
                        'null_B3_cells': nulls, 'groups': [{'method': k[0], 'seed': k[1], 'view': k[2], 'rows': v} for k, v in groups.items()],
                        'new_metrics_or_rankings_computed': False})
    dump('audit/SAVED_EXPORT_SCHEMA_AUDIT.json', exports)

    history = []
    for x in csvrows(P / 'FUSION_RESULTS.csv'):
        if x['view_id'] == 'ONE_VIEW_PER_STEP':
            history.append({k: x[k] for k in ['method', 'view_id', 'aggregation', 'seeds', 'n_records',
                            'mrr', 'seen_target_mrr', 'unseen_target_mrr', 'top10_accuracy']})
    recount = [x for x in csvrows(D / 'INDEPENDENT_HIT_RECOUNT.csv') if x['view_id'] == 'ONE_VIEW_PER_STEP']
    counterfactual = [x for x in csvrows(D / 'COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv') if x['view_id'] == 'ONE_VIEW_PER_STEP']
    reviews = list(lines(V / 'review/QUERY_EVIDENCE_REVIEWS.jsonl'))
    case_ids = {x['sample_id'] for x in reviews}
    misspairs = [x for x in csvrows(D / 'GTE_MISS_GOLD_DIAGNOSTICS.csv') if x['seed'] == '17' and x['view_id'] == 'ONE_VIEW_PER_STEP']
    provenance = {'source': 'read saved historical tables;no evaluator or parameter grid rerun',
                  'fusion_ONE_three_seed_results': history, 'ONE_recount': recount,
                  'ONE_counterfactual_components': counterfactual,
                  'gold_pair_denominator_reconciliation': {'all_query_missed_gold_pairs_seed17_ONE': len(misspairs),
                    'missed_gold_pairs_inside384_query_misses': sum(x['sample_id'] in case_ids for x in misspairs),
                    'missed_gold_pairs_in_other_GTE_hit_queries': sum(x['sample_id'] not in case_ids for x in misspairs),
                    'interpretation': 'query misses and missed Gold assignments have different denominators'},
                  'within_unseen_order_349_interpretation': 'seen-only movement cannot repair these frozen-order misses;does not prove representation causality',
                  'B3_Unseen_interpretation': 'closed-set missing-class structural limit;not backbone forgetting',
                  '32_losses_interpretation': 'historically diagnosed seen-supervision correction;not a new discovery or model result'}
    dump('audit/HISTORICAL_RESULT_SOURCE_AUDIT.json', provenance)

    baseline_rows = []
    for x in history:
        baseline_rows.append({'baseline_id': 'OPEN_' + x['method'], 'method': x['method'], 'condition': 'ONE;THREE_SEED_MEAN',
            'input_asset': str(A / 'data/P0_INPUTS.jsonl'), 'input_budget': 'existing frozen RAW;<=2000UTF8 bytes/query',
            'knowledge_asset': str(A / 'data/KNOWLEDGE_K2.json'), 'candidate_space': 216,
            'prediction_asset': str(P / 'FUSION_PREDICTIONS.jsonl'), 'source_asset': str(P / 'FUSION_RESULTS.csv'),
            'historical_MRR10': x['mrr'], 'historical_Top10': x['top10_accuracy'],
            'historical_Seen_MRR10': x['seen_target_mrr'], 'historical_Unseen_MRR10': x['unseen_target_mrr'],
            'query_count': 975, 'evaluation_qualification': 'PUBLIC_EXPOSED_DEVELOPMENT',
            'baseline_qualification': 'REGISTERED_SAVED_216_CANDIDATE_BASELINE',
            'limitations': 'not independent test;B3 absent unseen remains missing;historical metrics not new experiment',
            'new_experiment_result': False})
    lexical_results = csvrows(S / 'STRONG_BASELINE_RESULTS_P0.csv')
    for i, x in enumerate(lexical_results, 1):
        input_name = 'prediction' if x['input_view'] == 'all' else 'native' if x['input_view'] == 'sourcewise_same_native_content' else x['input_view']
        input_path = add(S / 'datasets' / ('p0_' + input_name + '.jsonl'), 'lexical condition frozen input;hash only')
        knowledge_path = add(S / 'knowledge' / (x['knowledge_view'] + '.json'), 'lexical condition frozen knowledge;hash only')
        baseline_rows.append({'baseline_id': f'LEXICAL_CONDITION_{i:03d}', 'method': x['method'],
            'condition': x['input_view'] + ';' + x['knowledge_view'],
            'input_asset': str(input_path),
            'input_budget': 'historical view-specific native/source content;not equalized with GTE2000-byte view',
            'knowledge_asset': str(knowledge_path), 'candidate_space': x['KnowledgeCoverage'],
            'prediction_asset': 'native receipt inspected for selected full216 BM25/char;other conditions registered in source table',
            'source_asset': str(S / 'STRONG_BASELINE_RESULTS_P0.csv'), 'historical_MRR10': x['mrr'],
            'historical_Top10': x['top10_accuracy'], 'historical_Seen_MRR10': 'NOT_AVAILABLE',
            'historical_Unseen_MRR10': 'NOT_AVAILABLE', 'query_count': x['N_Queries'],
            'evaluation_qualification': x['EvaluationQualification'],
            'baseline_qualification': 'FULL216_HISTORICAL_BASELINE' if x['KnowledgeCoverage'] == '216' else '203_COMMON_COVERAGE_DIAGNOSTIC_NOT_FULL216_COMPARATOR',
            'limitations': 'all existing conditions retained;strongest reported condition is descriptive development selection;no fair matched-budget superiority claim',
            'new_experiment_result': False})
    native_predictions = []
    for mode in ['bm25', 'char']:
        stem = f'P0_{mode}_K2_DESCRIPTION_16_1_native'
        receipt = add(S / 'experiments' / (stem + '_receipt.json'), 'actual lexical execution receipt', inspect='METADATA_READ')
        rr = load(receipt)
        pp = add(rr['output'], 'actual lexical top10 predictions', inspect='ALL_ROWS_SCHEMA_AND_COUNT_ONLY')
        z = list(lines(pp))
        native_predictions.append({'method': rr['method'], 'exit_code': rr['exit_code'], 'rows': len(z),
            'unique_queries': len({x['sample_id'] for x in z}), 'prediction_top10_valid': all(len(x['predictions']) == len(set(x['predictions'])) == 10 and set(x['predictions']) <= set(candidate_ids) for x in z),
            'full_candidate_scoring_source': str(S / 'baselines/engine.py'),
            'full_candidate_scoring_verified_by_source_inspection': True, 'stored_output': 'top10 only, not216 saved scores',
            'receipt_command': rr['command'], 'current_round_execution': False})
    dump('audit/LEXICAL_PREDICTION_RECEIPT_AUDIT.json', native_predictions)
    dump('audit/EXISTING_STRONG_BASELINE_REGISTRATION.json', csvrows(S / 'STRONG_BASELINE_REGISTER_V2.csv'))
    dump('audit/BASELINE_STATUS_SUPERSESSION.json', [
        {'earlier': 'V2 register SentenceSemanticEncoder NOT_EXECUTED / earlyLLM embedding blocked',
         'current_evidence': str(E / 'METHOD_RESEARCH_DECISION.md'),
         'qualified_status': 'later actual embedding/reranker baseline ready on exposed development;no independent test',
         'rule': 'earlier status is project-timestamp-specific,not current global absence'},
        {'earlier': 'V2 register SupervisedClassifier NOT_EXECUTED',
         'current_evidence': str(A / 'METHOD_RESEARCH_DECISION.md'),
         'qualified_status': 'later real grouped-dev B3 and related trained heads;Unseen closed-set limit remains',
         'rule': 'do not weaken comparisons by claiming no supervised baseline exists'},
        {'earlier': 'Agent environment readiness or prior partial milestone',
         'current_evidence': str(E / 'AGENT_PAIRED_COMPARISON.csv'),
         'qualified_status': 'engineering end-to-end episodes available;valid pair subsets0/1/2,not validated incremental gain',
         'rule': 'neither engineering success nor incomplete pairing proves algorithm gain'}])
    for name, root, fn, limitation in [
        ('B4_B5_B6_B7_B8_B9_contrastive_and_projection', A, 'METHOD_RESEARCH_DECISION.md', 'existing domain adaptation and hard negatives already tried;not a new algorithm;no checkpoint loaded'),
        ('Mechanism_views_and_reranker', M, 'METHOD_RESEARCH_DECISION.md', 'prior mechanism and cross-encoder comparisons do not establish new semantic contribution'),
        ('Static_LLM_and_Agent_controls_earlier_milestone', L, 'METHOD_RESEARCH_DECISION.md', 'earlier blocked/partial milestone;later validation02 has real embedding/reranker and3 valid episodes;do not present old blocked status as current')]:
        baseline_rows.append({'baseline_id': name, 'method': name, 'condition': 'HISTORICAL_SCOPE_ONLY',
            'input_asset': 'see linked frozen historical protocol', 'input_budget': 'historical method-specific;not harmonized',
            'knowledge_asset': 'see linked historical protocol', 'candidate_space': 'NOT_AVAILABLE_FOR_COMBINED_ROW',
            'prediction_asset': 'not re-executed;summary qualification audited', 'source_asset': str(root / fn),
            'historical_MRR10': 'NOT_AVAILABLE_FOR_COMBINED_ROW', 'historical_Top10': 'NOT_AVAILABLE_FOR_COMBINED_ROW',
            'historical_Seen_MRR10': 'NOT_AVAILABLE_FOR_COMBINED_ROW', 'historical_Unseen_MRR10': 'NOT_AVAILABLE_FOR_COMBINED_ROW',
            'query_count': 'NOT_AVAILABLE_FOR_COMBINED_ROW', 'evaluation_qualification': 'EXPOSED_DEVELOPMENT_OR_PILOT',
            'baseline_qualification': 'PRIOR_METHOD_NOT_TO_BE_RENAMED_AS_NOVEL', 'limitations': limitation,
            'new_experiment_result': False})
    for fn in ['EMBEDDING_REAL_RESULTS.csv', 'RERANKER_REAL_RESULTS.csv']:
        for i, x in enumerate(csvrows(E / fn), 1):
            baseline_rows.append({'baseline_id': 'VALIDATION02_' + x['method'], 'method': x['method'],
                'condition': 'historical repaired V2 input;single seed42;prefix/window/chunk protocol-specific',
                'input_asset': str(E / 'INPUT_SELECTION_REPAIR.md'),
                'input_budget': 'historical matched actual tokenizer caps:log2048,knowledge1024;not GTE2000-byte view',
                'knowledge_asset': str(E / 'R3_SEMANTIC_MODEL_EXECUTION_AGENT_VALIDATION_RESULTS.md'),
                'candidate_space': '216 public candidates;CE subset20/50/100 as method name;not identical candidate coverage',
                'prediction_asset': 'historical actual-run report/results audited;native predictions not individually revalidated this gate',
                'source_asset': str(E / fn), 'historical_MRR10': x['mrr'], 'historical_Top10': x['top10_accuracy'],
                'historical_Seen_MRR10': 'NOT_AVAILABLE_IN_THIS_TABLE', 'historical_Unseen_MRR10': 'NOT_AVAILABLE_IN_THIS_TABLE',
                'query_count': x['n_records'], 'evaluation_qualification': x['split'],
                'baseline_qualification': 'ACTUAL_MODEL_HISTORICAL_RESULT_NOT_CURRENT_NEW_EXPERIMENT',
                'limitations': 'retain matched lexical controls;single exposed-dev run;candidate/budget changes prohibit direct causal comparison with Z0/C4',
                'new_experiment_result': False})
    dump('audit/LATER_AGENT_PAIR_QUALIFICATION.json', {'source': str(E / 'AGENT_PAIRED_COMPARISON.csv'),
        'rows': csvrows(E / 'AGENT_PAIRED_COMPARISON.csv'),
        'interpretation': '3 valid engineering episodes reported;valid same-case pairs are0,1 or2 depending control;not full12-case valid comparison or incremental-gain proof;no new execution'})
    writecsv('EXISTING_BASELINE_AUDIT.csv', baseline_rows)

    # Qualifications inherit existing AI flags. No new semantic adjudication.
    matrix = []
    for x in reviews:
        sample = x['sample_id']
        flags = {g['evidence_assessment'] for g in x['gold_reviews']}
        scope_unresolved = 'GOLD_SCOPE_OR_GRANULARITY_UNCERTAIN' in flags
        obs_insufficient = x['overall_evidence_assessment'] in {'NO_RELEVANT_EVIDENCE_IN_VISIBLE_SCOPE', 'INSUFFICIENT_VISIBLE_INPUT'}
        quals = ['CANDIDATE_FOR_HUMAN_ADJUDICATION', 'REFERENCE_MISSING', 'NOT_ELIGIBLE_FOR_CURRENT_HYPOTHESIS']
        if scope_unresolved:
            quals.append('LABEL_SCOPE_UNRESOLVED')
        if obs_insufficient:
            quals.append('OBSERVATION_INSUFFICIENT')
        primary = 'LABEL_SCOPE_UNRESOLVED' if scope_unresolved else 'OBSERVATION_INSUFFICIENT' if obs_insufficient else 'REFERENCE_MISSING'
        matrix.append({'sample_id': sample, 'review_id': x['review_id'], 'logical_step_id': x['logical_step_id'],
            'scenario_id': x['scenario_id'], 'fold_id': x['fold_id'], 'input_view_hash': x['input_view_hash'],
            'gold_technique_ids': x['gold_technique_ids'], 'author_full_development_labels': qr[sample]['gold_technique_ids'],
            'author_label_status': 'AUTHOR_PROVIDED_NOT_INDEPENDENT_SEMANTIC_TRUTH',
            'observable_evidence_status': 'INHERITED_AI_' + x['overall_evidence_assessment'],
            'any_target_direct_AI_clue': 'DIRECT_EVIDENCE_PRESENT' in flags,
            'any_target_partial_AI_clue': 'PARTIAL_EVIDENCE_PRESENT' in flags,
            'distinguishing_evidence_status': 'NOT_AVAILABLE_NO_INDEPENDENT_PAIRWISE_ADJUDICATION',
            'gold_scope_status': 'AI_FLAG_SCOPE_UNRESOLVED' if scope_unresolved else 'NOT_INDEPENDENTLY_CONFIRMED',
            'independent_reference_status': 'INDEPENDENT_SEMANTIC_REFERENCE_NOT_AVAILABLE',
            'independent_test_status': 'INDEPENDENT_TEST_NOT_AVAILABLE',
            'input_coverage_status': 'FROZEN_BOUNDED_VIEW_OMITTED_COUNT_UNKNOWN',
            'human_adjudication_required': True, 'eligible_for_primary_metric': False,
            'qualification_states': quals, 'primary_blocker': primary,
            'blocker_reason': '现有AI线索：' + x['current_view_reasoning'] + '；独立语义参考与候选区分裁定未提供；既有材料已曝光，不能作独立测试。',
            'blinding_status': x['blinding_status'], 'AI_review_status': 'AI_PRE_REVIEW_NOT_GOLD',
            'source_AI_status_literal': x['review_status'],
            'source_review_path': str(V / 'review/QUERY_EVIDENCE_REVIEWS.jsonl'),
            'new_semantic_review_performed': False})
    writecsv('CASE_QUALIFICATION_MATRIX.csv', matrix)
    human = csvrows(M / 'MECHANISM_HUMAN_REVIEW_STATUS.csv')
    counts = {'original_queries': len(matrix), 'unique_queries': len({x['sample_id'] for x in matrix}),
              'logical_steps': len({x['logical_step_id'] for x in matrix}),
              'unique_visible_text_hashes': len({x['input_view_hash'] for x in matrix}),
              'query_target_Gold_assignments': sum(len(x['gold_technique_ids']) for x in matrix),
              'inherited_condition_records': load(V / 'results/REVIEW_COUNTS.json')['condition_rows'],
              'AI_flag_related_direct_or_partial_queries': sum(x['any_target_direct_AI_clue'] or x['any_target_partial_AI_clue'] for x in matrix),
              'AI_flag_any_direct_queries': sum(x['any_target_direct_AI_clue'] for x in matrix),
              'AI_flag_any_partial_queries': sum(x['any_target_partial_AI_clue'] for x in matrix),
              'independently_confirmed_relevant_behavior_queries': 'NOT_AVAILABLE',
              'queries_with_qualified_candidate_distinction': 'NOT_AVAILABLE',
              'human_adjudication_required': sum(x['human_adjudication_required'] for x in matrix),
              'currently_ineligible_for_confirmatory_primary_metric': sum(not x['eligible_for_primary_metric'] for x in matrix),
              'documented_qualified_independent_reference_records_in_checked_assets': 0,
              'actual_queries_with_qualified_independent_reference': 'NOT_AVAILABLE',
              'documented_qualified_independent_test_queries_in_checked_assets': 0,
              'actual_queries_with_independent_test_qualification': 'NOT_AVAILABLE',
              'primary_blocker_counts_exclusive': dict(Counter(x['primary_blocker'] for x in matrix)),
              'qualification_state_counts_nonexclusive': dict(Counter(q for x in matrix for q in x['qualification_states'])),
              'previous_30_case_human_queue_status_counts': dict(Counter(x['review_status'] for x in human)),
              'unit_warning': 'query,logical step,author label assignment and AI condition are not interchangeable;AI clues not qualified Gold or correct predictions'}
    dump('audit/CASE_QUALIFICATION_COUNTS.json', counts)

    # Finalize actual inventory with expected-version comparisons and content
    # inspection disclosure, never rewriting a legacy mismatch.
    used_metadata = [P / 'FULL_216_SCORE_MATRIX_MANIFEST.json', P / 'FUSION_RESULTS.csv',
                     D / 'INDEPENDENT_HIT_RECOUNT.csv', D / 'COUNTERFACTUAL_COMPONENT_DIAGNOSIS.csv',
                     D / 'GTE_MISS_GOLD_DIAGNOSTICS.csv', V / 'results/REVIEW_COUNTS.json',
                     S / 'STRONG_BASELINE_RESULTS_P0.csv', S / 'STRONG_BASELINE_REGISTER_V2.csv',
                     M / 'MECHANISM_HUMAN_REVIEW_STATUS.csv']
    for path in used_metadata:
        assets[str(path.resolve())]['content_inspection'] = 'METADATA_OR_SAVED_RESULT_TABLE_READ'
    assets[str((V / 'review/QUERY_EVIDENCE_REVIEWS.jsonl').resolve())]['content_inspection'] = 'EXISTING_AI_FIELDS_READ_NO_NEW_SEMANTIC_REVIEW'
    for path in [A / 'data/P0_INPUTS.jsonl', S / 'datasets/p0_native.jsonl', A / 'data/KNOWLEDGE_K2.json', S / 'knowledge/K2_DESCRIPTION_16_1.json']:
        assets[str(path.resolve())]['content_inspection'] = 'FROZEN_STRING_EQUALITY_AND_BUDGET_AUDIT'
    for p in assets.values():
        e = expected.get(p['path'])
        p['expected_sha256'] = e
        p['legacy_hash_status'] = 'MATCH' if e and p['sha256'] == e else 'MISMATCH' if e else 'NO_LEGACY_EXPECTATION_FOR_SELECTED_ASSET'
        if p['legacy_hash_status'] == 'MISMATCH':
            p['qualification'] = 'VERSION_DRIFT_BLOCKER_DO_NOT_REPAIR'
        elif p['exists']:
            p['qualification'] = 'HASH_MATCHED_DEVELOPMENT_ASSET' if e else 'CURRENT_BYTES_PINNED_DEVELOPMENT_ASSET'
    writecsv('ASSET_INVENTORY.csv', list(assets.values()))
    dump('audit/INPUT_HASH_SNAPSHOT.json', {'created_utc': datetime.now(timezone.utc).isoformat(),
        'timing': 'bytes hashed before gate matrix/report construction; exploratory reads were read-only',
        'files': [{'path': x['path'], 'sha256': x['sha256'], 'bytes': x['bytes']} for x in assets.values() if x['exists']]})
    mismatches = [x for x in assets.values() if x['legacy_hash_status'] == 'MISMATCH']
    missing = [x for x in assets.values() if not x['exists']]
    dump('audit/ASSET_AUDIT_SUMMARY.json', {'assets_checked': len(assets), 'missing_assets': missing,
        'hash_mismatches': mismatches, 'score_matrix_files': len(sm['matrices']),
        'referenced_source_checkpoints_hash_only': len({m['checkpoint_path'] for x in sm['matrices'] for m in x['source_models'].values()}),
        'checkpoint_deserialization_or_execution': False, 'candidate_count': len(candidate_ids),
        'prediction_export_schema_invalid_rows': sum(x['schema_invalid_rows'] for x in exports),
        'new_historical_metrics_recomputed': False, 'baseline_audit_rows': len(baseline_rows),
        'case_counts': counts, 'input_parity': parity})
    print(json.dumps({'assets_checked': len(assets), 'missing_assets': len(missing), 'legacy_hash_mismatches': len(mismatches),
                      'baseline_audit_rows': len(baseline_rows), 'matrix_counts': counts, 'input_parity': parity}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
