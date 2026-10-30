"""Metadata-only qualification. Never open a log archive or event-record file."""
from pathlib import Path
import hashlib, json, re, xml.etree.ElementTree as ET, zipfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
WORKSPACE = BASE.parent
PREVIOUS = WORKSPACE / 'research3_attack_mechanism_discrimination01'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def receipt(path):
    content = path.read_bytes()
    return {'path': str(path), 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}

def inspect_plan(path):
    result = receipt(path)
    raw = path.read_bytes()
    result['git_blob_sha1'] = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    result['qualification'] = 'EXPOSED_LOCAL_EMULATION_PLAN_NOT_MATCHED_TO_CURRENT_OFFICIAL_BLOB'
    result['sheets'] = []
    with zipfile.ZipFile(path) as book:
        shared = []
        if 'xl/sharedStrings.xml' in book.namelist():
            shared = [''.join(x.itertext()) for x in ET.fromstring(book.read('xl/sharedStrings.xml')).findall('m:si', NS)]
        for name in book.namelist():
            if not (name.startswith('xl/worksheets/') and name.endswith('.xml')):
                continue
            rows = []
            for row in ET.fromstring(book.read(name)).findall('.//m:row', NS):
                values = {}
                for cell in row.findall('m:c', NS):
                    column = re.match('[A-Z]+', cell.get('r', '')).group()
                    node = cell.find('m:v', NS)
                    value = node.text if node is not None else ''
                    if cell.get('t') == 's' and value:
                        value = shared[int(value)]
                    values[column] = value or ''
                rows.append(values)
            # Only headers and step/technique columns survive. No hands-on bodies.
            result['sheets'].append({
                'sheet_xml': name, 'row_count': len(rows),
                'headers': rows[0] if rows else {},
                'step_technique_rows': [{'step': row.get('C', ''), 'technique_labels': row.get('B', ''), 'technique_ids': sorted(set(re.findall(r'\bT\d{4}(?:\.\d{3})?\b', row.get('B', ''))))} for row in rows[1:]],
            })
    return result

def main():
    prior_file = PREVIOUS / 'external_dataset/LOCAL_SOURCE_QUALIFICATION.json'
    prior = json.loads(prior_file.read_text())
    candidates_file = WORKSPACE / 'research3_attack_technique_benchmark01/datasets/official_knowledge_documents.json'
    candidates = set(json.loads(candidates_file.read_text()))
    plans = [WORKSPACE / 'intent_ig2_work/local_sources/apt29/apt29.xlsx', WORKSPACE / 'research3_active_provenance_r38h_20261010/sources/apt29.xlsx']
    result = {'date_asia_shanghai': '2026-10-28', 'scope': 'PUBLIC_METADATA_AND_LOCAL_EMULATION_PLAN_COLUMNS_ONLY',
              'logs_or_archives_opened': False, 'new_log_downloads': 0, 'external_predictions': 0,
              'inherited_qualification_receipt': receipt(prior_file),
              'candidate_space_receipt': receipt(candidates_file), 'candidate_count': len(candidates),
              'inherited_mordor_derived_steps': prior['Mordor_reference_steps'],
              'inherited_mordor_label_intersection': prior['overlap_216'],
              'inherited_mordor_outside_candidates': prior['outside_216'],
              'local_emulation_plans': [inspect_plan(p) for p in plans if p.exists()],
              'splunk_exact_source_label': 'T1003.003', 'splunk_parent_candidate': 'T1003',
              'splunk_parent_in_216': 'T1003' in candidates,
              'splunk_label_unit': 'DATASET_BAG_NOT_EVENT',
              'external_test_status': 'EXTERNAL_TEST_NOT_READY'}
    for plan in result['local_emulation_plans']:
        labels = {tid for sheet in plan['sheets'] for row in sheet['step_technique_rows'] for tid in row['technique_ids']}
        plan['unique_label_ids'] = sorted(labels)
        plan['direct_parent_id_intersection_216'] = sorted(labels & candidates)
        plan['direct_id_outside_216'] = sorted(labels - candidates)
        plan['official_xlsx_blob_sha1'] = 'e2b95dc306967a6a2d9af033cf1fe7c3ad155c13'
        plan['matches_fixed_official_blob'] = plan['git_blob_sha1'] == plan['official_xlsx_blob_sha1']
        plan['label_column_status'] = 'TECHNIQUE_NAMES_PRESENT_NO_EXPLICIT_T_IDS_IN_LABEL_COLUMN; do not infer an authoritative crosswalk from names or description-body IDs'
    result['saved_public_metadata_receipts'] = [receipt(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name not in {'LOCAL_METADATA_AUDIT.json', 'audit_local_metadata.py', 'QUALIFICATION_DECISION.json', 'METADATA_SOURCE_RECEIPTS.json'}]
    (HERE / 'LOCAL_METADATA_AUDIT.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'candidate_count': len(candidates), 'plans': len(result['local_emulation_plans']), 'splunk_parent_in_216': result['splunk_parent_in_216'], 'external_test_status': result['external_test_status']}))

if __name__ == '__main__':
    main()
