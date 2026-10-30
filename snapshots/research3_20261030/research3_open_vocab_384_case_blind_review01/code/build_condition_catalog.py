"""Fixed target-reference paraphrases; do not expand partial parent definitions."""
import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
# name, visible-reference core, object, required outcome, scope of available body
DATA={
'T1007':('System Service Discovery','尝试查询或列举本地已注册系统服务','本地服务名称/状态/配置',False,''),
'T1049':('System Network Connections Discovery','获取当前系统或远端系统的网络连接列表','网络连接及其端点/协议',False,''),
'T1069':('Permission Groups Discovery','查询组、组成员关系或权限设置','用户组/权限及成员',False,''),
'T1201':('Password Policy Discovery','访问企业系统或云环境口令策略的详细信息','长度/锁定/复杂度等口令策略',False,''),
'T1518':('Software Discovery','可见正文具体描述列举安全软件、配置、防御工具或传感器','已安装安全软件/监控或防御配置',False,'SECURITY_SOFTWARE_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1614':('System Location Discovery','可见正文描述获取系统语言以推断地理位置','系统语言、默认值或键盘布局',False,'LANGUAGE_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1615':('Group Policy Discovery','获取Group Policy/GPO设置','域组策略对象/设置',False,''),
'T1547':('Boot or Logon Autostart Execution','配置系统设置使程序在启动或登录时自动执行','自动启动配置、程序及启动/登录触发',True,'BODY_ENDS_DURING_CORE_SENTENCE'),
'T1595':('Active Scanning','可见正文描述主动检查目标配置/软件版本与漏洞利用的潜在匹配','被探测目标及软件/配置/漏洞相关响应',False,'VULNERABILITY_SCANNING_VARIANT_NOT_COMPLETE_PARENT'),
'T1136':('Create Account','可见正文描述创建本地账户以维持访问','新账户及本地账户属性',True,'LOCAL_ACCOUNT_BRANCH_NOT_EXHAUSTIVE_PARENT'),
'T1120':('Peripheral Device Discovery','尝试获取连接计算机的外设/组件信息','外围设备与硬件组件',False,''),
'T1124':('System Time Discovery','查询/获取本地或远端系统时间或时区','系统时间/时区',False,''),
'T1497':('Virtualization/Sandbox Evasion','进行与虚拟化/分析环境识别相关的系统检查并关联避开分析','虚拟机或沙箱标志和检查结果',False,'SYSTEM_CHECKS_BRANCH_PURPOSE_NOT_DIRECTLY_OBSERVABLE'),
'T1556':('Modify Authentication Process','可见正文描述修改PAM以获取凭据或允许不当账户访问','PAM配置/库/程序及认证行为',True,'PAM_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1098':('Account Manipulation','可见正文描述给控制的云账户增加角色或权限以维持访问','云账户、IAM策略/角色或管理员权限',True,'CLOUD_ROLE_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1218':('System Binary Proxy Execution','可见正文描述滥用rundll32等受信任系统程序代理恶意代码','受信程序、被代理DLL/负载及调用关系',False,'RUNDLL32_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1021':('Remote Services','可见正文描述使用有效账户通过VNC远程控制另一计算机','VNC/RFB会话、远端主机及认证',False,'VNC_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1074':('Data Staged','将已收集数据集中在本地或远端位置以备外传','收集数据、源位置和暂存目标',True,''),
'T1560':('Archive Collected Data','使用实用程序压缩/加密或封装已收集数据以便运输','输入数据、压缩/加密工具及产物',True,'UTILITY_BRANCH_NOT_EXHAUSTIVE_PARENT'),
'T1005':('Data from Local System','搜索/获取本地文件系统、配置或数据库中的感兴趣数据','本地数据源与被获取内容',False,''),
'T1018':('Remote System Discovery','尝试获取网络中其他系统的地址、主机名或逻辑标识列表','远端主机地址/名称/标识',False,''),
'T1046':('Network Service Discovery','尝试列举远端主机或网络基础设备运行的服务','服务/端口或相应探测响应',False,''),
'T1573':('Encrypted Channel','用加密算法隐藏控制通信而非仅依赖协议的固有保护','通信双方、加密处理和控制流量',True,''),
'T1014':('Rootkit','使用拦截/挂钩/修改系统信息接口等方式隐藏系统对象','程序/文件/连接/驱动及隐藏或接口改动',True,''),
'T1569':('System Services','可见正文描述利用launchctl/launchd等服务框架执行程序','服务框架、服务对象和程序执行',False,'LAUNCHCTL_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1036':('Masquerading','可见正文描述通过双扩展名掩盖真实文件类型','文件名/扩展名与实际类型',True,'DOUBLE_EXTENSION_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1072':('Software Deployment Tools','使用集中管理/软件部署系统执行命令或横向活动','管理/部署系统、目标端点及执行任务',False,''),
'T1486':('Data Encrypted for Impact','加密目标数据并造成可用性或访问的影响','目标数据、加密改变及访问性',True,''),
'T1565':('Data Manipulation','可见正文描述插入、删除或修改静态数据以影响结果或隐藏活动','静态数据内容及改变',True,'STORED_DATA_VARIANT_NOT_EXHAUSTIVE_PARENT'),
'T1531':('Account Access Removal','通过删除/锁定/改凭据等操作抑制合法账户访问','合法账户及访问资格/凭据变化',True,''),
'T1485':('Data Destruction','可见正文描述修改云存储桶生命周期策略以删除对象','云存储桶/生命周期策略/对象',True,'CLOUD_LIFECYCLE_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1489':('Service Stop','停止或禁用服务使其不可用','具体服务及停止/禁用状态',True,''),
'T1080':('Taint Shared Content','将恶意程序/脚本/利用代码加入共享内容并可能被远端触发','共享存储内容、恶意修改及远端访问',True,''),
'T1213':('Data from Information Repositories','可见正文描述利用SharePoint信息仓库挖掘有价值信息','SharePoint或可见信息库及被读取的数据',False,'SHAREPOINT_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1599':('Network Boundary Bridging','可见正文描述通过修改网络设备NAT配置跨越信任边界','边界设备、NAT映射及信任区间',True,'NAT_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1205':('Traffic Signaling','可见正文描述socket filter匹配特殊流量后激活后门动作','套接字过滤条件、触发数据包及后门动作',True,'SOCKET_FILTER_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1528':('Steal Application Access Token','窃取应用访问令牌以获得访问凭据','应用/API令牌及其被获取的来源',True,''),
'T1550':('Use Alternate Authentication Material','使用密码哈希/票据/令牌等替代认证材料以绕过正常访问控制或移动','材料类型、身份和认证使用关系',False,''),
'T1204':('User Execution','可见正文描述依赖用户打开恶意文件以执行代码','用户、文件及打开/执行链',True,'MALICIOUS_FILE_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1115':('Clipboard Data','访问/收集剪贴板保存的用户数据','剪贴板访问与内容',True,''),
'T1222':('File and Directory Permissions Modification','改变文件或目录权限/属性以规避访问控制','文件路径及权限/ACL状态',True,''),
'T1010':('Application Window Discovery','获取当前打开的应用窗口列表','窗口/应用列表或枚举请求',False,''),
'T1056':('Input Capture','可见正文描述记录按键以截获输入的凭据','按键/输入事件或其截获接口与数据',True,'KEYLOGGING_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1176':('Software Extensions','可见正文描述安装/滥用浏览器扩展以建立持续访问','浏览器扩展、安装/激活和访问权限',True,'BROWSER_EXTENSION_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1566':('Phishing','可见正文描述发送带恶意链接的定向社工消息以获取访问','社工消息、接收者和恶意链接/交互',False,'SPEARPHISHING_LINK_VARIANT_BODY_NOT_COMPLETE_PARENT'),
'T1219':('Remote Access Tools','使用远程支持/桌面软件建立交互式控制通道','远控软件、对端和交互会话',False,''),
'T1210':('Exploitation of Remote Services','利用远程服务软件弱点执行控制代码或获得未授权访问','远程服务、弱点/利用输入和访问边界',True,''),
'T1525':('Implant Internal Image','将恶意代码植入受害环境内部注册表的云/容器镜像','内部镜像、注册表及代码植入变化',True,''),
'T1610':('Deploy Container','在环境中创建/启动容器以执行进程或绕开限制','容器/镜像、运行时及部署/启动事件',True,''),
'T1589':('Gather Victim Identity Information','获取可用于针对受害者的身份信息','人员姓名、邮箱、凭据/MFA等身份属性',False,''),
'T1592':('Gather Victim Host Information','获取受害主机的软硬件/配置/管理信息','受害主机及其配置/功能属性',False,''),
'T1095':('Non-Application Layer Protocol','使用非应用层协议在主机与控制端或感染主机之间通信','协议、通信双方与控制关系',False,''),
'T1190':('Exploit Public-Facing Application','利用面向互联网应用/服务的弱点取得初始网络访问','暴露应用、弱点及初始访问边界',True,''),
'T1033':('System Owner/User Discovery','尝试识别系统主要用户、登录用户或使用该系统的用户','用户身份/会话及主动获取行为',False,'')
}

def main():
 defs=json.loads((R/'inputs/TARGET_DEFINITIONS.json').read_text());assert set(DATA)==set(defs)
 out={}
 for tid,(name,core,obj,required,scope) in DATA.items():
  text=defs[tid];assert name in text,(tid,name)
  out[tid]={'frozen_name':name,'frozen_description_sha256':hashlib.sha256(text.encode()).hexdigest(),'frozen_description':text,'core_condition':core,'object_condition':obj,'result_required_in_visible_definition':required,'reference_scope_qualification':scope or 'VISIBLE_BODY_GIVES_USABLE_CORE_NOT_INDEPENDENTLY_EXHAUSTIVE','variant_specific_requirements_not_necessary_for_every_parent_subtype':bool(scope),'required_conditions_apply_only_to_visible_variant_when_scope_partial':bool(scope),'possible_actor_or_asset':'actor/host/object only if explicitly bound by current records; no inference from sample or technique label','required_result_text':'确认定义所述状态/内容/访问改变，而不只记录工具名或准备动作' if required else '最终输出或后续影响可以未提供；不得将可选结果当作定义的必要条件','distinguishing_information_needed':obj+'；需绑定行为主体、对象及时间，不能仅有背景或工具名','optional_behaviors':'定义中的may、例如、such as及后续用途是可能路径，不将所有举例同时当必要条件','examples_not_observation_facts':True,'interpretation_provenance':'same-context AI paraphrase of supplied frozen description; not independently adjudicated','literal_reference_unchanged':True}
 (R/'review/GOLD_CONDITION_CATALOG.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print('Frozen target condition catalog',len(out))
if __name__=='__main__':main()
