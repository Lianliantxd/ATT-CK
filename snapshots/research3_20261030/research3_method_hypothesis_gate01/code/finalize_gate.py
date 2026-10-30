"""Seal completed gate artifacts, not an experiment authorization."""
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
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def info(p):
    return {'path': str(p.relative_to(R)), 'bytes': p.stat().st_size, 'sha256': sha(p)}


def load(p):
    return json.loads(p.read_text())


def dump(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')


def main():
    final = load(R / 'FINAL_VALIDATION.json')
    assert final['failed_check_count'] == 0 and final['status'] == 'PASS_METHOD_GATE_WITH_DOCUMENTED_BLOCKERS'
    assert all(final['required_artifacts_present'].values())
    assert final['old_files_modified'] == 0 and final['experiment_executed'] is False
    manifest = load(R / 'RUN_MANIFEST.json')
    assert manifest['final_decision'] == final['final_decision'] == 'GO_AFTER_REFERENCE_QUALIFICATION'
    outputs = [info(p) for p in sorted(R.rglob('*')) if p.is_file() and p.name not in {'RUN_MANIFEST.json', 'DELIVERY_SHA256.json'}]
    for e in outputs:
        p = R / e['path']
        if p.suffix == '.json':
            load(p)
        elif p.suffix == '.csv':
            with p.open(newline='') as f:
                assert all(None not in row for row in csv.DictReader(f))
    manifest.update({
        'manifest_phase': 'SEALED_GATE_NOT_METHOD_EXPERIMENT',
        'sealed_utc': datetime.now(timezone.utc).isoformat(),
        'output_hashes': outputs,
        'code_hashes': [e for e in outputs if e['path'].startswith('code/')],
        'self_hash_rule': 'embedded list excludes RUN_MANIFEST and DELIVERY_SHA256;delivery checksum list includes RUN_MANIFEST and all others,excluding its own hash',
        'old_files_modified': 0,
        'old_integrity_scope': final['old_integrity_scope'],
        'formal_reference_status': final['reference_status'],
        'fair_comparison_ready': False,
        'method_experiment_admitted': False,
        'independent_test_status': final['independent_test_status'],
        'runtime': {'python': platform.python_version(), 'executable': sys.executable,
                    'dependency_scope': 'existing local standard library only',
                    'checkpoint_loading': False, 'GPU_used': False,
                    'peak_memory_CPU_usage_or_assistant_tokens_independently_metered': False},
        'actual_commands': [
            {'command': 'python3 -B research3_method_hypothesis_gate01/code/audit_assets.py',
             'status': 'EXECUTED_SUCCESS', 'result': '507 assets;128 baseline conditions;384 qualification rows',
             'repetition_reason': 're-executed after adding successor-model records and earlier baseline register;no model inference'},
            {'command': 'python3 -B research3_method_hypothesis_gate01/code/build_gate.py',
             'status': 'EXECUTED_SUCCESS', 'result': 'populated report,reference contract,one conditional hypothesis,nonexecutable experiment design'},
            {'command': 'python3 -B research3_method_hypothesis_gate01/code/validate_gate.py',
             'status': 'EXECUTED_SUCCESS', 'result': final['status'], 'checks': final['check_count']},
            {'command': 'python3 -B research3_method_hypothesis_gate01/code/finalize_gate.py',
             'status': 'IN_PROCESS_FIRST_SEAL_CHECK'}],
        'command_inventory_scope': 'artifact-producing/validation commands;exploratory read commands and failed guessed paths disclosed separately;not a reconstructed exhaustive shell transcript',
        'AI_usage_boundary': 'current assistant performed method-gate reasoning;0 model/agent calls means0 additional programmatic inference or delegated agents,not absence of AI reasoning',
        'limitations': final['limitations'],
        'current_task_success_boundary': 'gate completed for received scope;reference/test/implementation not qualified;no algorithm gain claimed'})
    mp = R / 'RUN_MANIFEST.json'
    dp = R / 'audit/DELIVERY_SHA256.json'

    def seal_and_check():
        dump(mp, manifest)
        entries = outputs + [info(mp)]
        entries.sort(key=lambda e: e['path'])
        dump(dp, entries)
        records = load(dp)
        present = {str(p.relative_to(R)) for p in R.rglob('*') if p.is_file() and p != dp}
        assert present == {e['path'] for e in records}
        assert all((R / e['path']).stat().st_size == e['bytes'] and sha(R / e['path']) == e['sha256'] for e in records)
        assert all(sha(R / e['path']) == e['sha256'] for e in manifest['output_hashes'])
        return records

    records = seal_and_check()
    # A successful readback has actually occurred before recording that fact.
    # Refresh only this manifest's checksum and verify the final readback again.
    manifest['actual_commands'][-1]['status'] = 'EXECUTED_FIRST_SEAL_READBACK_PASS'
    manifest['delivery_validation'] = {'first_readback_hash_check': 'PASS',
        'required_root_artifacts': 10, 'outputs_reparsed': True,
        'final_refreshed_manifest_checksum': 'verified by seal_and_check before this command returns',
        'method_experiment_status': 'NOT_EXECUTED_NOT_ADMITTED'}
    records = seal_and_check()
    print(json.dumps({'execution_status': manifest['execution_status'], 'final_decision': manifest['final_decision'],
                      'required_root_artifacts': 10, 'delivered_files_including_checksum_list': len(records) + 1,
                      'delivered_bytes': sum(e['bytes'] for e in records) + dp.stat().st_size,
                      'delivery_readback_hash_check': 'PASS', 'delivery_checksum_list_sha256': sha(dp),
                      'new_model_calls': 0, 'new_training_runs': 0, 'server_access': False,
                      'old_files_modified': 0, 'experiment_executed': False}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
