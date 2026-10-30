"""Transport-resilient revision: same three authorized files and hashes, server only."""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

E = Path(__file__).resolve().parent
EXPECTED = Path('/home/tianxiaodan/code/ATT/R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION01/external_dataset')
COMMIT = '671f9f5b065f03a5502db07c20f1fe3f620d29d9'
PREFIX = f'https://media.githubusercontent.com/media/splunk/attack_data/{COMMIT}/datasets/attack_techniques/T1003.003/atomic_red_team/'
ALLOW = {
    '4688_windows-security.log': (11176, '81e1d4e381f4dc38b97c48f9fa5b0ab0b098810c321b7d4599029a9f22530259'),
    'crowdstrike_falcon.log': (10681, 'c4275ab0ef976b0d00ba7840031a06d9f47d1beeaf4c3056d2fc7bb8fe08b38a'),
    'windows-sysmon.log': (12883992, 'ee1c7cd9fa20013c82da17f8cb1998197c117ab4c209ab56203290bc90739fda'),
}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Redirect outside exact authorized URL refused')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if E != EXPECTED:
        raise SystemExit('Restricted to authorized server destination')
    start = time.monotonic()
    mpath = E / 'SERVER_DOWNLOAD_MANIFEST.json'
    m = json.loads(mpath.read_text())
    g = json.loads((E / 'SERVER_DOWNLOAD_AUTHORIZATION.json').read_text())
    assert g.get('authorized') is True and g['request_sha256'] == sha(mpath.read_bytes())
    for c in g['code_files']:
        assert sha((E / c['name']).read_bytes()) == c['sha256']
    assert {x['name'] for x in m['files']} == set(ALLOW)
    entries = {x['name']:x for x in m['files']}
    raw = E / 'raw'; raw.mkdir(exist_ok=True)
    assert not raw.is_symlink()
    opener = urllib.request.build_opener(NoRedirect())
    receipts = []; transport = []
    for name, (size, wanted) in ALLOW.items():
        entry = entries[name]; path = raw / name
        assert entry['bytes'] == size and entry['sha256'] == wanted
        assert entry['download_url'] == PREFIX + name and entry['local_destination'] == str(path)
        assert not path.is_symlink()
        reused = path.exists()
        if reused:
            assert path.stat().st_size == size and sha(path.read_bytes()) == wanted
        else:
            temp = path.with_suffix('.log.partial')
            assert not temp.is_symlink()
            for attempt in range(1,4):
                if time.monotonic() - start > 1800:
                    raise ValueError('1800-second bounded transport window exceeded')
                offset = temp.stat().st_size if temp.exists() else 0
                if offset > size:
                    raise ValueError('Partial is larger than authorized object')
                if offset == size:
                    break
                headers = {'User-Agent':'R3-Scientific-Data-Audit/1.0'}
                if offset:
                    headers['Range'] = f'bytes={offset}-'
                request = urllib.request.Request(entry['download_url'], headers=headers)
                try:
                    with opener.open(request, timeout=180) as response:
                        if response.geturl() != entry['download_url']:
                            raise ValueError('Unexpected response URL')
                        if offset:
                            cr = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', response.headers.get('Content-Range',''))
                            if response.status != 206 or not cr or tuple(map(int,cr.groups())) != (offset,size-1,size):
                                raise ValueError('Exact Content-Range required for safe resume')
                        elif response.status != 200:
                            raise ValueError('Unexpected initial response status')
                        with temp.open('ab' if offset else 'xb') as output:
                            count = offset
                            while True:
                                if time.monotonic()-start > 1800:
                                    raise ValueError('Transport time bound exceeded')
                                block = response.read(min(65536,size+1-count))
                                if not block:
                                    break
                                count += len(block)
                                if count > size:
                                    raise ValueError('Payload size bound exceeded')
                                output.write(block)
                            output.flush();os.fsync(output.fileno())
                        if count != size:
                            raise OSError('Incomplete response')
                    break
                except (TimeoutError, ConnectionError, OSError, urllib.error.URLError) as error:
                    transport.append({'file':name,'attempt':attempt,'resume_offset_before':offset,'retained_partial_bytes':temp.stat().st_size if temp.exists() else 0,'failure_type':type(error).__name__})
                    (E/'TRANSPORT_RETRIES.json').write_text(json.dumps(transport,indent=2)+'\n')
                    print(json.dumps(transport[-1]),flush=True)
                    if attempt == 3:
                        raise
            if temp.stat().st_size != size or sha(temp.read_bytes()) != wanted:
                raise ValueError('Full payload size/SHA256 qualification failed')
            os.replace(temp,path)
        receipts.append({'name':name,'server_path':str(path),'bytes':size,'sha256':wanted,'verified':True,'reused_existing_exact_file':reused,'source_url':entry['download_url']})
        print(json.dumps({'file':name,'bytes':size,'sha256_verified':True}),flush=True)
    result={'status':'THREE_EXACT_PUBLIC_LOGS_ACQUIRED_AND_HASH_VERIFIED','host':'10.109.119.118','files':receipts,'total_payload_bytes':sum(x['bytes'] for x in receipts),'elapsed_seconds':time.monotonic()-start,'download_scope':'3 fixed objects only; bounded same-object transport retries','raw_logs_returned_to_local':False,'model_calls':0,'gpu_calls':0,'training_runs':0,'llm_calls':0,'packages_installed':0,'captured_commands_executed':0,'authorization_request_sha256':g['request_sha256'],'transport_retries':transport}
    (E/'SERVER_DOWNLOAD_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'bytes':result['total_payload_bytes'],'elapsed_seconds':result['elapsed_seconds']}),flush=True)


if __name__=='__main__':
    main()
