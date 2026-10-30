"""Create fixed instance metadata and scoped authorization request; no network or logs."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

R = Path(__file__).resolve().parent.parent
E = R / 'external_dataset'
COMMIT = '671f9f5b065f03a5502db07c20f1fe3f620d29d9'
INSTANCE = 'cc9b25e1-efc9-11eb-926b-550bf0943fbb'
PREFIX = 'datasets/attack_techniques/T1003.003/atomic_red_team/'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    receipts = json.loads((E / 'metadata/SOURCE_RECEIPTS.json').read_text())
    files = []
    for name in ['windows-sysmon', '4688_windows-security', 'crowdstrike_falcon']:
        pointer = (E / f'metadata/{name}.lfs').read_text()
        oid = next(x.split(':')[1] for x in pointer.splitlines() if x.startswith('oid sha256:'))
        size = int(next(x.split()[1] for x in pointer.splitlines() if x.startswith('size ')))
        path = PREFIX + name + '.log'
        files.append({'name': name + '.log', 'repository_path': path, 'bytes': size,
                      'sha256': oid, 'git_blob_pointer_sha1': next(x['git_blob_sha1'] for x in receipts['receipts'] if x['file'] == name + '.lfs'),
                      'metadata_url': f'https://github.com/splunk/attack_data/blob/{COMMIT}/{path}',
                      'download_url': f'https://media.githubusercontent.com/media/splunk/attack_data/{COMMIT}/{path}',
                      'local_destination': str(E / 'raw' / (name + '.log'))})
    total = sum(x['bytes'] for x in files)
    metadata_files = []
    for p in sorted((E / 'metadata').iterdir()):
        if p.is_file():
            metadata_files.append({'path': str(p.relative_to(R)), 'bytes': p.stat().st_size, 'sha256': sha256(p)})
    grant = {'task': 'R3_OPEN_VOCAB_TECHNIQUE_GENERALIZATION01', 'authorized': False,
             'status': 'PENDING_EXPLICIT_USER_DOWNLOAD_AUTHORIZATION', 'dataset_id': INSTANCE,
             'repository': 'splunk/attack_data', 'commit': COMMIT, 'files': files,
             'total_payload_bytes': total, 'maximum_bags': 1, 'label_unit': 'DATASET_LEVEL_BAG',
             'declared_subtechniques': ['T1003.003'], 'parent_techniques': ['T1003'],
             'license': 'Apache-2.0', 'license_sha256': sha256(E / 'metadata/LICENSE'),
             'license_url': f'https://github.com/splunk/attack_data/blob/{COMMIT}/LICENSE',
             'allowed_action_if_approved': 'Download only three exact public LFS objects; hash verify; local static parsing, annotation stripping, and one-Bag feasibility audit. No execution of captured commands.',
             'not_included': ['GPU or server operation', 'new model downloads', 'new training', 'LLM calls', 'upload of raw logs or Gold', 'repository clone', 'other logs or archives'],
             'qualification_now': 'E0', 'qualification_after_download': 'Conditional E1 feasibility; E2 not promised',
             'payload_endpoints_tested': False, 'payload_endpoint_note': 'Fixed-commit GitHub media URL constructed from verified path; actual availability and payload hashes checked only after explicit authorization.',
             'metadata_files': metadata_files}
    (E / 'EXTERNAL_DOWNLOAD_AUTHORIZATION_REQUEST.json').write_text(json.dumps(grant, ensure_ascii=False, indent=2) + '\n')
    rows = '\n'.join(f"| {x['name']} | {x['bytes']:,} | `{x['sha256']}` |" for x in files)
    urls = '\n'.join(f"- [{x['name']}]({x['download_url']}) → `{x['local_destination']}`" for x in files)
    request = f'''# 单实例公开日志下载授权请求

状态：等待本轮明确授权；未下载任何日志正文。仅申请固定 commit `{COMMIT}` 的 Splunk Attack Data 实例 `{INSTANCE}`，三个 YAML 声明传感器合并为 **1 个 Bag**。

| 文件 | 字节 | 必须匹配的 LFS SHA256 |
|---|---:|---|
{rows}

合计 **{total:,} bytes**（约 {total/1024/1024:.2f} MiB）。不拉取仓库、ZIP、同目录其他日志。下载目标为本项目 `external_dataset/raw/`。以下是由已核实路径构造的固定 commit LFS media URL；尚未请求正文，实际可用性须授权后验证。

{urls}

根 [LICENSE](https://github.com/splunk/attack_data/blob/{COMMIT}/LICENSE) 实读为 Apache-2.0，SHA256 `{grant['license_sha256']}`。已查看根、datasets、attack_techniques、T1003.003、atomic_red_team 五级目录，无更近 LICENSE/NOTICE；仅根有 LICENSE。研究副本保留许可及出处，修改后的派生输入显式注明变更。本次读取公开元数据，不执行日志内命令。

必要性：只有真实日志取得并核对哈希，才能验证 Bag 边界、处理格式、标签泄漏及执行/脚本依赖。YAML 的 T1003.003 是整个实例声明，不能复制为每条日志 Gold；三个传感器不是三个独立执行。此次仅为有界数据准入与本地静态可行性工作，不含服务器、GPU、新模型、新训练、LLM 或数据上传。主融合的外部 GTE 向量仍缺失，不能在未取得真实向量时填主模型成绩。

取得三个对象后仍不自动成为 E2：单类单 Bag 不能证明216类泛化；与 CAM-LDS 的脚本独立性、日志内规则标签、实际解析边界均需核验。当前 E0 / EXTERNAL_TEST_NOT_READY。

授权要求来源：用户本轮附件 §14.5 写明“只有存在明确下载授权时才执行”；§20.2 写明旧授权“不自动扩展至本轮”。本文件的 authorized=false 不代表拒绝，仅表示尚无本轮日志下载授权。
'''
    (E / 'EXTERNAL_DOWNLOAD_AUTHORIZATION_REQUEST.md').write_text(request)
    columns = ['dataset_id','repository','commit','qualification','label_unit','bag_count','declared_subtechnique','parent_technique','log_files','payload_bytes','license','logs_acquired','script_independence','external_prediction_count','reason']
    with (R / 'EXTERNAL_DATA_INSTANCE_REGISTER.csv').open('w', newline='') as out:
        w = csv.DictWriter(out, fieldnames=columns); w.writeheader()
        w.writerow(dict(zip(columns, [INSTANCE,'splunk/attack_data',COMMIT,'E0','DATASET_LEVEL_BAG',1,'T1003.003','T1003',';'.join(x['name'] for x in files),total,'Apache-2.0',False,'UNRESOLVED',0,'New payload download requires explicit current authorization; raw logs and external GTE embeddings unavailable'])))
    (R / 'EXTERNAL_EVALUATION_PREDICTIONS.jsonl').write_text('')
    with (R / 'EXTERNAL_EVALUATION_RESULTS.csv').open('w', newline='') as out:
        columns = ['dataset_id','qualification','method','evaluation_unit','evaluated_bags','top1','top5','top10','mrr10','status','reason']
        w=csv.DictWriter(out,fieldnames=columns);w.writeheader()
        for method in ['Z0_FROZEN_GTE','S0_B3','C0_TRAIN_FREQUENCY','C1_SEEN_BIAS','C2_RRF','C3_SCORE_FUSION','C4_RESIDUAL','C5_FREQUENCY_GTE','B2_CPU_FEASIBILITY']:
            w.writerow(dict(zip(columns,[INSTANCE,'E0',method,'DATASET_LEVEL_BAG',0,'N/A','N/A','N/A','N/A','NOT_EXECUTED','No authorized raw logs; GTE methods also need new external embeddings not presently authorized'])))
    print(json.dumps({'payload_bytes_requested':total,'log_bodies_acquired':0,'qualification':'E0','download_request':str(E / 'EXTERNAL_DOWNLOAD_AUTHORIZATION_REQUEST.md')}))


if __name__ == '__main__':
    main()
