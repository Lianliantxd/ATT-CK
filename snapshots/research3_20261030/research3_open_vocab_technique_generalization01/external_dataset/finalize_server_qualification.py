"""Audit downloaded server receipts and finalize data-admission facts, no model calls."""
import csv,hashlib,json,shutil
from pathlib import Path
E=Path(__file__).resolve().parent;R=E.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def main():
 m=json.loads((E/'SERVER_DOWNLOAD_MANIFEST.json').read_text());g=json.loads((E/'SERVER_DOWNLOAD_AUTHORIZATION.json').read_text())
 d=json.loads((E/'server_receipts/SERVER_DOWNLOAD_RECEIPT.json').read_text());a=json.loads((E/'server_receipts/PREPROCESS_AUDIT.json').read_text())
 assert g['authorized'] and g['request_sha256']==sha(E/'SERVER_DOWNLOAD_MANIFEST.json')==d['authorization_request_sha256']
 assert d['status']=='THREE_EXACT_PUBLIC_LOGS_ACQUIRED_AND_HASH_VERIFIED'
 expected={x['name']:x for x in m['files']};assert len(expected)==3
 assert sum(x['bytes'] for x in d['files'])==d['total_payload_bytes']==12905849
 for x in d['files']:
  exp=expected[x['name']];assert x['verified'] and x['bytes']==exp['bytes'] and x['sha256']==exp['sha256'] and x['server_path']==exp['local_destination']
 assert {x['name'] for x in a['inputs']}==set(expected)
 for x in a['inputs']:assert x['sha256']==expected[x['name']]['sha256'] and x['bytes']==expected[x['name']]['bytes'] and x['unparsed_xml_residual_bytes']==0
 assert sum(x['records'] for x in a['inputs'])==7023 and a['bag_count']==1 and a['event_level_gold_created']==a['commands_executed']==a['model_calls']==0
 assert not list((E/'raw').glob('*'))
 for c in g['code_files']:assert sha(E/c['name'])==c['sha256']
 # These SHA256 were read from successful SSH stdout; they are not a downloaded
 # extra receipt and do not imply local access to any raw or derived log body.
 stdout={
 'SERVER_DOWNLOAD_AUTHORIZATION.json':{'bytes':1427,'sha256':'470bb2cc313480163ecb3297dcbc5e0387197f36bbe27699a3266fb444b12e88'},
 'SERVER_DOWNLOAD_MANIFEST.json':{'bytes':5557,'sha256':'07d1e522f19ca58abb4bc386c74b170ba312054b19d14c451aa5c6e14b692e77'},
 'SERVER_DOWNLOAD_RECEIPT.json':{'bytes':2266,'sha256':'541d8c1cbe75f5d463a62a06658bb5c6d533b2a9f32c624b12656bec4cb47ff3'},
 'download_server_payloads_v2.py':{'bytes':6599,'sha256':'8a215cbc4c08a3616da89c04133792d064b939e921823ebd8bb1e98883315749'},
 'prepare_server_bag.py':{'bytes':8419,'sha256':'6d8966965a8df1733aaba825f0ba6dd04051d219bf22b31d8c6fa229c11efc36'},
 'processed/BAG_INPUT.jsonl':{'bytes':15236232,'sha256':'5b97effee468ef68851f114391381145ac8355b2b2b47faeedc7a3335bbba1cd'},
 'processed/BAG_REFERENCE.jsonl':{'bytes':235,'sha256':'46411d80dc49361e1c390575222808f97548f630272a208101cc2ff597934f4e'},
 'processed/PREPROCESS_AUDIT.json':{'bytes':1351,'sha256':'801f9899544f62288f00aa1497e2d92ebf1d7bc7e36153c07609c86616601ea7'}}
 for name,entry in stdout.items():
  if name.startswith('processed/BAG_'):continue
  local=E/'server_receipts'/Path(name).name if name in ['SERVER_DOWNLOAD_RECEIPT.json','processed/PREPROCESS_AUDIT.json'] else E/name
  assert local.stat().st_size==entry['bytes'] and sha(local)==entry['sha256']
 assert stdout['processed/BAG_INPUT.jsonl']['sha256']==a['bag_input_sha256'] and stdout['processed/BAG_REFERENCE.jsonl']['sha256']==a['bag_reference_sha256']
 dump(E/'server_receipts/SERVER_INTEGRITY_STDOUT_CAPTURE.json',{'evidence_type':'TRANSCRIBED_SUCCESSFUL_SSH_STDOUT_NOT_DOWNLOADED_SERVER_FILE','host':'10.109.119.118','objects':stdout,'raw_or_cleaned_log_body_copied_to_local':False})
 old=E/'QUALIFICATION_AUDIT.json';historical=E/'METADATA_ONLY_QUALIFICATION_AUDIT.json'
 if not historical.exists():shutil.copyfile(old,historical)
 q=json.loads(historical.read_text());q.update({'status':'PASS_SERVER_ONLY_ACQUISITION_NO_MODEL_EVALUATION','qualification':'E1_BAG_FEASIBILITY_DATA_READY_NO_MODEL_EVALUATION','scientific_state':'EXTERNAL_TEST_NOT_READY','server_log_body_bytes_acquired':12905849,'local_log_body_bytes_downloaded':0,'new_log_body_bytes_downloaded':12905849,'bags_prepared':1,'bags_evaluated':0,'prediction_rows':0,'records_parsed':7023,'annotation_fields_removed':7015,'technique_id_occurrences_removed':105,'parse_status':a['parse_status'],'server_storage_root':m['server_root'],'remaining_blockers':['SCRIPT_INDEPENDENCE_UNRESOLVED','EXTERNAL_GTE_FEATURES_UNAVAILABLE','ONE_BAG_ONE_LABEL_LIMITED_COVERAGE','LABEL_EXHAUSTIVENESS_UNKNOWN','NO_EXTERNAL_MODEL_EVALUATION'],'request_sha256':g['request_sha256'],'historical_proposal_retained':True,'historical_metadata_audit_path':str(historical.relative_to(R))})
 q['server_receipt_files']=[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted((E/'server_receipts').glob('*.json'))]
 q['finalizer_sha256']=sha(Path(__file__));dump(old,q)
 path=R/'EXTERNAL_DATA_INSTANCE_REGISTER.csv'
 rows=list(csv.DictReader(path.open()));assert len(rows)==1
 rows[0].update({'qualification':q['qualification'],'logs_acquired':'True','reason':'All3 server-only payload hashes verified; one Bag paired; no model evaluation; script independence and label exhaustiveness unresolved','server_root':m['server_root'],'parsed_records':'7023','raw_storage':'SERVER_ONLY'})
 with path.open('w') as out:w=csv.DictWriter(out,list(rows[0]));w.writeheader();w.writerows(rows)
 path=R/'EXTERNAL_EVALUATION_RESULTS.csv';rows=list(csv.DictReader(path.open()))
 for row in rows:row.update({'qualification':q['qualification'],'reason':'Server logs acquired and Bag prepared; authentic external GTE features/model inference not executed; E2 script independence unresolved'})
 with path.open('w') as out:w=csv.DictWriter(out,list(rows[0]));w.writeheader();w.writerows(rows)
 label=(R/'EXTERNAL_LABEL_UNIT_AUDIT.md').read_text().replace('尚未取得日志内容。','三个日志已在用户指定服务器取得并通过大小与SHA256核验，实际解析共7023条记录。')
 label=label.replace('只有未来真实日志审计可以确认剥离是否充分。','本次实际清洗移除7015个注释字段和105处T-ID；这验证了具体规则已执行，不代表所有隐式标签线索都已穷尽排除。')
 label=label.replace('当前缺少授权时在打开原始日志前停止。','服务器生产版本prepare_server_bag.py读取本轮服务器grant，已对真实日志完成静态解析；原prepare_bag.py仍是历史本地入口，其等待授权状态不代表当前server操作未授权。')
 (R/'EXTERNAL_LABEL_UNIT_AUDIT.md').write_text(label)
 report=f'''# 外部数据实例资格：真实服务器取得与Bag配对

**三份真实日志已取得并通过SHA256核验，1个Bag已完成静态配对；主模型外部评价仍未执行。** 数据准入标记E1_BAG_FEASIBILITY_DATA_READY_NO_MODEL_EVALUATION，它只表示数据/接口可行性候选，不表示已经完成E1开发性能评价；独立测试仍EXTERNAL_TEST_NOT_READY。

用户本轮明确回复“保存在服务器上，/home/tianxiaodan/code/ATT/，本地没路径”。据此原始与清洗正文仅保存在`{m['server_root']}/`；本地仅有代码、公开元数据、下载与清洗统计回执，不保存这些日志正文。首次40秒读取超时失败保留在SERVER_DOWNLOAD_FAILURE_V1.json，后续同三对象有界重试成功，下载器实际wall747.45秒。授权、manifest与代码SHA绑定一致。历史提案authorized=false及E0快照保留，不能据此覆盖本轮后续grant；SERVER_DOWNLOAD_MANIFEST内继承的“not_included: GPU or server operation”是原提案文字残留，具体用户服务器目的地授权与当前grant只覆盖下载/静态准入，不包含GPU/模型前向。

| 项目 | 已确认事实与限制 |
|---|---|
| 来源 | splunk/attack_data，固定commit `{m['commit']}`，实例 `{m['dataset_id']}` |
| 真实对象 | Sysmon 12,883,992 bytes；Security 11,176；CrowdStrike 10,681；共12,905,849 bytes，各SHA匹配固定LFS指针 |
| 许可 | 固定根Apache-2.0，五级祖先目录无更近LICENSE/NOTICE；许可与出处随服务器副本保留 |
| 标签 | 官方YAML在实例级声明T1003.003→父T1003，属于216候选；单正类非穷尽Bag标签 |
| 评价单位 | 三传感器合成一个Bag，不把7023条记录或3文件当独立攻击样本 |
| 解析 | Sysmon7010个XML事件、Security8个XML事件、CrowdStrike5个NDJSON记录；XML未解析残余0 |
| 标签剥离 | 移除7015注释字段、105处技术ID；模型输入使用中性Bag及传感器ID，参考文件隔离 |
| 派生输入 | 服务器processed/BAG_INPUT.jsonl，15,236,232 bytes，SHA `{a['bag_input_sha256']}` |
| 配对参考 | 服务器processed/BAG_REFERENCE.jsonl，235 bytes，SHA `{a['bag_reference_sha256']}` |
| 解析资格 | STRUCTURE_PARSED_NOT_SEMANTICALLY_VALIDATED，不宣称隐式标签线索全部消除 |
| 脚本/执行独立性 | UNRESOLVED；没有此次Atomic脚本固定版本或SHA，CAM-LDS对应脚本身份也不完整 |
| 真实模型外评 | 无外部GTE特征，没有运行B3/GTE/融合；预测0行，9个NOT_EXECUTED结果为N/A |

公开元数据与固定许可来自[根LICENSE]({m['license_url']})、[官方YAML](https://github.com/splunk/attack_data/blob/{m['commit']}/datasets/attack_techniques/T1003.003/atomic_red_team/atomic_red_team.yml)。五个Git blob逐字校验的原审计保留于METADATA_ONLY_QUALIFICATION_AUDIT.json；本轮成功下载的精确对象、来源URL和SHA在server_receipts/SERVER_DOWNLOAD_RECEIPT.json。PREPROCESS_AUDIT.json是实际服务器文件取回；额外SERVER_INTEGRITY_STDOUT_CAPTURE.json明确是成功SSH输出转录，不能冒充第三份服务器原文件。

只运行惰性文本/XML/JSON解析，没有执行日志中的命令，没有新包、模型下载、训练、GPU或LLM。7023个记录没有逐事件Gold。来源只声明一个正类，未来可以报告声明正类的Rank/Hit/MRR；不能将其他候选都当真实FP进而宣称完整多标签Precision/F1。

E2仍缺执行/脚本依赖核验、可靠的多技术覆盖和真实完整预测。这个单类单Bag即使进一步完成模型前向，也只能作为有限迁移测例，不能证明216类总体泛化。用户下载/静态准入授权不自动涵盖新GTE前向；当前不另开模型预算。

OTRF/Mordor继承原审计，计划字节差异、已曝光APT29派生、步骤映射及许可文本冲突仍在；本轮没有读其日志或重编号TEST。原研究目录保持只读。
'''
 (R/'EXTERNAL_DATASET_QUALIFICATION.md').write_text(report)
 print('SERVER_BAG_QUALIFICATION_PASS',q['qualification'],12905849,7023)
if __name__=='__main__':main()
