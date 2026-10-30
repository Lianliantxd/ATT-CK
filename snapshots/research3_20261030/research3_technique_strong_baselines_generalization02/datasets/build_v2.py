"""Safe ZIP-only CAM-LDS v2 reader and deterministic fresh-window sampling.
Never imports/runs official script or reads an archive member before metadata allowlisting.
"""
import collections,csv,hashlib,json,random,re,stat,zipfile,ast,io,time
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT.parent/'research3_attack_technique_benchmark01'
ARCH=ROOT.parent/'rp3_existing_data/cam_lds_zenodo_v2/manifestations_filtered.zip'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def sha_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''): h.update(b)
 return h.hexdigest()
def write(f,o):f.write(json.dumps(o,ensure_ascii=False)+'\n')
def source_type(path):
 p=path.lower()
 if '/audit/' in p or p.endswith('nclog/audit.log'):return 'audit'
 if '/auth.log' in p:return 'authentication'
 if '/suricata/' in p:return 'suricata'
 if '/alerts/alerts.json' in p:return 'wazuh'
 if 'access.log' in p or 'puppetserver-access.log' in p:return 'web_access'
 if any(t in p for t in ['/apache2/','/zm/','/nclog/','/exim4/','/squid/','/puppetlabs/','vsftpd','/containers/']):return 'application'
 if any(p.endswith(t) for t in ['syslog','messages','daemon.log','kern.log','debug','cron.log','dpkg.log','cloud-init.log','shorewall-init.log','unattended-upgrades-shutdown.log']):return 'system'
 return 'other'
def hash_sources(sources):
 return SHA(json.dumps([(s['source_type'],[l['text_hash'] for l in s['lines']]) for s in sources],separators=(',',':')).encode())
def view(sample_id,sources):
 return {'sample_id':sample_id,'text':'\n'.join(l['text'] for s in sources for l in s['lines']),'sources':sources}

# Extract only the eight public cleaning pattern literals; never execute API code.
_clean_ast=ast.parse((OLD/'official_sources/get_llm_responses.py').read_text())
OFFICIAL_CLEAN_PATTERNS=[n.args[0].value for n in ast.walk(_clean_ast) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='sub' and n.args and isinstance(n.args[0],ast.Constant)]
assert len(OFFICIAL_CLEAN_PATTERNS)==8
DIRECT_ID=re.compile(r'(?i)T\d{4}(?:[._]\d{3})?')
ANNOTATION_KEY=re.compile(r'"(?:mitre(?:_[a-zA-Z_]+)?|techniques?|tactics?)"\s*:\s*',re.I)
def clean_log(line):
 # Remove nested native JSON annotation values by JSON value boundaries, without
 # serializing behavioral fields or altering their whitespace/number formatting.
 text=line
 while True:
  m=ANNOTATION_KEY.search(text)
  if m is None:break
  try:
   _,length=json.JSONDecoder().raw_decode(text[m.end():]); end=m.end()+length
  except ValueError:
   # Unstructured malformed annotation: eliminate its key only; direct IDs below.
   text=text[:m.start()]+'"annotation_removed":'+text[m.end():];continue
  start=m.start()
  before=text[:start];after=text[end:]
  if before.rstrip().endswith(','):before=before.rstrip()[:-1]
  elif after.lstrip().startswith(','):after=after.lstrip()[1:]
  text=before+after
 for pattern in OFFICIAL_CLEAN_PATTERNS:text=re.sub(pattern,'',text)
 # Literal escaped annotation keys inside payload strings are blocked as fields too.
 text=re.sub(r'(?i)(?:\\*")mitre(?:_[a-z_]+)?(?:\\*")\s*:', '\"annotation_removed\":', text)
 text=DIRECT_ID.sub('[LABEL_REMOVED]',text)
 assert not DIRECT_ID.search(text) and not ANNOTATION_KEY.search(text)
 return text

def main():
 t=time.time(); p0=[json.loads(l) for l in (OLD/'STEP_LEVEL_DATASET.jsonl').open()]
 labels=json.load((OLD/'official_sources/labels.json').open())
 pairs=sorted(set((x['simulation_id'],str(x['step_id'])) for x in p0),key=lambda p:p[0]+'-'+p[1]); allowed=set(pairs)
 assert len(pairs)==385 and all(not (s.split('_')[0]=='1' and st in ['35','36','37']) for s,st in pairs)
 records={}; excluded=collections.Counter(); allowed_members=[]; mapping=[]
 z=zipfile.ZipFile(ARCH); seen=collections.Counter(i.filename for i in z.infolist())
 # No member body reads occur in this loop.
 for i in sorted(z.infolist(),key=lambda i:i.filename):
  n=i.filename; parts=PurePosixPath(n).parts; mode=i.external_attr>>16
  reason=None
  if i.is_dir():reason='DIRECTORY'
  elif n.startswith('/') or '\\' in n or any(x in ['..','.'] for x in n.split('/')):reason='UNSAFE_PATH'
  elif stat.S_ISLNK(mode):reason='SYMLINK'
  elif seen[n]!=1:reason='DUPLICATE_MEMBER_NAME'
  elif len(parts)<6 or parts[:2]!=('manifestations_filtered','steps'):reason='NOT_STEP_LOG'
  else:
   m=re.fullmatch(r'([1-7](?:_[a-zA-Z0-9_]+)?)-(\d+)',parts[2])
   if not m:reason='ACCESS_SCOPE_UNCERTAIN'
   else:
    sim,step=m.groups()
    if sim.split('_')[0]=='1' and int(step) in [35,36,37]:reason='CONV_A01_NOT_AUTHORIZED'
    elif (sim,step) not in allowed:reason='OUTSIDE_FROZEN_P0_EXECUTION_STEP_PAIRS'
    elif 'attacker' in parts[3].lower() or any('attackmate' in q.lower() for q in parts):reason='ATTACKER_CONTROL_MATERIAL'
    elif parts[4]!='logs':reason='NOT_VICTIM_LOG'
    elif parts[-1] in ['output.log','collectd.log']:reason='CONTROL_OR_COLLECTD'
    elif mode & 0o111:reason='EXECUTABLE_MEMBER'
    elif i.file_size>32*1024*1024 or (i.file_size>1024*1024 and i.file_size/max(1,i.compress_size)>1000):reason='ANOMALOUS_SIZE_OR_RATIO'
    elif not (re.search(r'\.(?:log|json)(?:\.\d+)?$',parts[-1]) or parts[-1] in ['syslog','messages','debug','mainlog']):reason='NOT_APPROVED_TEXT_LOG_SUFFIX'
    else:
     host=parts[3]; rel='/'.join(parts[4:]); sid='src_'+SHA(n.encode())[:16]
     row={'member':n,'simulation_id':sim,'step_id':step,'host':host,'relative_path':rel,'source_id':sid,'source_type':source_type(n),'uncompressed_bytes':i.file_size,'crc32':i.CRC}
     allowed_members.append(row); mapping.append((i,row)); continue
  excluded[reason]+=1
 archive_hash=sha_file(ARCH)
 dump(ROOT/'datasets/manifests/ZIP_METADATA_AUDIT.json',{'archive':str(ARCH),'sha256':archive_hash,'total_members':len(z.infolist()),'allowlisted_member_count':len(mapping),'allowlisted_bytes':sum(i.file_size for i,r in mapping),'excluded_counts':dict(excluded),'body_reads_at_audit':0,'rule':'exact P0 execution-step pairs; scenario1 steps35,36,37 denied before body reads','limits':{'member_bytes':33554432,'compression_ratio':1000}})
 with (ROOT/'datasets/manifests/ALLOWLISTED_MEMBERS.jsonl').open('w') as f:
  for row in allowed_members:write(f,row)
 # Only this audited, bounded allowlist may reach z.read(). No extraction.
 cache={}; source_stats=[]; cleaning=collections.Counter()
 for i,row in mapping:
  raw=z.read(i)
  if b'\0' in raw or raw.startswith((b'\x7fELF',b'MZ',b'#!')):raise ValueError('unexpected executable/binary in audited text log')
  # Match official encoding/errors and newline handling using TextIOWrapper.
  lines=[l.rstrip('\n') for l in io.TextIOWrapper(io.BytesIO(raw),encoding='utf-8',errors='ignore',newline=None)]
  ll=[]
  for j,line in enumerate(lines):
   cleaned=clean_log(line)
   cleaning['lines_total']+=1;cleaning['lines_changed']+=int(cleaned!=line)
   cleaning['direct_ids_before']+=len(DIRECT_ID.findall(line));cleaning['direct_ids_after']+=len(DIRECT_ID.findall(cleaned))
   cleaning['mitre_annotation_lines_before']+=int(bool(re.search(r'(?i)mitre[^a-z]',line)))
   ll.append({'line_id':row['source_id']+':'+str(j+1),'text':cleaned,'text_hash':SHA(cleaned.encode()),'raw_text_hash':SHA(line.encode())})
  src={'source_id':row['source_id'],'source_type':row['source_type'],'lines':ll}
  cache.setdefault((row['simulation_id'],row['step_id']),[]).append(src)
  source_stats.append(dict(row,total_lines=len(ll),content_sha256=SHA(raw),decoded_replacement_policy='utf8-ignore; universal-newline'))
 with (ROOT/'datasets/manifests/SOURCE_PROVENANCE.jsonl').open('w') as f:
  for row in source_stats:write(f,row)
 # Match official sample_log_file() core exactly; random consumption over sorted inputs.
 official=ROOT/'datasets/create_llm_prompt_resample_official_42bbd2c.py'
 module=ast.parse(official.read_text()); fun=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='sample_log_file'); env={'random':random};exec(compile(ast.Module(body=[fun],type_ignores=[]),str(official),'exec'),env)
 class MemoryPath:
  def __init__(self,lines):self.lines=lines
  def open(self,*a,**kw):return io.StringIO('\n'.join(self.lines)+'\n')
 # Verify translated contiguous-window operation against official function for representative lengths.
 for n in [1,5,10,11,100,1000]:
  random.seed(42); a=env['sample_log_file'](MemoryPath([str(i) for i in range(n)]),10,'random')
  random.seed(42);start=random.randint(0,n-10) if n>10 else 0
  assert a==[str(i) for i in range(n)][start:start+10]
 def sample(sources,rng):
  out=[]
  for s in sources:
   lines=s['lines'];start=rng.randint(0,len(lines)-10) if len(lines)>10 else 0
   if lines:out.append(dict(s,lines=lines[start:start+10]))
  return out
 def ref(sid,pair,rep,sources):
  sim,step=pair;scenario=sim.split('_')[0];variant=sim.partition('_')[2]
  gold=list(labels[sim+'-'+step]['metadata'])
  assert gold
  return {'sample_id':sid,'ground_truth':sorted(set(t.split('.')[0] for t in gold)),'official_technique_labels':gold,'scenario_id':scenario,'step_id':step,'simulation_id':sim,'variant_id':variant,'sampling_replica_id':rep,'input_hash':hash_sources(sources),'logical_step_id':scenario+'-'+step,'data_version':'CAM-LDS-v2','log_line_count':sum(len(s['lines']) for s in sources)}
 p2hash=[]
 for kind in ['full','sampled']:
  rng=random.Random(42)
  with (ROOT/f'datasets/p2_v2/prediction_{kind}.jsonl').open('w') as pf,(ROOT/f'datasets/p2_v2/reference_{kind}.jsonl').open('w') as rf:
   for index,pair in enumerate(pairs):
    sources=cache.get(pair,[]); sources=sources if kind=='full' else sample(sources,rng)
    sid='v2_'+kind+'_'+f'{index:04d}';rr=ref(sid,pair,0,sources)
    write(pf,view(sid,sources));write(rf,rr)
    if kind=='sampled':p2hash.append(rr['input_hash'])
 # Official ordering: collect all pairs/variants and sample every file, then choose variant per logical step.
 variants={}
 for pair in pairs:
  if any(s['lines'] for s in cache.get(pair,[])):
   key=(pair[0].split('_')[0],pair[1]);variants.setdefault(key,[]).append(pair)
 rng=random.Random(42);p1refs=[]
 with (ROOT/'datasets/p1_resampled/prediction.jsonl').open('w') as pf,(ROOT/'datasets/p1_resampled/reference.jsonl').open('w') as rf:
  for rep in range(5):
   sampled={pair:sample(cache.get(pair,[]),rng) for pair in pairs}
   for index,(key,opts) in enumerate(variants.items()):
    pair=rng.choice(opts);sources=sampled[pair];sid='v2_resample_'+f'{index:03d}'+'_r'+str(rep);rr=ref(sid,pair,rep,sources)
    write(pf,view(sid,sources));write(rf,rr);p1refs.append(rr)
 # Additional paired-variant control: each P0 record's exact simulation is frozen, fresh windows only.
 rng=random.Random(42);fixedrefs=[]
 with (ROOT/'datasets/p1_resampled/prediction_fixed_variant.jsonl').open('w') as pf,(ROOT/'datasets/p1_resampled/reference_fixed_variant.jsonl').open('w') as rf:
  for x in p0:
   pair=(x['simulation_id'],str(x['step_id']));sources=sample(cache.get(pair,[]),rng);sid='v2_fixed_'+x['sample_id'];rr=ref(sid,pair,x['sampling_replica_id'],sources);rr['p0_sample_id']=x['sample_id']
   write(pf,view(sid,sources));write(rf,rr);fixedrefs.append(rr)
 with (ROOT/'P2_AUTHORIZED_STEP_MANIFEST.csv').open('w') as f:
  fields=['simulation_id','scenario_id','step_id','logical_step_id','source_files','log_lines','bytes','authorized_status'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for sim,step in pairs:
   rs=[r for r in source_stats if r['simulation_id']==sim and r['step_id']==step]
   w.writerow(dict(simulation_id=sim,scenario_id=sim.split('_')[0],step_id=step,logical_step_id=sim.split('_')[0]+'-'+step,source_files=len(rs),log_lines=sum(r['total_lines'] for r in rs),bytes=sum(r['uncompressed_bytes'] for r in rs),authorized_status='AUTHORIZED_CURRENT_TURN_EXCLUDING_CONV_A01'))
 def stats(refs):
  groups=collections.defaultdict(set)
  for r in refs:groups[r['logical_step_id']].add(r['input_hash'])
  return {'queries':len(refs),'logical_steps':len(groups),'unique_content_hashes':len(set(r['input_hash'] for r in refs)),'duplicate_hash_records':len(refs)-len(set(r['input_hash'] for r in refs)),'different_inputs_per_logical_step':{k:len(v) for k,v in groups.items()},'scenarios':sorted(set(r['scenario_id'] for r in refs))}
 common={'archive_path':str(ARCH),'archive_sha256':archive_hash,'scope':'exact385 P0-selected execution-step pairs, 195 logical steps,34 simulations','version':'CAM-LDS v2; not independent dataset','seed':42,'allowed_member_count':len(mapping),'allowed_body_bytes':sum(i.file_size for i,r in mapping),'denied_member_counts':dict(excluded),'external_log_transmissions':0,'gt_source':str(OLD/'official_sources/labels.json')+' metadata.keys only','prediction_view':'sample_id,text,sources; opaque source/line IDs, no GT/scenario/step metadata','source_types':dict(collections.Counter(r['source_type'] for r in source_stats)),'leakage_cleaning':dict(cleaning),'cleaning_policy':'official eight regexes + nested annotation-value removal + unbounded direct T-ID redaction; native text never in prediction','implementation':str(Path(__file__).resolve()),'implementation_sha256':sha_file(Path(__file__))}
 dump(ROOT/'P1_RESAMPLED_DATA_MANIFEST.json',dict(common,protocol='P1',status='PUBLIC_EXPOSED_DEVELOPMENT',sampling='official fresh per-repetition contiguous ten lines per host-source; sorted file order; restricted P0 variant pool',official_script_commit='42bbd2cf8409f64a1e6c8fc936c91725e8c558b2',official_script_sha256=sha_file(official),official_main_executed=False,official_sampling_function_executed_for_equivalence_checks=True,official_sampling_core_equivalence_checks=6,primary=stats(p1refs),fixed_variant_control=stats(fixedrefs),qualifier='P1 draws v2 logs; P0/P1 cannot isolate resampling from version/variant effects'))
 dump(ROOT/'P2_V2_DATA_MANIFEST.json',dict(common,protocol='P2',status='PUBLIC_EXPOSED_DEVELOPMENT',execution_step_pairs=len(pairs),logical_steps=195,simulations=34,sampled_queries=385,full_queries=385,source_files=len(source_stats),full_lines=sum(r['total_lines'] for r in source_stats),sampled_unique_hashes=len(set(p2hash)),sampled_budget='ten contiguous lines per nonempty host-source, seed42; not fixed TOTAL budget',full_budget='all allowable victim step logs, no sequence or attacker content'))
 print(json.dumps({'p1':stats(p1refs),'fixed':stats(fixedrefs),'p2_full_lines':sum(r['total_lines'] for r in source_stats),'allowed_sources':len(mapping),'seconds':time.time()-t}))
if __name__=='__main__':main()
