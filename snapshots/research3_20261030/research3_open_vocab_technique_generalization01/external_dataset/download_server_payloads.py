"""Download three explicitly authorized fixed public objects on the named server.

No archive extraction, package installation, command execution, or model loading.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.request
from pathlib import Path

E = Path(__file__).resolve().parent
EXPECTED = Path('/home/tianxiaodan/code/ATT/R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION01/external_dataset')
COMMIT = '671f9f5b065f03a5502db07c20f1fe3f620d29d9'
PREFIX = f'https://media.githubusercontent.com/media/splunk/attack_data/{COMMIT}/datasets/attack_techniques/T1003.003/atomic_red_team/'
ALLOW = {
    'windows-sysmon.log': (12883992, 'ee1c7cd9fa20013c82da17f8cb1998197c117ab4c209ab56203290bc90739fda'),
    '4688_windows-security.log': (11176, '81e1d4e381f4dc38b97c48f9fa5b0ab0b098810c321b7d4599029a9f22530259'),
    'crowdstrike_falcon.log': (10681, 'c4275ab0ef976b0d00ba7840031a06d9f47d1beeaf4c3056d2fc7bb8fe08b38a'),
}


class ExactOriginRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if newurl != req.full_url:
            raise ValueError('Unexpected redirect outside exact authorized URL')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if E != EXPECTED:
        raise SystemExit('This downloader is restricted to the explicitly authorized server project path')
    started = time.monotonic()
    manifest_path = E / 'SERVER_DOWNLOAD_MANIFEST.json'
    manifest = json.loads(manifest_path.read_text())
    grant = json.loads((E / 'SERVER_DOWNLOAD_AUTHORIZATION.json').read_text())
    if grant.get('authorized') is not True or grant.get('request_sha256') != digest(manifest_path.read_bytes()):
        raise SystemExit('Explicit exact-manifest authorization absent')
    for item in grant['code_files']:
        if digest((E / item['name']).read_bytes()) != item['sha256']:
            raise ValueError('Authorized code hash mismatch')
    if {x['name'] for x in manifest['files']} != set(ALLOW):
        raise ValueError('File allowlist mismatch')
    raw = E / 'raw'; raw.mkdir(exist_ok=True)
    if raw.is_symlink():
        raise ValueError('Raw directory must not be a symlink')
    opener = urllib.request.build_opener(ExactOriginRedirect())
    receipts = []
    for item in manifest['files']:
        name = item['name']; size, sha = ALLOW[name]
        path = raw / name
        if item['bytes'] != size or item['sha256'] != sha or item['download_url'] != PREFIX + name or item['local_destination'] != str(path):
            raise ValueError('Exact file contract mismatch')
        if path.is_symlink():
            raise ValueError('Existing payload is a symlink')
        existed = path.exists()
        if existed:
            if path.stat().st_size != size or digest(path.read_bytes()) != sha:
                raise ValueError('Existing payload differs; refusing to overwrite')
        else:
            temp = path.with_suffix(path.suffix + '.partial')
            h = hashlib.sha256(); count = 0
            try:
                request = urllib.request.Request(item['download_url'], headers={'User-Agent':'R3-Scientific-Data-Audit/1.0'})
                with opener.open(request, timeout=40) as response, temp.open('xb') as target:
                    if response.status != 200 or response.geturl() != item['download_url']:
                        raise ValueError('Unexpected HTTP response or URL')
                    while True:
                        if time.monotonic() - started > 600:
                            raise ValueError('600-second request limit exceeded')
                        block = response.read(min(1024 * 128, size + 1 - count))
                        if not block:
                            break
                        count += len(block)
                        if count > size:
                            raise ValueError('Payload larger than frozen size')
                        h.update(block); target.write(block)
                    target.flush(); os.fsync(target.fileno())
                if count != size or h.hexdigest() != sha:
                    raise ValueError('Downloaded payload size or SHA256 mismatch')
                os.replace(temp, path)
            except Exception:
                if temp.exists() and not temp.is_symlink():
                    temp.unlink()
                raise
        receipts.append({'name':name, 'server_path':str(path), 'bytes':size, 'sha256':sha, 'verified':True, 'reused_existing_exact_file':existed, 'source_url':item['download_url']})
    result = {'status':'THREE_EXACT_PUBLIC_LOGS_ACQUIRED_AND_HASH_VERIFIED', 'host':'10.109.119.118', 'files':receipts, 'total_payload_bytes':sum(x['bytes'] for x in receipts), 'elapsed_seconds':time.monotonic()-started, 'download_scope':'3 fixed objects only', 'raw_logs_returned_to_local':False, 'model_calls':0, 'gpu_calls':0, 'training_runs':0, 'llm_calls':0, 'packages_installed':0, 'captured_commands_executed':0, 'authorization_request_sha256':grant['request_sha256']}
    (E / 'SERVER_DOWNLOAD_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'bytes':result['total_payload_bytes'],'elapsed_seconds':result['elapsed_seconds']}))


if __name__ == '__main__':
    main()
