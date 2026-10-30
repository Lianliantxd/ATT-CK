"""Separate deterministic structural/citation validation, not adjudication."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def read(name):
    return json.loads((R / name).read_text())


def lines(name):
    return [json.loads(x) for x in (R / name).read_text().splitlines() if x.strip()]


def main():
    errors, checks = [], []

    def check(name, predicate):
        checks.append({'check': name, 'passed': bool(predicate)})
        if not predicate:
            errors.append(name)

    inp = lines('inputs/REVIEW_INPUTS.jsonl')
    reviews = lines('review/QUERY_EVIDENCE_REVIEWS.jsonl')
    registry = lines('inputs/VISIBLE_FACT_REGISTRY.jsonl')
    facts = {f['fact_id']: f for f in registry}
    frozen = read('inputs/FROZEN_REVIEW_MANIFEST.json')
    cat = read('review/GOLD_CONDITION_CATALOG.json')
    definitions = read('inputs/TARGET_DEFINITIONS.json')
    counts = read('results/REVIEW_COUNTS.json')
    expected = frozen['ordered_manifest']
    check('384 unique queries and exact frozen order',
          len(inp) == len(reviews) == len({x['sample_id'] for x in reviews}) == 384 and
          [r['sample_id'] for r in reviews] == [r['sample_id'] for r in expected])
    check('80 logical steps;54 target IDs;520 assignments;86 multi-Gold queries',
          len({r['logical_step_id'] for r in reviews}) == 80 and len(cat) == 54 and
          sum(len(r['gold_technique_ids']) for r in reviews) == 520 and
          sum(len(r['gold_technique_ids']) > 1 for r in reviews) == 86)
    check('2178 source-locator IDs unique', len(facts) == len(registry) == 2178)
    check('catalog retains all literal target definitions', set(cat) == set(definitions) and all(c['frozen_description'] == definitions[t] for t, c in cat.items()))
    ev_enum = {'DIRECTLY_SUPPORTED', 'PARTIALLY_SUPPORTED', 'EXPLICITLY_CONTRADICTED',
               'NOT_ESTABLISHED', 'NOT_OBSERVABLE_IN_CURRENT_VIEW', 'NOT_EVALUABLE'}
    top_enum = {'DIRECT_EVIDENCE_PRESENT', 'PARTIAL_EVIDENCE_PRESENT', 'BACKGROUND_COMPATIBILITY_ONLY',
                'NO_RELEVANT_EVIDENCE_IN_VISIBLE_SCOPE', 'INSUFFICIENT_VISIBLE_INPUT',
                'COMPETING_TECHNIQUE_AMBIGUITY', 'GOLD_SCOPE_OR_GRANULARITY_UNCERTAIN', 'NOT_EVALUABLE'}
    diag_enum = {'OBSERVABLE_EVIDENCE_PRESENT', 'PARTIAL_EVIDENCE_PRESENT', 'BACKGROUND_COMPATIBILITY_ONLY',
                 'NO_RELEVANT_EVIDENCE_IN_VISIBLE_SCOPE', 'INSUFFICIENT_VISIBLE_INPUT',
                 'GOLD_LOG_GRANULARITY_MISMATCH', 'COMPETING_TECHNIQUE_AMBIGUITY',
                 'DISTINGUISHING_FIELD_MISSING_FROM_VIEW', 'POSSIBLE_PREPROCESSING_LOSS',
                 'POSSIBLE_LABEL_MAPPING_ISSUE', 'SEMANTIC_CAUSE_UNRESOLVED'}
    failure_enum = {'OBSERVATION_COVERAGE_LIMITATION', 'INPUT_REPRESENTATION_LIMITATION',
                    'PREPROCESSING_OR_TRUNCATION_CONFIRMED', 'GOLD_SCOPE_OR_GRANULARITY_UNCERTAIN',
                    'CANDIDATE_SEMANTIC_OVERLAP', 'POSSIBLE_REPRESENTATION_RANKING_FAILURE',
                    'POSSIBLE_LABEL_ALIGNMENT_ISSUE', 'UNRESOLVED'}
    citation_count = 0
    for src, r in zip(inp, reviews):
        rid = r['review_id']
        for key in ['review_id', 'sample_id', 'logical_step_id', 'scenario_id', 'execution_id',
                    'fold_id', 'view_id', 'input_view', 'input_view_hash', 'gold_technique_ids']:
            check(rid + ':source_metadata:' + key, src[key] == r[key])
        check(rid + ':input_text_hash', hashlib.sha256(src['frozen_input_text'].encode()).hexdigest() == r['input_view_hash'])
        scope = r['visible_scope']
        check(rid + ':actual_visible_scope', scope['visible_fact_ids'] == src['visible_fact_ids'] and
              scope['visible_record_count'] == len(src['frozen_input_text'].splitlines()) and
              scope['omitted_record_count'] is None and scope['native_fact_ids_provided'] is False)
        check(rid + ':honest_AI_nonblind_status', r['review_status'] == 'AI_BLIND_PRE_REVIEW_NOT_GOLD' and
              r['blinding_status'] == 'PREDICTION_BLINDING_NOT_ENFORCED' and r['human_review_required'] is True and
              r['confidence'] in {'LOW', 'MEDIUM', 'HIGH'} and bool(r['confidence_basis']) and bool(r['human_review_reasons']))
        check(rid + ':valid_top_and_diagnostics', r['overall_evidence_assessment'] in top_enum and
              all(d['label'] in diag_enum and d['reason'] for d in r['diagnostic_labels']) and
              all(d['label'] in failure_enum and d['reason'] for d in r['failure_diagnoses']))
        check(rid + ':competitor_block_preserved', r['competing_technique_analysis']['competing_techniques_reviewed'] == [] and
              r['competing_technique_analysis']['status'] == 'NOT_EVALUABLE_WITHOUT_BREAKING_ALLOWED_REVIEW_INPUT_CONTRACT' and
              r['competing_technique_analysis']['Gold_is_unique_supported_explanation'] is False)
        observed = {f['fact_id']: f for f in r['visible_facts']}
        check(rid + ':literal_visible_facts_complete', set(observed) == set(scope['visible_fact_ids']))
        for fid, f in observed.items():
            original = facts[fid]
            check(fid + ':exact_original_input_line', original['text'] == src['frozen_input_text'].splitlines()[original['line_number'] - 1])
            check(fid + ':literal_and_hash_and_owner', original['review_id'] == rid and f['literal_text'] == original['text'] and
                  f['text_sha256'] == hashlib.sha256(f['literal_text'].encode()).hexdigest())
            if '[**]' in f['literal_text'] or 'Classification:' in f['literal_text']:
                check(fid + ':IDS_derivation_disclosed', f['source_type'] == 'IDS_ALERT_DERIVED_PATTERN_NOT_NATIVE_PAYLOAD')
        conds = r['gold_semantic_conditions']
        cond_ids = {c['condition_id'] for c in conds}
        check(rid + ':all_Gold_have_conditions', set(g['technique_id'] for g in r['gold_reviews']) == set(r['gold_technique_ids']) and
              all(set(g['condition_ids']) <= cond_ids and g['condition_ids'] for g in r['gold_reviews']))
        for g in r['gold_reviews']:
            ref = cat[g['technique_id']]
            check(rid + ':' + g['technique_id'] + ':frozen_definition_unchanged',
                  g['frozen_description'] == ref['frozen_description'] and
                  g['frozen_description_sha256'] == hashlib.sha256(g['frozen_description'].encode()).hexdigest())
            check(rid + ':' + g['technique_id'] + ':target_level_reference_scope',
                  all(f in observed and facts[f]['review_id'] == rid for f in g['supporting_fact_ids'] + g['context_fact_ids']))
            if g['evidence_assessment'] in {'DIRECT_EVIDENCE_PRESENT', 'PARTIAL_EVIDENCE_PRESENT'}:
                check(rid + ':' + g['technique_id'] + ':target_level_positive_reference', bool(g['supporting_fact_ids']))
        for c in conds:
            check(c['condition_id'] + ':status_and_reason', c['evidence_status'] in ev_enum and bool(c['reasoning']) and bool(c['scope_limitations']))
            for key in ['supporting_fact_ids', 'contradicting_fact_ids', 'context_fact_ids']:
                for fid in c[key]:
                    citation_count += 1
                    check(c['condition_id'] + ':' + key + ':' + fid, fid in facts and facts[fid]['review_id'] == rid and fid in observed)
            if c['evidence_status'] in {'DIRECTLY_SUPPORTED', 'PARTIALLY_SUPPORTED'}:
                check(c['condition_id'] + ':positive_citations_and_source', bool(c['supporting_fact_ids']) and bool(c['supporting_source_type']))
            if c['evidence_status'] == 'EXPLICITLY_CONTRADICTED':
                check(c['condition_id'] + ':explicit_contradiction_reference', bool(c['contradicting_fact_ids']))
            if c['evidence_status'] not in {'DIRECTLY_SUPPORTED', 'EXPLICITLY_CONTRADICTED'}:
                check(c['condition_id'] + ':specific_missing_information', bool(c['missing_information']))
        # Unknown must not silently become an explicit counterfactual.
        check(rid + ':no_missing_to_contradiction_conversion',
              not any(c['evidence_status'] == 'EXPLICITLY_CONTRADICTED' for c in conds))

    actual = Counter(r['overall_evidence_assessment'] for r in reviews)
    check('exclusive summary counts reproducible', all(actual[k] == v for k, v in counts['exclusive_overall_assessments'].items()) and sum(actual.values()) == 384)
    check('nonexclusive any-Gold summary counts reproducible', all(sum(any(g['evidence_assessment'] == k for g in r['gold_reviews']) for r in reviews) == v for k, v in counts['nonexclusive_any_gold_assessments'].items()))
    check('condition row count reproducible', counts['condition_rows'] == sum(len(r['gold_semantic_conditions']) for r in reviews))
    derived = lines('review/DERIVED_HEX_INTERPRETATIONS.jsonl')
    check('105 static decoded fields;10 incomplete final nibbles', len(derived) == 105 and sum(x['odd_final_nibble_undecodable'] for x in derived) == 10)
    for x in derived:
        f = facts[x['fact_id']]
        check(x['fact_id'] + ':hex_decode_source_not_register', f['review_id'] == x['review_id'] and
              (x['field'] == 'proctitle' or 'type=EXECVE ' in f['text']) and
              x['field'] + '=' + x['literal_hex'] in f['text'])
    def keys(x):
        if isinstance(x, dict):
            for k, v in x.items():
                yield k
                yield from keys(v)
        elif isinstance(x, list):
            for v in x:
                yield from keys(v)
    forbidden = {'top10', 'gte_top10', 'model_predictions', 'rank', 'scores', 'ranking', 'B3_prediction', 'C4_prediction'}
    check('no prediction payload keys in reviewer inputs or outputs', not (set(keys(inp)) | set(keys(reviews))) & forbidden)

    parse_counts = {}
    for p in sorted(R.rglob('*')):
        if not p.is_file() or p.name in {'FINAL_VALIDATION.json', 'VALIDATION_CHECK_DETAILS.json'}:
            continue
        if p.suffix == '.json':
            json.loads(p.read_text())
            parse_counts[str(p.relative_to(R))] = 'JSON_PARSE_OK'
        elif p.suffix == '.jsonl':
            parsed = [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
            parse_counts[str(p.relative_to(R))] = len(parsed)
        elif p.suffix == '.csv':
            with p.open(newline='') as f:
                parsed = list(csv.DictReader(f))
            check(str(p.relative_to(R)) + ':CSV_no_overflow', all(None not in row for row in parsed))
            parse_counts[str(p.relative_to(R))] = len(parsed)
    for p in read('manifests/INPUT_HASHES.json'):
        check('source_hash_unchanged:' + p['path'], sha(Path(p['path'])) == p['sha256'])

    snap = read('manifests/OLD_ASSET_PRE_FINALIZATION_SNAPSHOT.json')
    changed = [s['path'] for s in snap['files'] if not Path(s['path']).exists() or sha(Path(s['path'])) != s['sha256']]
    check('281 observed old files unchanged since pre-finalization snapshot', not changed)
    observed_paths = {s['path'] for s in snap['files']}
    present_paths = {str(p.resolve()) for dirname in ['research3_open_vocab_failure_mechanism_diagnosis01', 'research3_open_vocab_technique_generalization01'] for p in (R.parent / dirname).rglob('*') if p.is_file() and not p.is_symlink()}
    added = sorted(present_paths - observed_paths)
    check('no files added to old source directories since snapshot', not added)
    legacy = []
    for dirname in ['research3_open_vocab_failure_mechanism_diagnosis01', 'research3_open_vocab_technique_generalization01']:
        base = R.parent / dirname
        entries = json.loads((base / 'manifests/DELIVERY_SHA256.json').read_text())
        diffs = []
        for e in entries:
            p = base / e['path']
            actual_sha = sha(p) if p.exists() else None
            if actual_sha != e['sha256']:
                diffs.append({'path': str(p), 'legacy_expected_sha256': e['sha256'], 'current_sha256': actual_sha,
                              'interpretation': 'pre-existing discrepancy previously disclosed; no repair or modification in this task'})
        legacy.append({'directory': str(base), 'legacy_manifest_entries': len(entries), 'mismatches': diffs})
    # A pre-existing P report whitespace drift is reported, never normalized.
    old_audit = {'observed_files': len(snap['files']), 'observed_bytes': sum(s['bytes'] for s in snap['files']),
                 'snapshot_timing_limitation': snap['timing'], 'changed_since_snapshot': changed,
                 'added_since_snapshot': added,
                 'legacy_manifest_comparisons': legacy,
                 'other_historical_directories': 'not rehashed in this task; no write operations targeted them'}
    (R / 'results/OLD_ASSET_INTEGRITY_AUDIT.json').write_text(json.dumps(old_audit, ensure_ascii=False, indent=2) + '\n')
    (R / 'results/VALIDATION_CHECK_DETAILS.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2) + '\n')
    final = {'execution_status': 'PARTIAL_REVIEW_WITH_DOCUMENTED_BLOCKERS',
             'mechanical_validation': 'PASS' if not errors else 'FAIL',
             'overall_full_blind_review_contract': 'NOT_SATISFIED',
             'full_contract_blockers': ['independent prediction blinding not enforced',
                                        'Top10 competitor comparison not evaluated under restricted reviewer inputs',
                                        'request sections8.3 remainder through13.3 absent'],
             'semantic_adjudication': 'NOT_INDEPENDENTLY_VALIDATED_NOT_HUMAN_GOLD',
             'coverage': {'frozen_queries': len(expected), 'reviewed_queries': len(reviews),
                          'unique_output_queries': len({r['sample_id'] for r in reviews}),
                          'missing_query_ids': sorted({r['sample_id'] for r in expected} - {r['sample_id'] for r in reviews}),
                          'duplicate_query_ids': [k for k, v in Counter(r['sample_id'] for r in reviews).items() if v > 1],
                          'logical_steps': 80, 'target_techniques': 54, 'query_Gold_assignments': 520,
                          'multi_Gold_queries': 86, 'independently_blinded_queries': 0,
                          'competitor_comparisons_completed': 0, 'competitor_comparisons_blocked': 384},
             'check_count': len(checks), 'failure_count': len(errors), 'failures': errors,
             'condition_reference_instances_checked': citation_count,
             'parsed_file_counts': parse_counts,
             'old_assets_changed_since_snapshot': changed,
             'legacy_asset_drift_is_not_an_unconditional_PASS': True,
             'limitation': 'citation existence/scope and serialization checks cannot establish semantic correctness; delivery seal verified separately by finalize_delivery.py'}
    (R / 'results/FINAL_VALIDATION.json').write_text(json.dumps(final, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: final[k] for k in ['execution_status', 'mechanical_validation', 'overall_full_blind_review_contract', 'check_count', 'failure_count', 'condition_reference_instances_checked']}, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
