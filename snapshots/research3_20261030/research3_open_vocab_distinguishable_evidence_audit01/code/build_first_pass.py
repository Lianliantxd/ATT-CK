"""Serialize new source-based manual notes and seal before candidate access."""
import csv,hashlib,json,re
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(n):return json.loads((R/n).read_text())
def dump(n,x):(R/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def csvout(n,rows):
 with (R/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
  for x in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in x.items()})
# Newly authored from all54 literal frozen definitions read this turn. No old
# condition catalog, old judgment plan or AI assessment is imported.
DATA={
'T1007':('尝试获取已注册本地系统服务信息','本地服务及其注册/状态信息',None,'GENERAL'),
'T1049':('尝试获取系统网络连接清单','本地或远端系统的连接关系',None,'GENERAL'),
'T1069':('查询用户组、成员或权限设置','组/权限及其成员',None,'GENERAL'),
'T1201':('读取口令策略细节','口令复杂度/长度/锁定策略',None,'GENERAL'),
'T1518':('列举安全软件、配置或防御工具','安装的软件/传感器/防御配置',None,'SECURITY_SOFTWARE_BRANCH'),
'T1614':('获取系统语言以推断位置','系统语言/键盘或默认语言',None,'LANGUAGE_BRANCH'),
'T1615':('获取Group Policy/GPO设置','域组策略对象和设置',None,'GENERAL'),
'T1547':('配置启动或登录时执行程序','程序、自启配置及触发点','自启配置或启动/登录执行关系','CORE_SENTENCE_INCOMPLETE'),
'T1595':('主动检查目标软件/配置与漏洞匹配','被探测目标及版本/漏洞相关响应',None,'VULNERABILITY_SCANNING_BRANCH'),
'T1136':('创建本地账户','新账户、UID/GID等属性','新账户状态出现','LOCAL_ACCOUNT_BRANCH'),
'T1120':('尝试查询所连接的外设或硬件组件','连接系统的设备/组件信息',None,'GENERAL'),
'T1124':('查询系统时间或时区','本地或远端时间/时区值',None,'GENERAL'),
'T1497':('执行虚拟化/分析环境检查','VME/沙箱标志与检查结果','检查与避开分析/改变行为的联系','SYSTEM_CHECK_BRANCH'),
'T1556':('修改PAM认证流程','PAM配置、库或认证执行组件','认证过程或允许访问的改变','PAM_BRANCH'),
'T1098':('给受控云账户增加角色/权限','云账户、IAM/角色权限','角色/权限增加','CLOUD_ROLE_BRANCH'),
'T1218':('滥用受信系统程序代理代码','rundll32等可见变体与被代理负载',None,'RUNDLL32_BRANCH_NOT_COMPLETE_PARENT'),
'T1021':('使用有效账户远程控制另一计算机','VNC/RFB身份与远端主机',None,'VNC_BRANCH_NOT_COMPLETE_PARENT'),
'T1074':('把已收集数据集中暂存','收集数据、源位置及集中位置','数据集中写入或暂存关系','LOCAL_REMOTE_STAGING'),
'T1560':('压缩/加密/封装已收集数据','收集数据与压缩/归档工具','归档或加密产物','UTILITY_BRANCH'),
'T1005':('搜索或获取本地感兴趣数据','本地文件/配置/数据库内容',None,'GENERAL'),
'T1018':('尝试获取其他系统地址/主机名列表','远端系统标识/地址',None,'GENERAL'),
'T1046':('尝试列举远端运行的服务','远端服务、端口或相应响应',None,'GENERAL'),
'T1573':('用算法加密控制通信','通信端点、控制流量和加密处理','加密与C2流量的联系','SYMMETRIC_ASYMMETRIC_BODY'),
'T1014':('通过系统接口挂钩/修改隐藏对象','程序/文件/连接/服务与系统信息接口','隐藏或接口修改','GENERAL'),
'T1569':('借服务管理框架执行程序','launchctl/launchd任务和执行对象',None,'LAUNCHCTL_BRANCH_NOT_COMPLETE_PARENT'),
'T1036':('以双扩展名掩盖真实类型','文件名扩展与实际类型','类型误导/伪装关系','DOUBLE_EXTENSION_BRANCH'),
'T1072':('使用集中软件部署/配置管理系统执行命令','管理系统、任务与目标端点','管理任务执行','GENERAL'),
'T1486':('加密目标数据以影响可用性','目标数据和加密改变','数据加密及访问性影响','GENERAL'),
'T1565':('插入/删除/修改静态数据内容','静态数据与被改变的内容','内容完整性改变及相关影响','STORED_DATA_BRANCH'),
'T1531':('抑制合法用户的账户访问','合法账户/凭据/访问资格','锁定/删除/改凭据等阻止访问','GENERAL'),
'T1485':('修改云存储桶生命周期以删除对象','云存储桶、生命周期策略及对象','生命周期策略修改及删除关系','LIFECYCLE_BRANCH_NOT_COMPLETE_PARENT'),
'T1489':('停止或禁用具体服务','被停止/禁用的服务','服务停止/禁用状态','GENERAL'),
'T1080':('将恶意内容加入共享存储','共享文件/仓库与恶意负载','共享内容被污染及远端接触关系','GENERAL'),
'T1213':('从SharePoint等可见信息仓库挖掘数据','SharePoint/Confluence信息仓库',None,'REPOSITORY_BRANCH_NOT_COMPLETE_PARENT'),
'T1599':('修改网络设备NAT以跨越边界','边界设备、NAT和信任区间','NAT映射改变或跨界关系','NAT_BRANCH_NOT_COMPLETE_PARENT'),
'T1205':('通过socketfilter匹配流量激活后门','套接字过滤器、触发包和后门','匹配触发并激活的联系','SOCKET_FILTER_BRANCH'),
'T1528':('窃取应用访问令牌','令牌及其来源/拥有者','令牌被获得/窃取','GENERAL'),
'T1550':('使用替代认证材料访问资源','哈希/票据/token等材料及身份',None,'GENERAL'),
'T1204':('依赖用户打开恶意文件获得执行','用户、文件与打开/执行链','用户动作引发代码执行','MALICIOUS_FILE_BRANCH'),
'T1115':('获取剪贴板保存的数据','剪贴板与其内容','实际读取/采集数据','GENERAL'),
'T1222':('改变文件或目录权限/属性','文件路径及ACL/权限','权限/属性改变','LINUX_MAC_BRANCH'),
'T1010':('尝试列举当前打开应用窗口','窗口/应用列表或明确枚举请求',None,'GENERAL'),
'T1056':('通过记录按键截获输入','输入/按键及截获接口','截获的输入或凭据数据','KEYLOGGING_BRANCH'),
'T1176':('安装或滥用浏览器扩展建立访问','扩展对象、浏览器及权限','扩展安装/激活与持续访问关系','BROWSER_EXTENSION_BRANCH'),
'T1566':('发送包含恶意链接的定向社工消息','发件/收件对象、消息和链接',None,'SPEARPHISHING_LINK_BRANCH'),
'T1219':('用远程访问软件建立交互控制通道','RMM/远程桌面软件与peer','远端交互控制或C2通道','GENERAL'),
'T1210':('利用远程服务漏洞获得未授权访问','远端服务、漏洞及边界','漏洞利用和未授权访问/代码执行','GENERAL'),
'T1525':('给受害环境内注册表镜像植入代码','内部容器/云镜像和注册表','镜像被修改/植入','GENERAL'),
'T1610':('创建/启动容器以执行或规避限制','容器/镜像与部署环境','容器创建/启动','GENERAL'),
'T1589':('收集受害者身份信息','姓名/邮箱/凭据/MFA等身份资料',None,'GENERAL'),
'T1592':('收集受害主机配置/功能信息','硬件/软件/系统管理信息',None,'GENERAL'),
'T1095':('使用非应用层协议承载控制通信','协议、控制端或感染主机',None,'GENERAL'),
'T1190':('利用公开应用弱点取得初始网络访问','互联网暴露应用、漏洞/错误配置','初始进入网络的访问关系','GENERAL'),
'T1033':('主动识别系统用户/所有者','用户身份/会话或其获取请求',None,'GENERAL')}
def source_type(t):
 if '[**]' in t or '"rule":' in t or '"alert":' in t:return 'DERIVED_PATTERN'
 if 'Executing Browser Command:' in t or 'Browser command' in t or 'Command: type' in t or 'Sleeping ' in t:return 'OTHER_DOCUMENTED_SOURCE'
 if t.startswith(('ARCH=','UID=','OUID=','FSUID=','SADDR=')):return 'OTHER_DOCUMENTED_SOURCE'
 return 'NATIVE_LOG_RECORD'
def binding(fs):
 ts='\n'.join(f['text'] for f in fs)
 return {'subject_binding_status':'VISIBLE_ACCOUNT_PROCESS_OR_SOURCE_ADDRESS_ONLY' if re.search(r'pid=|comm=|exe=|\[\d+\]|from \d|SRC=',ts) else 'NOT_ESTABLISHED',
  'asset_binding_status':'VISIBLE_PATH_ENDPOINT_OR_REQUEST_OBJECT_ONLY' if re.search(r'/|COMMAND=|a[0-9]=|DST=| is |query\[|service|new user',ts) else 'NOT_ESTABLISHED',
  'temporal_binding_status':'VISIBLE_TIMESTAMPS_OR_AUDIT_KEYS_NOT_CAUSAL_PROOF' if re.search(r'audit\(\d|\d\d:\d\d:\d\d',ts) else 'NOT_ESTABLISHED'}
def main():
 assert not (R/'audit/FIRST_PASS_SEAL.json').exists(),'sealed first pass immutable'
 rows=[json.loads(s) for s in (R/'inputs/FIRST_PASS_INPUTS.jsonl').read_text().splitlines()]
 facts=[json.loads(s) for s in (R/'inputs/VISIBLE_FACT_REGISTRY.jsonl').read_text().splitlines()];fm={f['fact_id']:f for f in facts}
 notes=load('review/FIRST_PASS_MANUAL_NOTES.json');aid={x['step']:x for x in load('inputs/FIRST_PASS_READING_AID.json')};defs=load('inputs/GOLD_FROZEN_DEFINITIONS.json')
 assert set(DATA)==set(defs) and set(aid)==set(notes)
 registry={t:{'technique_id':t,'frozen_description':defs[t],'description_sha256':hashlib.sha256(defs[t].encode()).hexdigest(),
  'core_behavior':d[0],'necessary_object':d[1],'required_state_or_result':d[2],'definition_scope':d[3],
  'necessary_prerequisites':'动作/对象定义中列出的访问材料、目标类型及关系；不另造通用前提',
  'optional_behaviors':'may、示例工具、实现方式及可能后续用途不自动成为每个变体的必要条件',
  'actor_asset_constraints':'实际日志身份与资产仅按可见文字；攻击者/授权/意图另外未认证',
  'distinguishing_condition':d[0]+'；要求与'+d[1]+'的对象和时间绑定',
  'provenance':'new same-context AI paraphrase this run,not independent reference;literal definition unchanged'} for t,d in DATA.items()}
 dump('review/GOLD_CONDITION_REGISTRY.json',registry)
 out=[];flat=[];decodes=[]
 for q in rows:
  n=notes[q['logical_step_id']];a=aid[q['logical_step_id']];own=[fm[f] for f in q['visible_fact_ids']]
  base={'level':n['default'],'lines':n.get('lines',[])};base.update(n.get('overrides',{}).get(q['review_id'],{}));gg=[];cc=[]
  for t in q['gold_technique_ids']:
   j=dict(base);j.update(n.get('targets',{}).get(t,{}));level=j['level'];chosen={a['lines'][i-1]['text'] for i in j.get('lines',[])}
   selected=[f for f in own if f['text'] in chosen];refs=[f['fact_id'] for f in selected]
   if level not in ['NONE','INPUT_UNKNOWN']:assert refs,(q['review_id'],t,level)
   core,obj,result,scope=DATA[t]
   ev='DIRECTLY_SUPPORTED' if level=='DIRECT' else 'PARTIALLY_SUPPORTED' if level=='PARTIAL' else 'NOT_EVALUABLE' if level=='SCOPE' else 'NOT_OBSERVABLE_IN_CURRENT_VIEW' if level=='INPUT_UNKNOWN' else 'NOT_ESTABLISHED'
   if t=='T1115' and level=='DIRECT':ev='PARTIALLY_SUPPORTED' # explicit request,actual collection not shown
   status_result='DIRECTLY_SUPPORTED' if level=='DIRECT' and t in {'T1136','T1072','T1489'} else 'NOT_EVALUABLE' if level=='SCOPE' else 'NOT_ESTABLISHED'
   b=binding(selected);local=[]
   def condition(kind,text,status,required=True):
    positive=status in ['DIRECTLY_SUPPORTED','PARTIALLY_SUPPORTED'];ids=refs if positive else []
    z={'sample_id':q['sample_id'],'review_id':q['review_id'],'gold_technique_id':t,'condition_id':q['review_id']+'_'+t+'_'+kind,
     'condition_text':text,'condition_type':kind,'required_for_observable_behavior_contract':required,'evidence_status':status,
     'supporting_fact_ids':ids,'contradicting_fact_ids':[],'context_fact_ids':refs if not positive else [],
     'supporting_source_type':sorted({source_type(f['text']) for f in selected}) if positive else ['NO_SUPPORTING_SOURCE'],
     **b,'scope_limitations':[q['input_view'],'omitted original records unknown','Fact IDs are derived displayed-line locators,not native event IDs',scope,'adversarial attribution/full intent not certified'],
     'missing_information':[] if status=='DIRECTLY_SUPPORTED' else [n.get('missing',n['observation'])],
     'reasoning':'步骤阅读笔记（含视图差别，不是把所有视图合并为本查询事实）：'+n['observation']+'；本条件只按当前查询实际出现的引用行判定，不借用其他采样。',
     'human_review_required':True,'reference_status':'NONINDEPENDENT_AI_PRE_AUDIT_NOT_GOLD'}
    cc.append(z);flat.append(z);local.append(z)
   condition('CORE_BEHAVIOR',core,ev)
   condition('OBJECT_AND_PREREQUISITE',obj,ev)
   condition('ACTION_OBJECT_TIME_BINDING','将上述动作与当前对象/进程/时间绑定（不认证攻击者）',ev)
   if result:condition('REQUIRED_STATE_OR_RESULT',result,status_result)
   condition('ADVERSARIAL_ATTRIBUTION','攻击者归属、授权边界及完整攻击目的','NOT_ESTABLISHED',False)
   if level in ['PREPARATORY','BROAD','SCOPE']:
    condition('VISIBLE_CONTEXT_NOT_GOLD_PROOF','当前引用行字面记录的背景/准备动作；不将步骤笔记中其他采样的信息作为本查询事实','DIRECTLY_SUPPORTED',False)
   behavioral=all(z['evidence_status']=='DIRECTLY_SUPPORTED' for z in local if z['required_for_observable_behavior_contract'])
   gg.append({'technique_id':t,'frozen_description_sha256':registry[t]['description_sha256'],'definition_scope':scope,
    'fresh_relatedness_level':level,'supporting_fact_ids':refs,'reasoning':n['observation'],
    'observable_necessary_conditions_supported_AI_only':behavioral,
    'full_gold_semantic_truth':'NOT_AVAILABLE_WITHOUT_QUALIFIED_REFERENCE',
    'condition_ids':[z['condition_id'] for z in local]})
  for f in own:
   for m in re.finditer(r'\b(proctitle|cmd|a[0-9]+)=([0-9A-Fa-f]{8,})(?=\s|$)',f['text']):
    k,v=m.groups()
    if k.startswith('a') and 'type=EXECVE' not in f['text']:continue
    raw=bytes.fromhex(v[:len(v)//2*2]);decoded=raw.decode('utf8',errors='replace')
    decodes.append({'fact_id':f['fact_id'],'sample_id':q['sample_id'],'field':k,'literal_hex':v,'decoded_complete_byte_pairs':decoded,
     'incomplete_final_nibble':len(v)%2==1,'source_type':'DERIVED_PATTERN','method':'static hex decode;no execution or missing-suffix reconstruction'})
  out.append({**{k:q[k] for k in ['sample_id','review_id','logical_step_id','scenario_id','execution_id','execution_id_mapping','fold_id','view_id','input_view','input_view_hash','gold_technique_ids']},
   'phase':'FIRST_PASS_SEALED_BEFORE_CURRENT_CANDIDATES','first_pass_complete':True,
   'blinding_status':'INDEPENDENT_BLIND_REVIEW_NOT_AVAILABLE','review_status':'NONINDEPENDENT_AI_EVIDENCE_AUDIT_NOT_GOLD',
   'visible_scope':{k:q[k] for k in ['visible_fact_ids','visible_record_count','visible_record_count_unit','omitted_record_count','native_fact_ids_provided','coverage_limitations']},
   'visible_facts':[{'fact_id':f['fact_id'],'text':f['text'],'source_type':source_type(f['text']),'fact_id_kind':'DERIVED_SOURCE_LOCATOR_NOT_NATIVE_EVENT_ID','native_original_authenticity':'NOT_INDEPENDENTLY_CERTIFIED_FROZEN_COPY'} for f in own],
   'gold_audits':gg,'gold_conditions':cc,'manual_source_note':n['observation'],
   'source_reading_method':'all80 step-union texts/737lines and per-query occurrences read anew this run;no old judgement/catalog imported;not independent per-case contexts',
   'related_behavior_evidence_AI_only':any(g['fresh_relatedness_level'] in ['DIRECT','PARTIAL'] for g in gg),
   'observable_gold_core_supported_AI_only':any(g['observable_necessary_conditions_supported_AI_only'] for g in gg),
   'gold_scope_unresolved_AI_only':any(g['fresh_relatedness_level']=='SCOPE' for g in gg),'human_review_required':True})
 p=R/'review/FIRST_PASS_CASE_EVIDENCE.jsonl';p.write_text(''.join(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n' for x in out))
 csvout('review/CONDITION_EVIDENCE_MATRIX.csv',flat)
 (R/'review/DERIVED_VISIBLE_HEX.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in decodes))
 paths=['review/FIRST_PASS_MANUAL_NOTES.json','review/GOLD_CONDITION_REGISTRY.json','review/FIRST_PASS_CASE_EVIDENCE.jsonl','review/CONDITION_EVIDENCE_MATRIX.csv','review/DERIVED_VISIBLE_HEX.jsonl']
 seal={'phase':'FIRST_PASS_COMPLETE_SEALED','created_utc':datetime.now(timezone.utc).isoformat(),'query_count':len(out),'unique_queries':len({x['sample_id'] for x in out}),
  'condition_instances':len(flat),'all80_steps_and384_occurrence_maps_read':True,'new_current_candidate_payload_access_before_seal':False,
  'independent_blinding':'NOT_AVAILABLE','historical_information_already_exposed':True,'files':[{'path':n,'sha256':sha(R/n)} for n in paths]}
 dump('audit/FIRST_PASS_SEAL.json',seal)
 print(json.dumps({'queries':len(out),'condition_instances':len(flat),'levels':dict(Counter(g['fresh_relatedness_level'] for x in out for g in x['gold_audits'])),
  'related_AI':sum(x['related_behavior_evidence_AI_only'] for x in out),'behavioral_core_AI':sum(x['observable_gold_core_supported_AI_only'] for x in out)},ensure_ascii=False))
if __name__=='__main__':main()
