"""Inert local Bag preparation, gated by an explicit grant and exact payload hashes.

This script has no network/subprocess/model code. Test strings are parser fixtures,
not attack executions, synthetic observations, or evaluation predictions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

E = Path(__file__).resolve().parent
TID = re.compile(r'(?i)(?<![A-Za-z0-9])T\d{4}(?:\.\d{3})?(?![A-Za-z0-9])')
EXCLUDED_FIELDS = {'rulename','rule_name','ruleid','rule_id','mitre','mitre_technique','mitre_techniques','technique','technique_id','technique_name','attack_technique','attack_technique_id','signature','signatureid','signature_id','testname','test_name','testnumber','test_number','testguid','test_guid'}
EVENT = re.compile(r'<Event(?:\s[^>]*)?>.*?</Event\s*>', re.DOTALL)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def field_name(key: str) -> str:
    return key.rsplit('}', 1)[-1].lower()


def clean_string(value: str, audit: dict[str, int]) -> str:
    result, n = TID.subn('[ANNOTATION_ID_REMOVED]', value)
    audit['technique_id_occurrences_removed'] += n
    return result


def clean_object(value: Any, audit: dict[str, int]) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if field_name(str(key)) in EXCLUDED_FIELDS:
                audit['annotation_fields_removed'] += 1
            else:
                result[clean_string(str(key), audit)] = clean_object(item, audit)
        return result
    if isinstance(value, list):
        return [clean_object(item, audit) for item in value]
    if isinstance(value, str):
        return clean_string(value, audit)
    return value


def clean_xml(value: str, audit: dict[str, int]) -> str:
    if '<!DOCTYPE' in value.upper() or '<!ENTITY' in value.upper():
        raise ValueError('XML DTD/entity declarations forbidden')
    root = ET.fromstring(value)
    for parent in root.iter():
        for child in list(parent):
            name = field_name(child.tag)
            data_name = field_name(child.attrib.get('Name', child.attrib.get('name', '')))
            if name in EXCLUDED_FIELDS or data_name in EXCLUDED_FIELDS:
                parent.remove(child)
                audit['annotation_fields_removed'] += 1
        for key in list(parent.attrib):
            if field_name(key) in EXCLUDED_FIELDS:
                del parent.attrib[key]
                audit['annotation_fields_removed'] += 1
    return clean_string(ET.tostring(root, encoding='unicode'), audit)


def parse_records(text: str, audit: dict[str, int]) -> tuple[str, list[str], int]:
    # No external entity expansion, even if declaration lies outside Event blocks.
    if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():
        raise ValueError('XML DTD/entity declarations forbidden')
    matches = list(EVENT.finditer(text))
    if matches:
        residual = EVENT.sub('', text).strip()
        return 'XML_EVENT_STREAM', [clean_xml(x.group(), audit) for x in matches], len(residual.encode())
    try:
        whole = json.loads(text)
    except json.JSONDecodeError:
        whole = None
    if whole is not None:
        items = whole if isinstance(whole, list) else [whole]
        return 'JSON', [json.dumps(clean_object(x, audit), ensure_ascii=False, sort_keys=True) for x in items], 0
    lines = [x for x in text.splitlines() if x.strip()]
    parsed = []
    for line in lines:
        try:
            parsed.append(json.loads(line))
        except json.JSONDecodeError:
            return 'TEXT_LINES_UNRESOLVED_EVENT_BOUNDARIES', [clean_string(x, audit) for x in lines], 0
    return 'NDJSON', [json.dumps(clean_object(x, audit), ensure_ascii=False, sort_keys=True) for x in parsed], 0


def self_test() -> None:
    a = {'annotation_fields_removed': 0, 'technique_id_occurrences_removed': 0}
    xml = '<Event><EventData><Data Name="RuleName">T1003.003 tag</Data><Data Name="Image">C:\\example.exe</Data></EventData></Event>'
    x = clean_xml(xml, a)
    assert 'RuleName' not in x and 'example.exe' in x and a['annotation_fields_removed'] == 1
    x = clean_object({'mitre_technique': 'T1003.003', 'message': 'opaque T1003 marker', 'nested': [{'RuleName': 'known'}]}, a)
    assert 'mitre_technique' not in x and not TID.search(json.dumps(x))
    try:
        parse_records('<!DOCTYPE e [<!ENTITY x "y">]><Event/>', a)
    except ValueError:
        pass
    else:
        raise AssertionError('DTD accepted')
    assert parse_records('{"message":"a"}\n{"message":"b"}', a)[0] == 'NDJSON'
    print('PASS: parser fixtures; no real logs read and no predictions generated')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test(); return
    request = json.loads((E / 'SERVER_DOWNLOAD_MANIFEST.json').read_text())
    grant_path = E / 'SERVER_DOWNLOAD_AUTHORIZATION.json'
    if not grant_path.is_file():
        raise SystemExit('BLOCKED: explicit current SERVER_DOWNLOAD_AUTHORIZATION.json absent; no raw log opened')
    grant = json.loads(grant_path.read_text())
    if grant.get('authorized') is not True or grant.get('request_sha256') != digest((E / 'SERVER_DOWNLOAD_MANIFEST.json').read_bytes()):
        raise SystemExit('BLOCKED: grant missing or not bound to exact scoped request; no raw log opened')
    # Validate paths and byte counts for all three entries before reading any body.
    for entry in request['files']:
        p = Path(entry['local_destination'])
        if p.parent.resolve() != (E / 'raw').resolve() or p.name != entry['name'] or p.is_symlink():
            raise ValueError('Unexpected payload path or symlink')
        if not p.is_file() or p.stat().st_size != entry['bytes']:
            raise ValueError('Missing payload or byte count mismatch')
    audit: dict[str, Any] = {'annotation_fields_removed': 0, 'technique_id_occurrences_removed': 0, 'inputs': [], 'bag_count': 1, 'event_level_gold_created': 0, 'commands_executed': 0, 'model_calls': 0}
    records = []
    for index, entry in enumerate(request['files']):
        p = Path(entry['local_destination']); blob = p.read_bytes()
        if digest(blob) != entry['sha256']:
            raise ValueError('Payload SHA256 mismatch')
        text = blob.decode('utf-8-sig', errors='strict')
        fmt, items, residual_bytes = parse_records(text, audit)
        audit['inputs'].append({'name': p.name, 'sha256': digest(blob), 'bytes': len(blob), 'format': fmt, 'records': len(items), 'unparsed_xml_residual_bytes': residual_bytes})
        records.extend({'sensor_view_id': f'S{index+1}', 'record_id': f'S{index+1}-{j:08d}', 'text': item} for j,item in enumerate(items))
    if any(x['unparsed_xml_residual_bytes'] > 0 or 'UNRESOLVED' in x['format'] for x in audit['inputs']):
        audit['parse_status'] = 'NEEDS_MANUAL_BOUNDARY_REVIEW'
    else:
        audit['parse_status'] = 'STRUCTURE_PARSED_NOT_SEMANTICALLY_VALIDATED'
    audit['scientific_qualification'] = 'E1_FEASIBILITY_CANDIDATE_ONLY; script independence unresolved; model input budget and inference not yet qualified'
    output = {'bag_id': 'EXTERNAL_BAG_001', 'records': records}
    serialized = json.dumps(output, ensure_ascii=False)
    assert not TID.search(serialized)
    processed = E / 'processed'; processed.mkdir(exist_ok=True)
    (processed / 'BAG_INPUT.jsonl').write_text(serialized + '\n')
    # Reference is separated and never concatenated into model input.
    reference = {'bag_id': 'EXTERNAL_BAG_001', 'source_dataset_id': request['dataset_id'], 'declared_parent_labels': request['parent_techniques'], 'label_exhaustiveness': 'UNKNOWN', 'label_unit': 'DATASET_LEVEL_BAG', 'source_positive_label_only': True}
    (processed / 'BAG_REFERENCE.jsonl').write_text(json.dumps(reference) + '\n')
    audit['bag_input_sha256'] = digest((processed / 'BAG_INPUT.jsonl').read_bytes())
    audit['bag_reference_sha256'] = digest((processed / 'BAG_REFERENCE.jsonl').read_bytes())
    (processed / 'PREPROCESS_AUDIT.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'records':len(records),'bags':1,'parse_status':audit['parse_status']}))


if __name__ == '__main__':
    main()
