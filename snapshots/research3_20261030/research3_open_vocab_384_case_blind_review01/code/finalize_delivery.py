"""Seal current artifacts, retain limitations, and verify every delivery hash."""
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def load(n):
    return json.loads((R / n).read_text())


def info(p):
    return {'path': str(p.relative_to(R)), 'bytes': p.stat().st_size, 'sha256': sha(p)}


def dump(n, x):
    (R / n).write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def main():
    required = [
        'review/QUERY_EVIDENCE_REVIEWS.jsonl', 'review/CONDITION_EVIDENCE_MATRIX.csv',
        'review/HUMAN_REVIEW_QUEUE.csv', 'review/GOLD_CONDITION_CATALOG.json',
        'review/step_judgments.json', 'inputs/FROZEN_REVIEW_MANIFEST.json',
        'inputs/VISIBLE_FACT_REGISTRY.jsonl', 'inputs/REVIEW_INPUTS.jsonl',
        'protocol/BLINDING_AND_SCOPE_DISCLOSURE.json', 'protocol/BLOCKER_REGISTER.json',
        'protocol/EXECUTED_REVIEW_PROTOCOL.md', 'results/REVIEW_COUNTS.json',
        'results/MINIMUM_ADMISSION_ANSWERS.json', 'results/QUERY_REVIEW_SUMMARY.csv',
        'results/QUERY_STEP_VIEW_MAP.csv', 'results/DIAGNOSTIC_LABEL_OVERLAP.csv',
        'results/FINAL_VALIDATION.json', 'results/OLD_ASSET_INTEGRITY_AUDIT.json',
        'results/VALIDATION_CHECK_DETAILS.json',
        'reports/2026-10-28--open-vocab--r03--384-case-evidence-review.md',
        'reports/analysis-report.md', 'reports/stats-appendix.md', 'reports/figure-catalog.md']
    assert all((R / n).is_file() for n in required)
    validation = load('results/FINAL_VALIDATION.json')
    assert validation['mechanical_validation'] == 'PASS' and validation['failure_count'] == 0
    assert validation['execution_status'] == 'PARTIAL_REVIEW_WITH_DOCUMENTED_BLOCKERS'
    counts = load('results/REVIEW_COUNTS.json')
    old = load('results/OLD_ASSET_INTEGRITY_AUDIT.json')
    assert not old['changed_since_snapshot'] and not old['added_since_snapshot']
    outputs = [info(p) for p in sorted(R.rglob('*')) if p.is_file() and p.name not in {'RUN_MANIFEST.json', 'DELIVERY_SHA256.json'}]
    for e in outputs:
        assert sha(R / e['path']) == e['sha256']
    # Re-parse even final validator outputs, which that validator necessarily
    # wrote after checking its other inputs.
    parse_summary = {}
    for e in outputs:
        p = R / e['path']
        if p.suffix == '.json':
            json.loads(p.read_text())
            parse_summary[e['path']] = 'JSON_OK'
        elif p.suffix == '.jsonl':
            parse_summary[e['path']] = len([json.loads(s) for s in p.read_text().splitlines() if s.strip()])
        elif p.suffix == '.csv':
            with p.open(newline='') as f:
                parsed = list(csv.DictReader(f))
            assert all(None not in row for row in parsed)
            parse_summary[e['path']] = len(parsed)

    now = datetime.now(timezone.utc).isoformat()
    manifest = {
        'task_id': 'R3_OPEN_VOCAB_384_CASE_BLIND_EVIDENCE_REVIEW01',
        'run_version': 'v1_same_context_limited_AI_review',
        'directory_creation': 'new task directory created for this run; no pre-existing run overwritten',
        'execution_status': 'PARTIAL_REVIEW_WITH_DOCUMENTED_BLOCKERS',
        'decision': 'PRIORITIZE_EVIDENCE_ALIGNMENT_REVIEW',
        'decision_boundary': 'priority of independent evidence qualification, not proven dominant causal mechanism',
        'observed_artifact_start_utc': load('protocol/BLINDING_AND_SCOPE_DISCLOSURE.json')['created_utc'],
        'artifact_sealed_utc': now,
        'timing_limit': 'start is first retained preparation timestamp, not a full task or CPU timer',
        'input_paths_hashes': load('manifests/INPUT_HASHES.json'),
        'request_attachment_hashes': [info(R / f'protocol/USER_REQUEST_PART_{i}.txt') for i in (1, 2)],
        'frozen_review_list_sha256': load('inputs/FROZEN_REVIEW_MANIFEST.json')['manifest_list_sha256'],
        'code_version': [e for e in outputs if e['path'].startswith('code/')],
        'output_paths_hashes': outputs,
        'self_hash_rule': 'RUN_MANIFEST and DELIVERY_SHA256 excluded from this embedded list to avoid self-reference; DELIVERY_SHA256 includes RUN_MANIFEST and all other files, excluding its own self hash',
        'actual_commands': [
            {'command': 'python3 -B research3_open_vocab_384_case_blind_review01/code/decode_visible_hex.py', 'status': 'EXECUTED_SUCCESS', 'final_result': '105 fields;10 odd final nibbles;0 decoded commands executed'},
            {'command': 'python3 -B research3_open_vocab_384_case_blind_review01/code/materialize_reviews.py', 'status': 'EXECUTED_SUCCESS', 'final_result': '384 records;2618 conditions;re-executed after documented compound-proposition decomposition and metadata additions'},
            {'command': 'python3 -B research3_open_vocab_384_case_blind_review01/code/build_reports.py', 'status': 'EXECUTED_SUCCESS', 'final_result': 'reports,8 admission answers,5 blockers,384-row view map'},
            {'command': 'python3 -B research3_open_vocab_384_case_blind_review01/code/validate_reviews.py', 'status': 'EXECUTED_SUCCESS', 'final_result': validation['mechanical_validation']},
            {'command': 'python3 -B research3_open_vocab_384_case_blind_review01/code/finalize_delivery.py', 'status': 'EXECUTING_THIS_SEAL', 'result': 'all pre-seal existence,parse and hash checks already passed; final delivery readback verified before command returns'},
            {'command': 'python3 --version', 'status': 'EXECUTED_SUCCESS', 'result': 'Python 3.8.13'}],
        'preparation_commands_with_partial_telemetry': [
            {'script': str(R / 'code/prepare_inputs.py'), 'execution': 'executed successfully in earlier retained task context', 'exact_shell_interpreter_prefix': 'not reconstructed from compacted context'},
            {'script': str(R / 'code/build_condition_catalog.py'), 'execution': 'executed successfully in earlier retained task context', 'exact_shell_interpreter_prefix': 'not reconstructed from compacted context'},
            {'operation': 'stdlib incremental SHA256 snapshot of281 old files', 'execution': 'executed successfully via python3 -B stdin script; snapshot retained', 'exact_command': 'tool transcript; not reconstructed as a standalone file'}],
        'command_inventory_scope': 'artifact-producing and validation commands; exploratory read transcript not exhaustively reconstructed; no invented successful commands',
        'runtime': {'python_version': platform.python_version(), 'python_executable': sys.executable,
                    'dependencies': 'existing Python standard library only', 'CPU_thread_peak_measured': False,
                    'GPU_tasks': 0, 'peak_memory_measured': False},
        'review_counts': counts,
        'new_programmatic_model_API_calls': 0, 'new_agent_calls': 0,
        'new_embeddings_or_model_forwards': 0, 'new_training_runs': 0,
        'downloads': 0, 'external_network_accesses': 0, 'server_accesses': 0,
        'AI_usage_boundary': 'current assistant performed semantic pre-review; zero means additional programmatic model/agent/API calls, not absence of AI reasoning; internal token/compute not independently metered',
        'blinding': load('protocol/BLINDING_AND_SCOPE_DISCLOSURE.json'),
        'semantic_condition_provenance': 'same-context paraphrases; manual judgments read all80 step unions and query memberships; source definitions preserved, not independent elicitation',
        'failures_and_unfinished_items': load('protocol/BLOCKER_REGISTER.json'),
        'corrected_intermediate_issues': [
            {'issue': 'first snapshot attempt used hashlib.file_digest unavailable in Python3.8', 'result': 'AttributeError; no snapshot output; corrected using incremental stdlib SHA256; subsequent snapshot succeeded'},
            {'issue': 'initial static hex helper also interpreted SYSCALL register values as possible strings', 'result': 'restricted to PROCTITLE and EXECVE argument fields; final105 interpretations replace initial660 intermediate entries; no native facts or judgments derived from register-string interpretations'},
            {'issue': 'initial serialization could assign direct support to compound action+purpose/result propositions', 'result': 'decomposed18 direct-action targets into direct observable components and partial full propositions; full definition and top-level related-evidence judgments unchanged'}],
        'mechanical_validation': {'status': validation['mechanical_validation'],
                                  'check_count': validation['check_count'],
                                  'reference_instances': validation['condition_reference_instances_checked'],
                                  'independent_semantic_adjudication': False},
        'full_blind_review_contract': 'NOT_SATISFIED',
        'old_asset_integrity': old,
        'delivery_preseal_parse_summary': parse_summary,
        'known_required_files': required,
        'unknown_required_files': 'request sections8.3 remainder through13.3 missing; cannot certify undisclosed filenames',
        'stop_after_delivery': True}
    dump('RUN_MANIFEST.json', manifest)
    delivery = outputs + [info(R / 'RUN_MANIFEST.json')]
    delivery.sort(key=lambda e: e['path'])
    dump('manifests/DELIVERY_SHA256.json', delivery)
    # Actual readback verification. Any failure raises and must not be reported
    # as an overall success; this is file integrity only.
    readback = load('manifests/DELIVERY_SHA256.json')
    present = {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and p != R / 'manifests/DELIVERY_SHA256.json'}
    assert {e['path'] for e in readback} == present
    assert all((R / e['path']).stat().st_size == e['bytes'] and sha(R / e['path']) == e['sha256'] for e in readback)
    json.loads((R / 'RUN_MANIFEST.json').read_text())
    print(json.dumps({'sealed_manifest_entries': len(readback), 'total_files_including_checksum_list': len(readback) + 1,
                      'delivered_bytes_including_checksum_list': sum((R / e['path']).stat().st_size for e in readback) + (R / 'manifests/DELIVERY_SHA256.json').stat().st_size,
                      'delivery_sha256_list_sha256': sha(R / 'manifests/DELIVERY_SHA256.json'),
                      'readback_hash_verification': 'PASS', 'full_blind_review_contract': 'NOT_SATISFIED',
                      'execution_status': manifest['execution_status']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
