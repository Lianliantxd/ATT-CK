# Method error analysis

Full EvidenceLineFusion has not comprehensively exceeded simple fusion. On exposed P0 K2 BM25, full Top1/Top10/MRR are 0.026667/0.242051/0.081291, compared with RRF 0.069744/0.228718/0.106547. NoSourceCalibration is an ablation and must not be promoted after observing a favorable Top10.

Selection was fixed as ascending sample_id, first at most two queries per category. Categories use parent-normalized Top10 only. Repeated replicas remain selected under this rule and are not independent cases. Knowledge is the identical 216-candidate K2; no predictor is rerun using GT. Diagnostic GT traces below are explicitly post-hoc, label-conditioned analysis.

## candidate_only: 1-32-r2

Gold original: ['T1053']; parent: ['T1053'].
Full ranking: ['T1562', 'T1559', 'T1546', 'T1505', 'T1036', 'T1543', 'T1053', 'T1556', 'T1003', 'T1499']
RRF ranking: ['T1562', 'T1505', 'T1543', 'T1556', 'T1546', 'T1036', 'T1559', 'T1110', 'T1003', 'T1563']

Observed: native Suricata alert contains curl User-Agent and HTTP GET /TODO.md. Candidate top1 is T1562, not scheduled-task T1053; T1053 enters rank 7. The top1 lexical trace has high category/start/status/rule contributions. Reasonable inference: alert-envelope vocabulary can favor the long impairment description. A Top10 hit alone does not establish a task-scheduling evidence chain.

- `T1562` full rank 1, RRF rank 1, role prediction_top1; native `wazuh/logs/alerts/alerts.json` / `L0` / SHA256 `c9076f73cdb61caff8534f9628e666999e4de5a0f64fa88e662285f3a9faabb4`; hash and exact line verified. Strongest terms: [('start', 4.183201963932025), ('category', 4.174282507371437), ('status', 3.900140529412493), ('rule', 3.083992406875962), ('log', 2.8138225148468043), ('groups', 2.1127187638631737)].
  Native line: `{"timestamp":"2025-09-24T08:15:02.920+0000","rule":{"level":3,"description":"Suricata: Alert - ET HUNTING curl User-Agent to Dotted Quad","id":"86601","firedtimes":10,"mail":false,"groups":[` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Safe Mode Boot defense-evasion Impair Defenses defense-evasion Disable Windows Event Logging defense-evasion Disable or Modify System Firewall defense-evasion Disable or Modify Linux Audit System defense-evasion Indicator Blocking
- `T1053` full rank 7, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `videoserver/logs/log/audit/audit.log` / `L6` / SHA256 `ac3a4b53fcf7e3e065838f879856cfa2f6a48f09f435078c7378583bc60215c2`; hash and exact line verified. Strongest terms: [('cron', 7.552607290246963), ('arch', 6.292467481304507), ('usr', 2.232162441813697), ('type', 1.4710012192510158), ('root', 1.44207400980539)].
  Native line: `type=SYSCALL msg=audit(1758701761.916:13680): arch=c000003e syscall=257 success=yes exit=7 a0=ffffff9c a1=7fed92e5b176 a2=80000 a3=0 items=1 ppid=541 pid=17412 auid=4294967295 uid=0 gid=0 eu` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Scheduled Task execution persistence privilege-escalation Container Orchestration Job execution persistence privilege-escalation Cron execution persistence privilege-escalation Scheduled Task/Job execution persistence privilege-es
## candidate_only: 1-32-r3

Gold original: ['T1053']; parent: ['T1053'].
Full ranking: ['T1562', 'T1559', 'T1546', 'T1505', 'T1036', 'T1543', 'T1053', 'T1556', 'T1003', 'T1499']
RRF ranking: ['T1562', 'T1505', 'T1543', 'T1556', 'T1546', 'T1036', 'T1559', 'T1110', 'T1003', 'T1563']

Observed: native Suricata alert contains curl User-Agent and HTTP GET /TODO.md. Candidate top1 is T1562, not scheduled-task T1053; T1053 enters rank 7. The top1 lexical trace has high category/start/status/rule contributions. Reasonable inference: alert-envelope vocabulary can favor the long impairment description. A Top10 hit alone does not establish a task-scheduling evidence chain.

- `T1562` full rank 1, RRF rank 1, role prediction_top1; native `wazuh/logs/alerts/alerts.json` / `L0` / SHA256 `c9076f73cdb61caff8534f9628e666999e4de5a0f64fa88e662285f3a9faabb4`; hash and exact line verified. Strongest terms: [('start', 4.183201963932025), ('category', 4.174282507371437), ('status', 3.900140529412493), ('rule', 3.083992406875962), ('log', 2.8138225148468043), ('groups', 2.1127187638631737)].
  Native line: `{"timestamp":"2025-09-24T08:15:02.920+0000","rule":{"level":3,"description":"Suricata: Alert - ET HUNTING curl User-Agent to Dotted Quad","id":"86601","firedtimes":10,"mail":false,"groups":[` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Safe Mode Boot defense-evasion Impair Defenses defense-evasion Disable Windows Event Logging defense-evasion Disable or Modify System Firewall defense-evasion Disable or Modify Linux Audit System defense-evasion Indicator Blocking
- `T1053` full rank 7, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `videoserver/logs/log/audit/audit.log` / `L6` / SHA256 `ac3a4b53fcf7e3e065838f879856cfa2f6a48f09f435078c7378583bc60215c2`; hash and exact line verified. Strongest terms: [('cron', 7.552607290246963), ('arch', 6.292467481304507), ('usr', 2.232162441813697), ('type', 1.4710012192510158), ('root', 1.44207400980539)].
  Native line: `type=SYSCALL msg=audit(1758701761.916:13680): arch=c000003e syscall=257 success=yes exit=7 a0=ffffff9c a1=7fed92e5b176 a2=80000 a3=0 items=1 ppid=541 pid=17412 auid=4294967295 uid=0 gid=0 eu` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Scheduled Task execution persistence privilege-escalation Container Orchestration Job execution persistence privilege-escalation Cron execution persistence privilege-escalation Scheduled Task/Job execution persistence privilege-es
## rrf_only: 1-29-r0

Gold original: ['T1105', 'T1556.003']; parent: ['T1105', 'T1556'].
Full ranking: ['T1562', 'T1036', 'T1546', 'T1027', 'T1559', 'T1553', 'T1110', 'T1003', 'T1548', 'T1543']
RRF ranking: ['T1562', 'T1036', 'T1546', 'T1027', 'T1543', 'T1553', 'T1574', 'T1556', 'T1003', 'T1559']

Observed: native HTTP alert reports an ELF download, Wget and /pam_unix.so. This is an observed transfer/path, without proof the PAM module was loaded or authentication modified. Gold parent T1556 is RRF rank 8 but absent from full candidate Top10; top1 T1562 matches envelope words category/start/status/policy. Reasonable inference: vocabulary/specificity/source weighting can displace behavior-relevant candidates. Which component causes displacement is not established by this trace.

- `T1562` full rank 1, RRF rank 1, role prediction_top1; native `wazuh/logs/alerts/alerts.json` / `L1` / SHA256 `b5be558ce31d8ca65a561b73bf464af0566f9228ab8ab0e2b516edf12f5277a4`; hash and exact line verified. Strongest terms: [('start', 4.183201963932025), ('category', 4.174282507371437), ('status', 3.900140529412493), ('policy', 3.2252363466882517), ('rule', 3.083992406875962), ('log', 2.8138225148468043)].
  Native line: `{"timestamp":"2025-09-24T09:32:42.572+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Safe Mode Boot defense-evasion Impair Defenses defense-evasion Disable Windows Event Logging defense-evasion Disable or Modify System Firewall defense-evasion Disable or Modify Linux Audit System defense-evasion Indicator Blocking
- `T1105` full rank >10, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `videoserver/logs/log/audit/audit.log` / `L0` / SHA256 `0ba072999ed6272a23c313e04265b3bc7254965240d281f83394c449cfc346dd`; hash and exact line verified. Strongest terms: [('wget', 6.371290213094355)].
  Native line: `type=PATH msg=audit(1758706361.442:13750): item=0 name="/usr/bin/wget" inode=19049 dev=fe:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL cap_fp=0 cap_fi=0 cap_fe=0 cap_fver=0 cap_f` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Ingress Tool Transfer command-and-control Ingress Tool Transfer Adversaries may transfer tools or other files from an external system into a compromised environment. Tools or files may be copied from an external adversary-controll
- `T1556` full rank >10, RRF rank 8, role POSTHOC_GOLD_DIAGNOSTIC; native `wazuh/logs/alerts/alerts.json` / `L1` / SHA256 `b5be558ce31d8ca65a561b73bf464af0566f9228ab8ab0e2b516edf12f5277a4`; hash and exact line verified. Strongest terms: [('pam_unix', 5.249837091643741), ('id', 4.79519844255895), ('agent', 2.855549981722559), ('manager', 2.719184562086555), ('policy', 2.641343475026679), ('ip', 2.142381968276939)].
  Native line: `{"timestamp":"2025-09-24T09:32:42.572+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Pluggable Authentication Modules credential-access defense-evasion persistence Password Filter DLL credential-access defense-evasion persistence Hybrid Identity credential-access defense-evasion persistence Network Provider DLL cr
## rrf_only: 1-29-r1

Gold original: ['T1105', 'T1556.003']; parent: ['T1105', 'T1556'].
Full ranking: ['T1562', 'T1036', 'T1546', 'T1027', 'T1559', 'T1553', 'T1110', 'T1003', 'T1548', 'T1543']
RRF ranking: ['T1562', 'T1036', 'T1546', 'T1027', 'T1543', 'T1553', 'T1574', 'T1556', 'T1003', 'T1559']

Observed: native HTTP alert reports an ELF download, Wget and /pam_unix.so. This is an observed transfer/path, without proof the PAM module was loaded or authentication modified. Gold parent T1556 is RRF rank 8 but absent from full candidate Top10; top1 T1562 matches envelope words category/start/status/policy. Reasonable inference: vocabulary/specificity/source weighting can displace behavior-relevant candidates. Which component causes displacement is not established by this trace.

- `T1562` full rank 1, RRF rank 1, role prediction_top1; native `wazuh/logs/alerts/alerts.json` / `L1` / SHA256 `b5be558ce31d8ca65a561b73bf464af0566f9228ab8ab0e2b516edf12f5277a4`; hash and exact line verified. Strongest terms: [('start', 4.183201963932025), ('category', 4.174282507371437), ('status', 3.900140529412493), ('policy', 3.2252363466882517), ('rule', 3.083992406875962), ('log', 2.8138225148468043)].
  Native line: `{"timestamp":"2025-09-24T09:32:42.572+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Safe Mode Boot defense-evasion Impair Defenses defense-evasion Disable Windows Event Logging defense-evasion Disable or Modify System Firewall defense-evasion Disable or Modify Linux Audit System defense-evasion Indicator Blocking
- `T1105` full rank >10, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `videoserver/logs/log/audit/audit.log` / `L0` / SHA256 `0ba072999ed6272a23c313e04265b3bc7254965240d281f83394c449cfc346dd`; hash and exact line verified. Strongest terms: [('wget', 6.371290213094355)].
  Native line: `type=PATH msg=audit(1758706361.442:13750): item=0 name="/usr/bin/wget" inode=19049 dev=fe:01 mode=0100755 ouid=0 ogid=0 rdev=00:00 nametype=NORMAL cap_fp=0 cap_fi=0 cap_fe=0 cap_fver=0 cap_f` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Ingress Tool Transfer command-and-control Ingress Tool Transfer Adversaries may transfer tools or other files from an external system into a compromised environment. Tools or files may be copied from an external adversary-controll
- `T1556` full rank >10, RRF rank 8, role POSTHOC_GOLD_DIAGNOSTIC; native `wazuh/logs/alerts/alerts.json` / `L1` / SHA256 `b5be558ce31d8ca65a561b73bf464af0566f9228ab8ab0e2b516edf12f5277a4`; hash and exact line verified. Strongest terms: [('pam_unix', 5.249837091643741), ('id', 4.79519844255895), ('agent', 2.855549981722559), ('manager', 2.719184562086555), ('policy', 2.641343475026679), ('ip', 2.142381968276939)].
  Native line: `{"timestamp":"2025-09-24T09:32:42.572+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Pluggable Authentication Modules credential-access defense-evasion persistence Password Filter DLL credential-access defense-evasion persistence Hybrid Identity credential-access defense-evasion persistence Network Provider DLL cr
## both_miss: 1-1-r0

Gold original: ['T1590.002', 'T1591']; parent: ['T1590', 'T1591'].
Full ranking: ['T1021', 'T1559', 'T1583', 'T1197', 'T1070', 'T1647', 'T1218', 'T1220', 'T1037', 'T1216']
RRF ranking: ['T1021', 'T1559', 'T1218', 'T1216', 'T1197', 'T1567', 'T1047', 'T1546', 'T1583', 'T1070']

Observed: dnsmasq auth response is NXDOMAIN for an attackbed.com hostname. Top1 T1021 matches auth/com/is; com is a domain suffix here. Knowledge includes remote-services terminology and references containing com. Reasonable inference: the tokenizer conflates a hostname suffix with document vocabulary and scores incidental overlap. This does not prove remote-service execution, nor does the miss prove missing logs or an incorrect reconnaissance label.

- `T1021` full rank 1, RRF rank 1, role prediction_top1; native `corpdns/logs/log/syslog` / `L1` / SHA256 `b72f64ecb35531e6f0d2b7e74e6d494ba31a0b0994534d29d66a571a8c55e373`; hash and exact line verified. Strongest terms: [('com', 4.447692135953658), ('auth', 2.4292767197847143), ('is', 0.8874093387410478)].
  Native line: `Sep 22 07:42:45 corpdns dnsmasq[804]: auth nagios.attackbed.com is NXDOMAIN` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: VNC lateral-movement SSH lateral-movement Direct Cloud VM Connections lateral-movement SMB/Windows Admin Shares lateral-movement Remote Services lateral-movement Windows Remote Management lateral-movement Distributed Component Obj
- `T1590` full rank >10, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `corpdns/logs/log/syslog` / `L0` / SHA256 `405bbd734b8b909f88039c69f1dee5f197d06092ea412f846b6d30410ca0d767`; hash and exact line verified. Strongest terms: [('from', 0.29785348891013547)].
  Native line: `Sep 22 07:42:45 corpdns dnsmasq[804]: auth[A] nagios.attackbed.com from 192.42.1.174` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: IP Addresses reconnaissance DNS reconnaissance Network Topology reconnaissance Network Trust Dependencies reconnaissance Network Security Appliances reconnaissance Gather Victim Network Information reconnaissance Domain Properties
- `T1591` full rank >10, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `corpdns/logs/log/syslog` / `L0` / SHA256 `405bbd734b8b909f88039c69f1dee5f197d06092ea412f846b6d30410ca0d767`; hash and exact line verified. Strongest terms: [].
  Native line: `Sep 22 07:42:45 corpdns dnsmasq[804]: auth[A] nagios.attackbed.com from 192.42.1.174` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Identify Business Tempo reconnaissance Business Relationships reconnaissance Gather Victim Org Information reconnaissance Identify Roles reconnaissance Determine Physical Locations reconnaissance Identify Business Tempo Adversarie
## both_miss: 1-1-r1

Gold original: ['T1590.002', 'T1591']; parent: ['T1590', 'T1591'].
Full ranking: ['T1021', 'T1119', 'T1111', 'T1496', 'T1621', 'T1559', 'T1553', 'T1583', 'T1197', 'T1070']
RRF ranking: ['T1496', 'T1021', 'T1111', 'T1553', 'T1621', 'T1559', 'T1119', 'T1218', 'T1216', 'T1598']

Observed: dnsmasq auth response is NXDOMAIN for an attackbed.com hostname. Top1 T1021 matches auth/com/is; com is a domain suffix here. Knowledge includes remote-services terminology and references containing com. Reasonable inference: the tokenizer conflates a hostname suffix with document vocabulary and scores incidental overlap. This does not prove remote-service execution, nor does the miss prove missing logs or an incorrect reconnaissance label.

- `T1021` full rank 1, RRF rank 2, role prediction_top1; native `corpdns/logs/log/syslog` / `L1` / SHA256 `3ea15840f3f6eaf8a83b1d7b3225d3e6e692edfa18f75294f7583ce9e17db060`; hash and exact line verified. Strongest terms: [('com', 4.447692135953658), ('auth', 2.4292767197847143), ('is', 0.8874093387410478)].
  Native line: `Sep 24 12:34:51 corpdns dnsmasq[801]: auth camping.attackbed.com is NXDOMAIN` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: VNC lateral-movement SSH lateral-movement Direct Cloud VM Connections lateral-movement SMB/Windows Admin Shares lateral-movement Remote Services lateral-movement Windows Remote Management lateral-movement Distributed Component Obj
- `T1590` full rank >10, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `corpdns/logs/log/syslog` / `L8` / SHA256 `f98666c7b07e3d8094882279ebd919eb1d6b47131071fcd34f40f13316c0026b`; hash and exact line verified. Strongest terms: [('autodiscover', 2.7794452315967955), ('from', 0.29785348891013547)].
  Native line: `Sep 24 12:34:51 corpdns dnsmasq[801]: auth[A] autodiscover.sms.attackbed.com from 192.42.1.174` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: IP Addresses reconnaissance DNS reconnaissance Network Topology reconnaissance Network Trust Dependencies reconnaissance Network Security Appliances reconnaissance Gather Victim Network Information reconnaissance Domain Properties
- `T1591` full rank >10, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `corpdns/logs/log/syslog` / `L0` / SHA256 `852359f35e1ccd3a4823b875c6c8d3fc7c1fc232d9d12e42764b166ecea261bd`; hash and exact line verified. Strongest terms: [].
  Native line: `Sep 24 12:34:51 corpdns dnsmasq[801]: auth[A] camping.attackbed.com from 192.42.1.174` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Identify Business Tempo reconnaissance Business Relationships reconnaissance Gather Victim Org Information reconnaissance Identify Roles reconnaissance Determine Physical Locations reconnaissance Identify Business Tempo Adversarie
## multigold_partial: 1-29-r3

Gold original: ['T1105', 'T1556.003']; parent: ['T1105', 'T1556'].
Full ranking: ['T1562', 'T1027', 'T1110', 'T1546', 'T1505', 'T1556', 'T1552', 'T1499', 'T1036', 'T1559']
RRF ranking: ['T1027', 'T1505', 'T1562', 'T1552', 'T1110', 'T1556', 'T1553', 'T1546', 'T1543', 'T1036']

Observed: native HTTP alert contains Wget, ELF download and /pam_unix.so. Candidate parent T1556 appears at rank 6, T1105 is absent from Top10; top1 is T1562 with strong envelope-word overlap. Partial parent-level label coverage is therefore one of two gold techniques; no authentication modification is independently verified. Reasonable inference: lexical envelope terms dominate rank; a file path alone cannot establish the full labeled behavior.

- `T1562` full rank 1, RRF rank 3, role prediction_top1; native `wazuh/logs/alerts/alerts.json` / `L1` / SHA256 `9ea8c769ca8b5455db31647ecd3cc94340e9fba18e98af8814566f303c52b220`; hash and exact line verified. Strongest terms: [('start', 4.183201963932025), ('category', 4.174282507371437), ('status', 3.900140529412493), ('policy', 3.2252363466882517), ('rule', 3.083992406875962), ('log', 2.8138225148468043)].
  Native line: `{"timestamp":"2025-10-14T11:25:31.888+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Safe Mode Boot defense-evasion Impair Defenses defense-evasion Disable Windows Event Logging defense-evasion Disable or Modify System Firewall defense-evasion Disable or Modify Linux Audit System defense-evasion Indicator Blocking
- `T1105` full rank >10, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `inetfw/logs/log/suricata/fast.log` / `L1` / SHA256 `e0713794a23533c5507448ece46eb26909f7dd072c08b85bf32981eba4d818f6`; hash and exact line verified. Strongest terms: [('download', 4.264544747726557), ('file', 2.003655974553492), ('and', 0.24748725056250254)].
  Native line: `10/14/2025-11:25:31.150108  [**] [1:2019240:14] ET POLICY Executable and linking format (ELF) file download Over HTTP [**] [Classification: Potential Corporate Privacy Violation] [Priority: ` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Ingress Tool Transfer command-and-control Ingress Tool Transfer Adversaries may transfer tools or other files from an external system into a compromised environment. Tools or files may be copied from an external adversary-controll
- `T1556` full rank 6, RRF rank 6, role POSTHOC_GOLD_DIAGNOSTIC; native `wazuh/logs/alerts/alerts.json` / `L1` / SHA256 `9ea8c769ca8b5455db31647ecd3cc94340e9fba18e98af8814566f303c52b220`; hash and exact line verified. Strongest terms: [('pam_unix', 5.249837091643741), ('id', 4.79519844255895), ('agent', 2.855549981722559), ('manager', 2.719184562086555), ('policy', 2.641343475026679), ('ip', 2.142381968276939)].
  Native line: `{"timestamp":"2025-10-14T11:25:31.888+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Pluggable Authentication Modules credential-access defense-evasion persistence Password Filter DLL credential-access defense-evasion persistence Hybrid Identity credential-access defense-evasion persistence Network Provider DLL cr
## multigold_partial: 1-29-r4

Gold original: ['T1105', 'T1556.003']; parent: ['T1105', 'T1556'].
Full ranking: ['T1562', 'T1027', 'T1110', 'T1546', 'T1505', 'T1556', 'T1552', 'T1499', 'T1036', 'T1559']
RRF ranking: ['T1027', 'T1505', 'T1562', 'T1552', 'T1110', 'T1556', 'T1553', 'T1546', 'T1543', 'T1036']

Observed: native HTTP alert contains Wget, ELF download and /pam_unix.so. Candidate parent T1556 appears at rank 6, T1105 is absent from Top10; top1 is T1562 with strong envelope-word overlap. Partial parent-level label coverage is therefore one of two gold techniques; no authentication modification is independently verified. Reasonable inference: lexical envelope terms dominate rank; a file path alone cannot establish the full labeled behavior.

- `T1562` full rank 1, RRF rank 3, role prediction_top1; native `wazuh/logs/alerts/alerts.json` / `L1` / SHA256 `9ea8c769ca8b5455db31647ecd3cc94340e9fba18e98af8814566f303c52b220`; hash and exact line verified. Strongest terms: [('start', 4.183201963932025), ('category', 4.174282507371437), ('status', 3.900140529412493), ('policy', 3.2252363466882517), ('rule', 3.083992406875962), ('log', 2.8138225148468043)].
  Native line: `{"timestamp":"2025-10-14T11:25:31.888+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Safe Mode Boot defense-evasion Impair Defenses defense-evasion Disable Windows Event Logging defense-evasion Disable or Modify System Firewall defense-evasion Disable or Modify Linux Audit System defense-evasion Indicator Blocking
- `T1105` full rank >10, RRF rank >10, role POSTHOC_GOLD_DIAGNOSTIC; native `inetfw/logs/log/suricata/fast.log` / `L1` / SHA256 `e0713794a23533c5507448ece46eb26909f7dd072c08b85bf32981eba4d818f6`; hash and exact line verified. Strongest terms: [('download', 4.264544747726557), ('file', 2.003655974553492), ('and', 0.24748725056250254)].
  Native line: `10/14/2025-11:25:31.150108  [**] [1:2019240:14] ET POLICY Executable and linking format (ELF) file download Over HTTP [**] [Classification: Potential Corporate Privacy Violation] [Priority: ` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Ingress Tool Transfer command-and-control Ingress Tool Transfer Adversaries may transfer tools or other files from an external system into a compromised environment. Tools or files may be copied from an external adversary-controll
- `T1556` full rank 6, RRF rank 6, role POSTHOC_GOLD_DIAGNOSTIC; native `wazuh/logs/alerts/alerts.json` / `L1` / SHA256 `9ea8c769ca8b5455db31647ecd3cc94340e9fba18e98af8814566f303c52b220`; hash and exact line verified. Strongest terms: [('pam_unix', 5.249837091643741), ('id', 4.79519844255895), ('agent', 2.855549981722559), ('manager', 2.719184562086555), ('policy', 2.641343475026679), ('ip', 2.142381968276939)].
  Native line: `{"timestamp":"2025-10-14T11:25:31.888+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes` (full text and exact knowledge contexts saved in method/ERROR_CASES.json).
  Knowledge intro: Pluggable Authentication Modules credential-access defense-evasion persistence Password Filter DLL credential-access defense-evasion persistence Hybrid Identity credential-access defense-evasion persistence Network Provider DLL cr

Every cited native line was checked against the actual predictor input and its SHA256 recomputed. Representative-line scores are lexical traces; they do not fully decompose candidate source calibration or establish attack truth. Gold semantics are dataset labels, not independently verified by this audit. No missing-data, wrong-label, or causal-error claim follows from a Top10 miss.
