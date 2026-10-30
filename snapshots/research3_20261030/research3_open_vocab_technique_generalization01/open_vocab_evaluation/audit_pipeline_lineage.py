"""Read-only audit of saved fit/predict/evaluate provenance and stage order."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def load(name):
    return json.loads((R/name).read_text())


def main():
    fit = load('calibration/FITTING_RECEIPT.json')
    pred = load('predictions/PREDICTION_RECEIPT.json')
    evaluation = load('results/EVALUATION_AUDIT.json')
    tradeoff = load('results/TRADEOFF_EVALUATION_AUDIT.json')
    protocol = load('FUSION_PARAMETER_REGISTRATION.json')
    selected = load('calibration/SELECTED_PARAMETERS.json')
    assert fit['parameters_sha256'] == pred['parameters_sha256'] == sha(R/'calibration/SELECTED_PARAMETERS.json')
    assert fit['protocol_sha256'] == pred['protocol_sha256'] == evaluation['parameter_registration_sha256'] == tradeoff['parameter_registration_sha256'] == sha(R/'FUSION_PARAMETER_REGISTRATION.json')
    assert fit['source_sha256'] == sha(R/'calibration/fit_calibrators.py')
    assert pred['source_sha256'] == sha(R/'fusion/predict.py')
    assert pred['core_sha256'] == sha(R/'fusion/core.py')
    assert pred['main_prediction_sha256'] == evaluation['prediction_sha256'] == sha(R/'FUSION_PREDICTIONS.jsonl')
    assert pred['tradeoff_sha256'] == tradeoff['prediction_sha256'] == sha(R/'predictions/TRADEOFF_PREDICTIONS.jsonl')
    assert evaluation['evaluator_sha256'] == tradeoff['evaluator_sha256'] == sha(R/'open_vocab_evaluation/evaluate_saved.py')
    assert fit['selected_conditions'] == len(selected) == 462 and fit['grid_conditions'] == 1722
    assert pred['gold_read'] is False and fit['heldout_gold_read'] is False
    fit_refs = [p for p in fit['read_paths'] if 'reference' in Path(p).name.lower()]
    assert len(fit_refs) == 7 and all('/data/validation/' in p and p.endswith('_reference.jsonl') for p in fit_refs)
    assert not any('reference' in Path(p).name.lower() for p in pred['read_paths'])
    for item in selected:
        assert item['protocol_sha256'] == fit['protocol_sha256']
        assert item['fit_source_sha256'] == fit['source_sha256']
        assert item['core_source_sha256'] == pred['core_sha256']
        assert item['heldout_reference_read'] is False
        assert item['validation_reference_path'] in fit_refs
        assert item['validation_reference_sha256'] == sha(Path(item['validation_reference_path']))
        assert item['parameters'] in protocol['methods'][item['method']]['grid']
    names = ['FUSION_PARAMETER_REGISTRATION.json', 'calibration/SELECTED_PARAMETERS.json',
             'calibration/FITTING_RECEIPT.json', 'FUSION_PREDICTIONS.jsonl',
             'predictions/TRADEOFF_PREDICTIONS.jsonl', 'predictions/PREDICTION_RECEIPT.json',
             'FUSION_RESULTS.csv', 'results/EVALUATION_AUDIT.json',
             'SEEN_UNSEEN_TRADEOFF.csv', 'results/TRADEOFF_EVALUATION_AUDIT.json']
    times = {name: (R/name).stat().st_mtime_ns for name in names}
    assert times[names[0]] <= times[names[1]] <= times[names[2]]
    assert times[names[2]] <= min(times[names[3]], times[names[4]])
    assert max(times[names[3]], times[names[4]]) <= times[names[5]] <= times[names[6]] <= times[names[7]]
    assert times[names[5]] <= times[names[8]] <= times[names[9]]
    timeline = [{'path': name, 'sha256': sha(R/name), 'mtime_ns': times[name],
                 'mtime_utc': datetime.fromtimestamp(times[name]/1e9, timezone.utc).isoformat()} for name in names]
    output = {'status': 'PASS_WITH_DOCUMENTED_PREFLIGHT_TIMING_DEVIATION',
              'checked_selected_conditions': len(selected), 'registered_grid_conditions': fit['grid_conditions'],
              'fit_validation_reference_count': len(fit_refs), 'predictor_reference_read_count': 0,
              'new_fusion_metrics_used_for_parameter_selection': False,
              'hash_bindings_consistent': True, 'filesystem_stage_order_consistent': True,
              'time_evidence_limit': 'Receipts contain duration, not signed absolute stage timestamps; filesystem mtimes corroborate order but are not independent cryptographic execution proof.',
              'pre_prediction_reference_preflight_disclosure': evaluation['pre_prediction_reference_preflight_disclosure'],
              'qualification': 'Fit/predict access isolation passes; do not claim no agent ever read outer references before prediction.',
              'timeline': timeline, 'audit_source_sha256': sha(Path(__file__))}
    (R/'results/PIPELINE_LINEAGE_AUDIT.json').write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: output[k] for k in ['status', 'checked_selected_conditions', 'registered_grid_conditions', 'fit_validation_reference_count', 'predictor_reference_read_count']}))


if __name__ == '__main__':
    main()
