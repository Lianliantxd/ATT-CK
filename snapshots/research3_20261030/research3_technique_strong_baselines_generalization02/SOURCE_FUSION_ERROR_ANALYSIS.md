# Source fusion error analysis

P0 is PUBLIC_EXPOSED_DEVELOPMENT. These are post-hoc diagnostics, not independent validation. Five queries per step are correlated; query counts below must not be treated as independent trials. Labels are read only by this analysis, after prediction files exist.

| Knowledge / scorer | Method | Top1 | Top5 | Top10 | MRR |
|---|---|---:|---:|---:|---:|
| K2_bm25 | Max | 0.031795 | 0.145641 | 0.254359 | 0.084862 |
| K2_bm25 | Mean | 0.064615 | 0.172308 | 0.241026 | 0.111597 |
| K2_bm25 | RRF | 0.069744 | 0.147692 | 0.228718 | 0.106547 |
| K2_bm25 | SourceScoreNormalization | 0.068718 | 0.176410 | 0.243077 | 0.111829 |
| K2_bm25 | EvidenceLineFusion | 0.026667 | 0.152821 | 0.242051 | 0.081291 |
| K2_bm25 | EvidenceLineFusion_NoLineSelection | 0.025641 | 0.137436 | 0.244103 | 0.078976 |
| K2_bm25 | EvidenceLineFusion_NoDiscrimination | 0.034872 | 0.157949 | 0.226667 | 0.082665 |
| K2_bm25 | EvidenceLineFusion_NoSourceCalibration | 0.030769 | 0.151795 | 0.229744 | 0.083763 |
| K2_word | Max | 0.041026 | 0.149744 | 0.217436 | 0.081991 |
| K2_word | Mean | 0.045128 | 0.171282 | 0.250256 | 0.094032 |
| K2_word | RRF | 0.046154 | 0.147692 | 0.232821 | 0.088861 |
| K2_word | SourceScoreNormalization | 0.046154 | 0.158974 | 0.255385 | 0.095995 |
| K2_word | EvidenceLineFusion | 0.030769 | 0.139487 | 0.250256 | 0.078654 |
| K2_word | EvidenceLineFusion_NoLineSelection | 0.029744 | 0.110769 | 0.245128 | 0.075358 |
| K2_word | EvidenceLineFusion_NoDiscrimination | 0.027692 | 0.146667 | 0.213333 | 0.073076 |
| K2_word | EvidenceLineFusion_NoSourceCalibration | 0.030769 | 0.145641 | 0.267692 | 0.081337 |
| K3_bm25 | Max | 0.021538 | 0.160000 | 0.253333 | 0.080860 |
| K3_bm25 | Mean | 0.058462 | 0.171282 | 0.247179 | 0.109575 |
| K3_bm25 | RRF | 0.060513 | 0.155897 | 0.231795 | 0.103206 |
| K3_bm25 | SourceScoreNormalization | 0.061538 | 0.171282 | 0.247179 | 0.109479 |
| K3_bm25 | EvidenceLineFusion | 0.026667 | 0.161026 | 0.255385 | 0.082662 |
| K3_bm25 | EvidenceLineFusion_NoLineSelection | 0.025641 | 0.137436 | 0.246154 | 0.079809 |
| K3_bm25 | EvidenceLineFusion_NoDiscrimination | 0.030769 | 0.158974 | 0.231795 | 0.079995 |
| K3_bm25 | EvidenceLineFusion_NoSourceCalibration | 0.030769 | 0.161026 | 0.246154 | 0.085913 |

The preregistered candidate does not establish superiority: its Top10 is above RRF on all three conditions, but its Top1 and MRR are lower. Simple normalized mean has higher MRR than RRF on K2 BM25, K2 TF-IDF and K3 BM25. A Top10-only win must not be represented as better ranking overall. The TF-IDF no-source-calibration ablation has the largest Top10 of these runs; this is an exposed-data ablation, not a newly selected production method.


## K2_bm25: paired query disagreements

Top1: candidate-only hits 5; RRF-only hits 47; net -42 / 975.
Top10: candidate-only hits 37; RRF-only hits 24; net 13 / 975.

Candidate-only hit example: `3-16-r0`; GT ['T1053.003', 'T1105', 'T1071.001']; RRF ['T1036', 'T1134', 'T1003', 'T1037', 'T1562', 'T1546', 'T1070', 'T1547', 'T1218', 'T1548']; candidate ['T1036', 'T1003', 'T1134', 'T1562', 'T1037', 'T1548', 'T1070', 'T1546', 'T1218', 'T1053'].
Top-ranked candidate representative trace: source `reposerver/logs/log/audit/audit.log`, line `L2`, hash `d8ac4771906749993d91bacc0e28d68084d27f69f6a1eeb92963c83bce2be017`. Native text: `type=SYSCALL msg=audit(1765535870.136:17063): arch=c000003e syscall=82 success=yes exit=0 a0=55a3c12c3190 a1=55a3c1559800 a2=7ffff63253b0 a3=0 items=4 ppid=4266 pid=4787 auid=1002 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=pts2 ses=5 comm="vim" exe="/usr/bin/vim.basic" subj=unconfined
ARCH=x86_64 SYSCALL=rename AUID="john" UID="root" GID="root" EUID="root" SUID="root" FSUID="root" EGID="root" SGID="root" FSGID="root"`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

Candidate-only hit example: `3-50-r0`; GT ['T1036.005', 'T1564.001']; RRF ['T1218', 'T1070', 'T1553', 'T1134', 'T1059', 'T1003', 'T1562', 'T1546', 'T1547', 'T1543']; candidate ['T1218', 'T1562', 'T1553', 'T1070', 'T1037', 'T1543', 'T1036', 'T1528', 'T1546', 'T1548'].
Top-ranked candidate representative trace: source `reposerver/logs/log/syslog`, line `L0`, hash `53c455d207bbb562a8560ac6d2f969fece32dd3a6f63ac915ed0607ce47d5640`. Native text: `Dec 12 18:20:40 puppet snapd[3232]: storehelpers.go:916: cannot refresh: snap has no updates available: "core20", "lxd", "snapd"`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

RRF-only hit example: `1-29-r0`; GT ['T1105', 'T1556.003']; RRF ['T1562', 'T1036', 'T1546', 'T1027', 'T1543', 'T1553', 'T1574', 'T1556', 'T1003', 'T1559']; candidate ['T1562', 'T1036', 'T1546', 'T1027', 'T1559', 'T1553', 'T1110', 'T1003', 'T1548', 'T1543'].
Top-ranked candidate representative trace: source `wazuh/logs/alerts/alerts.json`, line `L1`, hash `b5be558ce31d8ca65a561b73bf464af0566f9228ab8ab0e2b516edf12f5277a4`. Native text: `{"timestamp":"2025-09-24T09:32:42.572+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes":736,"mail":false,"groups":["ids","suricata"]},"agent":{"id":"001","name":"inetfw","ip":"192.168.100.254"},"manager":{"name":"wazuh"},"id":"1758706362.11380113","decoder":{"name":"json"},"data":{"timestamp":"2025-09-24T09:32:41.754640+0000","flow_id":"900228277956940.000000","in_iface":"ens5","event_type":"alert","src_ip":"192.42.1.174","src_port":"80","dest_ip":"172.17.100.121","dest_port":"50990","proto":"TCP","metadata":{"flowbits":["http.dottedquadhost","ET.ELFDownload"]},"community_id":"1:g+4iCiKcppMnNbx6GCofzL0lLb0=","tx_id":"0","alert":{"action":"allowed","gid":"1","signature_id":"2019240","rev":"14","signature":"ET POLICY Executable and linking format (ELF) file download Over HTTP","category":"Potential Corporate Privacy Violation","severity":"1","metadata":{"confidence":["High"],"created_at":["2014_09_25"],"signature_severity":["Informational"],"updated_at":["2023_04_12"]}},"http":{"hostname":"192.42.1.174","url":"/pam_unix.so","http_user_agent":"Wget/1.21","http_method":"GET","protocol":"HTTP/1.1","status":"200","length":"69235"},"files":[{"filename":"/pam_unix.so","sid":[],"gaps":false,"state":"UNKNOWN","stored":false,"size":69235,"tx_id":0}],"app_proto":"http","flow":{"pkts_toserver":"11","pkts_toclient":"53","bytes_toserver":"870","bytes_toclient":"74396","start":"2025-09-24T09:32:41.749900+0000"}},"location":"/var/log/suricata/eve.json"}`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

RRF-only hit example: `2-4-r0`; GT ['T1547', 'T1569']; RRF ['T1036', 'T1562', 'T1546', 'T1070', 'T1547', 'T1037', 'T1574', 'T1218', 'T1003', 'T1543']; candidate ['T1036', 'T1562', 'T1548', 'T1037', 'T1003', 'T1134', 'T1546', 'T1574', 'T1070', 'T1543'].
Top-ranked candidate representative trace: source `videoserver/logs/log/audit/audit.log`, line `L9`, hash `d19927785ccd3fd7e418535eb6b23b2f4a775e671be270c293717733f4edb50a`. Native text: `type=SYSCALL msg=audit(1759313746.209:4663): arch=c000003e syscall=82 success=yes exit=0 a0=55942c8841e0 a1=7fff69185e3e a2=55942c8841e0 a3=fffffffffffff28e items=5 ppid=2802 pid=2850 auid=0 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=(none) ses=6 comm="sed" exe="/usr/bin/sed" subj==unconfined
ARCH=x86_64 SYSCALL=rename AUID="root" UID="root" GID="root" EUID="root" SUID="root" FSUID="root" EGID="root" SGID="root" FSGID="root"`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

## K2_word: paired query disagreements

Top1: candidate-only hits 4; RRF-only hits 19; net -15 / 975.
Top10: candidate-only hits 62; RRF-only hits 45; net 17 / 975.

Candidate-only hit example: `1-27-r0`; GT ['T1124']; RRF ['T1036', 'T1562', 'T1053', 'T1546', 'T1037', 'T1548', 'T1070', 'T1547', 'T1543', 'T1003']; candidate ['T1562', 'T1526', 'T1124', 'T1037', 'T1070', 'T1074', 'T1053', 'T1036', 'T1546', 'T1548'].
Top-ranked candidate representative trace: source `videoserver/logs/log/audit/audit.log`, line `L0`, hash `18935de2951054e006a41c627d2340989e80ac9cad341cde22726bd3d937d441`. Native text: `type=PROCTITLE msg=audit(1758711322.936:13630): proctitle=737368643A20726F6F74406E6F747479`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

Candidate-only hit example: `1-38-r0`; GT ['T1105', 'T1136.001']; RRF ['T1562', 'T1036', 'T1037', 'T1548', 'T1546', 'T1053', 'T1070', 'T1547', 'T1543', 'T1003']; candidate ['T1562', 'T1526', 'T1070', 'T1037', 'T1105', 'T1036', 'T1007', 'T1546', 'T1548', 'T1543'].
Top-ranked candidate representative trace: source `videoserver/logs/log/audit/audit.log`, line `L5`, hash `3196cc729d6f72f6e19f876c597119ad08ec355fadbfeb22e0987c6f064756fc`. Native text: `type=PROCTITLE msg=audit(1758523424.869:13134): proctitle=77676574002D4F00524541444D452E74787400687474703A2F2F3139322E34322E312E3137342F524541444D452E7478742E32`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

RRF-only hit example: `1-42-r0`; GT ['T1218', 'T1556.003']; RRF ['T1562', 'T1036', 'T1546', 'T1027', 'T1574', 'T1218', 'T1552', 'T1553', 'T1201', 'T1615']; candidate ['T1562', 'T1201', 'T1027', 'T1110', 'T1546', 'T1036', 'T1620', 'T1552', 'T1553', 'T1574'].
Top-ranked candidate representative trace: source `wazuh/logs/alerts/alerts.json`, line `L0`, hash `087ee1dd6167a16aa7072f64f8ef2a50756da03b9d4573b3bfe1fc543e9783af`. Native text: `{"timestamp":"2025-09-22T08:01:28.310+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes":2,"mail":false,"groups":["ids","suricata"]},"agent":{"id":"001","name":"inetfw","ip":"192.168.100.254"},"manager":{"name":"wazuh"},"id":"1758528088.11385497","decoder":{"name":"json"},"data":{"timestamp":"2025-09-22T08:01:28.712438+0000","flow_id":"1410319123008366.000000","in_iface":"ens5","event_type":"alert","src_ip":"192.42.1.174","src_port":"80","dest_ip":"172.17.100.121","dest_port":"60764","proto":"TCP","metadata":{"flowbits":["http.dottedquadhost","ET.ELFDownload"]},"community_id":"1:s4mgHq96m6LN0vpZkXJz4WSQz7M=","tx_id":"0","alert":{"action":"allowed","gid":"1","signature_id":"2019240","rev":"14","signature":"ET POLICY Executable and linking format (ELF) file download Over HTTP","category":"Potential Corporate Privacy Violation","severity":"1","metadata":{"confidence":["High"],"created_at":["2014_09_25"],"signature_severity":["Informational"],"updated_at":["2023_04_12"]}},"http":{"hostname":"192.42.1.174","url":"/pam_unix.so","http_user_agent":"Wget/1.21","http_method":"GET","protocol":"HTTP/1.1","status":"200","length":"41435"},"files":[{"filename":"/pam_unix.so","sid":[],"gaps":false,"state":"UNKNOWN","stored":false,"size":41435,"tx_id":0}],"app_proto":"http","flow":{"pkts_toserver":"12","pkts_toclient":"33","bytes_toserver":"936","bytes_toclient":"45276","start":"2025-09-22T08:01:28.707438+0000"}},"location":"/var/log/suricata/eve.json"}`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

RRF-only hit example: `2-1-r0`; GT ['T1021.004']; RRF ['T1053', 'T1037', 'T1543', 'T1546', 'T1563', 'T1187', 'T1558', 'T1021', 'T1036', 'T1056']; candidate ['T1053', 'T1543', 'T1123', 'T1037', 'T1546', 'T1651', 'T1559', 'T1036', 'T1558', 'T1563'].
Top-ranked candidate representative trace: source `videoserver/logs/log/syslog`, line `L4`, hash `0e25c3e1a79a376e765aaa58ccd09b8d5661f15523c60ba2e192b3b3b499e180`. Native text: `Oct  1 10:14:15 videoserver systemd[2805]: Reached target Timers.`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

## K3_bm25: paired query disagreements

Top1: candidate-only hits 8; RRF-only hits 41; net -33 / 975.
Top10: candidate-only hits 50; RRF-only hits 27; net 23 / 975.

Candidate-only hit example: `1-38-r0`; GT ['T1105', 'T1136.001']; RRF ['T1036', 'T1562', 'T1546', 'T1547', 'T1037', 'T1003', 'T1548', 'T1574', 'T1543', 'T1070']; candidate ['T1036', 'T1562', 'T1037', 'T1003', 'T1548', 'T1546', 'T1053', 'T1553', 'T1543', 'T1105'].
Top-ranked candidate representative trace: source `videoserver/logs/log/audit/audit.log`, line `L0`, hash `9d3ef6d61f17b897b5d0de79ee6dc6b678c81fd3be68fe1cf9fcde47b57707c0`. Native text: `type=SYSCALL msg=audit(1758523424.869:13134): arch=c000003e syscall=59 success=yes exit=0 a0=55936f2cd860 a1=55936f2cd910 a2=55936f2dc2e0 a3=fffffffffffff286 items=3 ppid=16915 pid=16927 auid=4294967295 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=pts0 ses=4294967295 comm="wget" exe="/usr/bin/wget" subj==unconfined
ARCH=x86_64 SYSCALL=execve AUID="unset" UID="root" GID="root" EUID="root" SUID="root" FSUID="root" EGID="root" SGID="root" FSGID="root"`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

Candidate-only hit example: `1-41-r0`; GT ['T1105', 'T1556.003']; RRF ['T1036', 'T1562', 'T1546', 'T1547', 'T1037', 'T1003', 'T1548', 'T1574', 'T1543', 'T1070']; candidate ['T1036', 'T1562', 'T1037', 'T1003', 'T1548', 'T1546', 'T1053', 'T1553', 'T1543', 'T1105'].
Top-ranked candidate representative trace: source `videoserver/logs/log/audit/audit.log`, line `L0`, hash `7922e0d39481a376444d48d380ce6771e9a643cbfba403bd1418722bd7347478`. Native text: `type=SYSCALL msg=audit(1758718398.999:13228): arch=c000003e syscall=59 success=yes exit=0 a0=55cb6c0cdf80 a1=55cb6c0ce030 a2=55cb6bfe78e0 a3=fffffffffffff286 items=3 ppid=17164 pid=17174 auid=0 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=pts1 ses=6 comm="wget" exe="/usr/bin/wget" subj==unconfined
ARCH=x86_64 SYSCALL=execve AUID="root" UID="root" GID="root" EUID="root" SUID="root" FSUID="root" EGID="root" SGID="root" FSGID="root"`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

RRF-only hit example: `1-29-r0`; GT ['T1105', 'T1556.003']; RRF ['T1562', 'T1036', 'T1546', 'T1027', 'T1556', 'T1553', 'T1543', 'T1574', 'T1003', 'T1559']; candidate ['T1562', 'T1036', 'T1546', 'T1027', 'T1559', 'T1110', 'T1553', 'T1003', 'T1548', 'T1543'].
Top-ranked candidate representative trace: source `wazuh/logs/alerts/alerts.json`, line `L1`, hash `b5be558ce31d8ca65a561b73bf464af0566f9228ab8ab0e2b516edf12f5277a4`. Native text: `{"timestamp":"2025-09-24T09:32:42.572+0000","rule":{"level":3,"description":"Suricata: Alert - ET POLICY Executable and linking format (ELF) file download Over HTTP","id":"86601","firedtimes":736,"mail":false,"groups":["ids","suricata"]},"agent":{"id":"001","name":"inetfw","ip":"192.168.100.254"},"manager":{"name":"wazuh"},"id":"1758706362.11380113","decoder":{"name":"json"},"data":{"timestamp":"2025-09-24T09:32:41.754640+0000","flow_id":"900228277956940.000000","in_iface":"ens5","event_type":"alert","src_ip":"192.42.1.174","src_port":"80","dest_ip":"172.17.100.121","dest_port":"50990","proto":"TCP","metadata":{"flowbits":["http.dottedquadhost","ET.ELFDownload"]},"community_id":"1:g+4iCiKcppMnNbx6GCofzL0lLb0=","tx_id":"0","alert":{"action":"allowed","gid":"1","signature_id":"2019240","rev":"14","signature":"ET POLICY Executable and linking format (ELF) file download Over HTTP","category":"Potential Corporate Privacy Violation","severity":"1","metadata":{"confidence":["High"],"created_at":["2014_09_25"],"signature_severity":["Informational"],"updated_at":["2023_04_12"]}},"http":{"hostname":"192.42.1.174","url":"/pam_unix.so","http_user_agent":"Wget/1.21","http_method":"GET","protocol":"HTTP/1.1","status":"200","length":"69235"},"files":[{"filename":"/pam_unix.so","sid":[],"gaps":false,"state":"UNKNOWN","stored":false,"size":69235,"tx_id":0}],"app_proto":"http","flow":{"pkts_toserver":"11","pkts_toclient":"53","bytes_toserver":"870","bytes_toclient":"74396","start":"2025-09-24T09:32:41.749900+0000"}},"location":"/var/log/suricata/eve.json"}`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

RRF-only hit example: `1-44-r0`; GT ['T1218', 'T1098.004']; RRF ['T1562', 'T1036', 'T1546', 'T1547', 'T1037', 'T1003', 'T1574', 'T1543', 'T1548', 'T1218']; candidate ['T1036', 'T1562', 'T1037', 'T1003', 'T1548', 'T1546', 'T1543', 'T1070', 'T1053', 'T1553'].
Top-ranked candidate representative trace: source `videoserver/logs/log/audit/audit.log`, line `L0`, hash `e37a57c6fb5cb341a02e4f705b7ef9c5115a868b19da02ce41404fc65c903cfb`. Native text: `type=SYSCALL msg=audit(1758532669.777:13178): arch=c000003e syscall=59 success=yes exit=0 a0=7ffd9dd8eeb8 a1=7ffd9dd8c930 a2=55e8cd4a2ae0 a3=7ffd9dd8c970 items=3 ppid=17139 pid=17140 auid=4294967295 uid=0 gid=0 euid=0 suid=0 fsuid=0 egid=0 sgid=0 fsgid=0 tty=pts0 ses=4294967295 comm="bash" exe="/usr/bin/bash" subj==unconfined
ARCH=x86_64 SYSCALL=execve AUID="unset" UID="root" GID="root" EUID="root" SUID="root" FSUID="root" EGID="root" SGID="root" FSGID="root"`.
Interpretation limit: this native line is the strongest lexical-match line for the candidate in that source. It is a ranking trace, not a verified explanation of the true attack. Source calibration and overlap specificity may emphasize incidental tokens; causal failure classification needs manual native-log review.

## Audit and limitations

- Predictor imports no reference or evaluator, rejects reference/metadata top-level fields, and records input/knowledge hashes. All 975 queries and 216 candidates are preserved.
- Source unit is the prepared host+file source_id. Native source lines are concatenated without prompt wrapper or injected source headings. Compare with the same native-text concatenation baseline to distinguish source fusion from text cleanup.
- Max ties are attributed equally, zero-score RRF candidates never contribute, absent sources are not zeros, and score ties use ascending technique ID.
- Best-line traces include exact native line/hash and flattened knowledge-file hash/candidate ID. The underlying knowledge JSON is flat; original MITRE subsections cannot be recovered from this file.
- Representative-line evidence does not prove the line caused the full-source rank. Candidate mechanism aggregates up to three lines; its score is defined explicitly in METHOD_FORMAL_DEFINITION.md.
- Line selection, specificity and source calibration use fixed parameters, without search. NoLineSelection and NoDiscrimination have mixed effects; the full candidate is not consistently better than its ablations.
- These CPU lexical comparisons are stronger baseline engineering and a minimal candidate test, not semantic encoding, a trained detector, or a completed novel-method claim. External generalization is assessed separately by the root report.
