"""Static audit-hex interpretation only; never execute decoded content."""
import hashlib
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parents[1]
records = []
for line in (R / 'inputs/VISIBLE_FACT_REGISTRY.jsonl').read_text().splitlines():
    f = json.loads(line)
    for m in re.finditer(r'\b(proctitle|a[0-9]+)=([0-9a-fA-F]+)(?=\s|$)', f['text']):
        name, value = m.groups()
        if name != 'proctitle' and 'type=EXECVE ' not in f['text']:
            # SYSCALL a0/a1 fields are register values/pointers, not encoded
            # command arguments; do not assign text semantics to them.
            continue
        if len(value) < 8:
            continue
        even = value[:len(value) // 2 * 2]
        raw = bytes.fromhex(even)
        try:
            decoded = raw.decode('utf-8')
        except UnicodeDecodeError:
            decoded = None
        records.append({'review_id': f['review_id'], 'sample_id': f['sample_id'],
                        'fact_id': f['fact_id'], 'field': name, 'literal_hex': value,
                        'decode_method': 'bytes.fromhex on complete byte pairs; strict UTF-8',
                        'odd_final_nibble_undecodable': len(value) % 2 != 0,
                        'decoded_utf8': decoded,
                        'nul_separated_components': decoded.split('\x00') if decoded is not None else None,
                        'decoded_bytes_sha256': hashlib.sha256(raw).hexdigest(),
                        'provenance': 'DERIVED_HEX_DECODE_OF_CURRENT_VISIBLE_LINE_NOT_ADDITIONAL_NATIVE_EVENT',
                        'scope': 'only displayed characters; no reconstruction of missing suffix or command execution'})
with (R / 'review/DERIVED_HEX_INTERPRETATIONS.jsonl').open('w') as out:
    for x in records:
        out.write(json.dumps(x, ensure_ascii=False, separators=(',', ':')) + '\n')
print(json.dumps({'derived_fields': len(records), 'odd_length_values': sum(x['odd_final_nibble_undecodable'] for x in records), 'executed_decoded_commands': 0}))
