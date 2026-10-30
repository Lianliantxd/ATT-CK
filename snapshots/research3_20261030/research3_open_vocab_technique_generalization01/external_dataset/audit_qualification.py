"""Independent stdlib audit of the metadata-only external deliverables."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parent
R = E.parent
D = R.parent / 'research3_domain_adaptive_contrastive_learning01'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    source = json.loads((E / 'metadata/SOURCE_RECEIPTS.json').read_text())
    checks = []
    for record in source['receipts']:
        p = E / 'metadata' / record['file']; data = p.read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        assert actual == record['git_blob_sha1'], (p, actual, record['git_blob_sha1'])
        checks.append({'path': str(p.relative_to(R)), 'git_blob_sha1': actual, 'sha256': sha256(data), 'bytes': len(data)})
    directories = source['directories']
    assert len(directories) == 5
    assert directories[0]['specific_license_entries'] == ['LICENSE']
    assert all(not x['specific_license_entries'] for x in directories[1:])
    assert 'Apache License' in (E / 'metadata/LICENSE').read_text()
    text = (E / 'metadata/atomic_red_team.yml').read_text()
    assert 'mitre_technique:\n- T1003.003\n' in text
    ids_path = D / 'data/CANDIDATE_TECHNIQUE_IDS.json'
    ids = json.loads(ids_path.read_text()); assert len(ids) == 216 and 'T1003' in ids
    request_path = E / 'EXTERNAL_DOWNLOAD_AUTHORIZATION_REQUEST.json'
    request = json.loads(request_path.read_text())
    assert request['authorized'] is False  # Frozen proposal, not a subsequent grant.
    assert request['total_payload_bytes'] == 12905849 == sum(x['bytes'] for x in request['files'])
    assert len(request['files']) == 3 and request['maximum_bags'] == 1
    assert not any((E / 'raw').glob('*'))
    for record in request['files']:
        assert '/671f9f5b065f03a5502db07c20f1fe3f620d29d9/' in record['download_url']
        pointer = (E / 'metadata' / (Path(record['name']).stem + '.lfs')).read_text()
        assert f"oid sha256:{record['sha256']}\n" in pointer
        assert f"size {record['bytes']}\n" in pointer
    register = list(csv.DictReader((R / 'EXTERNAL_DATA_INSTANCE_REGISTER.csv').open()))
    assert len(register) == 1 and register[0]['qualification'] == 'E0'
    assert (R / 'EXTERNAL_EVALUATION_PREDICTIONS.jsonl').stat().st_size == 0
    results = list(csv.DictReader((R / 'EXTERNAL_EVALUATION_RESULTS.csv').open()))
    assert len(results) == 9
    assert all(x['evaluated_bags']=='0' and x['status']=='NOT_EXECUTED' for x in results)
    assert all(x[k] == 'N/A' for x in results for k in ['top1','top5','top10','mrr10'])
    report = {'status': 'PASS_METADATA_ONLY', 'qualification': 'E0', 'scientific_state':'EXTERNAL_TEST_NOT_READY', 'git_blob_checks':checks,
              'license_ancestor_directories_checked':5, 'candidate_count':216, 'parent_id':'T1003',
              'candidate_inventory_path':str(ids_path), 'candidate_inventory_sha256':sha256(ids_path.read_bytes()),
              'request_sha256':sha256(request_path.read_bytes()), 'payload_bytes_requested':12905849,
              'new_log_body_bytes_downloaded':0, 'bags_evaluated':0, 'prediction_rows':0, 'not_executed_result_rows':9,
              'remaining_blockers':['CURRENT_EXPLICIT_DOWNLOAD_AUTHORIZATION_MISSING','RAW_PAYLOADS_NOT_ACQUIRED','SCRIPT_INDEPENDENCE_UNRESOLVED','EXTERNAL_GTE_FEATURES_UNAVAILABLE','ONE_BAG_ONE_LABEL_LIMITED_COVERAGE']}
    (E / 'QUALIFICATION_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','qualification','scientific_state','payload_bytes_requested','new_log_body_bytes_downloaded','bags_evaluated']}))


if __name__ == '__main__':
    main()
