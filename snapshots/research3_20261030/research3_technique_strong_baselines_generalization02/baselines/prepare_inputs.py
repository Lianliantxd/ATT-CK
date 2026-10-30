import gzip,hashlib,json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def stype(path):
 s=path.lower()
 if 'audit' in s:return 'audit'
 if 'auth' in s or 'secure' in s:return 'authentication'
 if 'wazuh' in s or 'alerts/alerts' in s:return 'wazuh'
 if 'suricata' in s or 'eve.json' in s:return 'suricata'
 if 'access.log' in s:return 'web_access'
 if any(x in s for x in ['syslog','daemon.log','kern.log','messages']):return 'system'
 if any(x in s for x in ['apache','error.log','nextcloud','docker','mail','puppet','zoneminder','ftp']):return 'application'
 return 'other'
def segment(text):
 host='';sources=[];current=None
 for line in text.splitlines():
  if line and not line.startswith(' ') and line.endswith(':'):
   host=line[:-1];continue
  if line.startswith('    ') and not line.startswith('        ') and line.endswith(':'):
   path=line.strip()[:-1];current={'source_id':host+'/'+path,'source_type':stype(path),'lines':[]};sources.append(current);continue
  if current is None:continue
  if line.startswith('        '):
   current['lines'].append({'line_id':'L'+str(len(current['lines'])),'text':line[8:]})
  elif current['lines']:current['lines'][-1]['text']+='\n'+line
 for source in sources:
  for row in source['lines']:row['text_hash']=hashlib.sha256(row['text'].encode()).hexdigest()
 return sources

def main():
 qs=[json.loads(x) for x in (R/'frozen_p0/STEP_LEVEL_DATASET.jsonl').read_text().splitlines()]
 with (R/'datasets/p0_prediction.jsonl').open('w') as out,(R/'datasets/p0_reference.jsonl').open('w') as ref:
  for q in qs:
   out.write(json.dumps({'sample_id':q['sample_id'],'text':q['strict_log_content'],'sources':segment(q['strict_log_content'])})+'\n')
   ref.write(json.dumps({'sample_id':q['sample_id'],'ground_truth':q['official_technique_labels'],'scenario_id':q['scenario_id'],'step_id':q['step_id'],'simulation_id':q['simulation_id'],'variant_id':q['variant_id'],'sampling_replica_id':q['sampling_replica_id'],'input_hash':hashlib.sha256(q['strict_log_content'].encode()).hexdigest()})+'\n')
 matrix=json.loads((R.parent/'research3_attack_technique_benchmark01/official_sources/mitre_matrix.json').read_text());ids=sorted({k.split('.')[0] for k in matrix});K0={k:[] for k in ids};tactics={k:[] for k in ids}
 for k,v in matrix.items():K0[k.split('.')[0]].append(v['name']);tactics[k.split('.')[0]].extend(v['tactics'])
 K0={k:' '.join(v) for k,v in K0.items()};K1=json.loads((R/'frozen_p0/datasets/official_knowledge_documents.json').read_text());K2=json.loads((R/'frozen_p0/datasets/extended_knowledge_documents.json').read_text());K3={k:' '.join(tactics[k]) for k in ids};covered=set()
 p=R.parent/'provenance_baserepro_04/data/enterprise-attack-16.1.json.gz';stix=json.load(gzip.open(p,'rt'))
 for obj in stix['objects']:
  if obj.get('type')!='attack-pattern' or obj.get('revoked') or obj.get('x_mitre_deprecated'):continue
  for x in obj.get('external_references',[]):
   if x.get('source_name')!='mitre-attack':continue
   k=x.get('external_id','').split('.')[0]
   if k in K3:K3[k]+=' '+obj.get('description','');covered.add(k)
 for name,value in [('K0_NAMES_ONLY',K0),('K1_NAMES_AND_TACTICS',K1),('K2_DESCRIPTION_16_1',K2),('K3_DESCRIPTION_16_1_WITHOUT_TITLES',K3),('K4_COMMON_COVERAGE_203',{k:K2[k] for k in sorted(covered)})]:
  (R/'knowledge'/(name+'.json')).write_text(json.dumps(value))
 (R/'knowledge/COVERAGE.json').write_text(json.dumps({'full_candidates':ids,'covered':sorted(covered),'missing':sorted(set(ids)-covered),'version':'existing16.1','source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2))
 print('prepared',len(qs),'candidates',len(ids),'covered',len(covered))
if __name__=='__main__':main()
