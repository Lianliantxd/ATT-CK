"""Attach the disclosed session-scope timing limitation without changing results."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit_path = ROOT / "results/FUSION_INDEPENDENT_AUDIT.json"
disclosure_path = ROOT / "reports/EVALUATOR_GOLD_ACCESS_TIMING_DISCLOSURE.json"
report_path = ROOT / "reports/FUSION_INDEPENDENT_AUDIT.md"
audit = json.loads(audit_path.read_text())
assert audit["auditor_sha256"] == hashlib.sha256((ROOT / "fusion/independent_audit.py").read_bytes()).hexdigest()
assert audit["status"] == "PASS_WITH_SCOPE_LIMITATIONS"
assert audit["prediction_score_max_abs_error"] == 0 and audit["ranking_mismatches"] == 0
disclosure = json.loads(disclosure_path.read_text())
audit["session_timing_disclosure"] = {"path": str(disclosure_path.relative_to(ROOT)), "sha256": hashlib.sha256(disclosure_path.read_bytes()).hexdigest(), **disclosure}
limitation = "The parent disclosed early evaluation-agent access to old heldout references for existing corpus-count checks before main prediction completion; no whole-session claim of zero early Gold access is supported."
if limitation not in audit["limitations"]:
    audit["limitations"].append(limitation)
audit["timing_disclosure_addendum_source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
audit_path.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n")
report = report_path.read_text()
marker = "## 全会话Gold访问时序限制"
if marker not in report:
    report += "\n" + marker + "\n\n主agent向本审核披露：评价agent在主预测完成前的setup阶段读取旧heldout_reference，只用于核对已知975查询、195逻辑步骤和7场景计数；未提前计算本轮融合外层指标、未向拟合器或预测器传递Gold、未因此调整参数。这属于全会话Gold访问的时序偏差，因此不能声称本会话任何进程都未提前访问Gold。\n\n可独立核验的较窄结论是：fit/predict的read_paths与代码未读取外层reference，参数hash在拟合后与预测前一致，本审核重算全部选参和预测精确吻合。评价agent的setup时序来自主agent披露，不伪称操作系统审计所得。详情与证据类型见EVALUATOR_GOLD_ACCESS_TIMING_DISCLOSURE.json。该偏差与已曝光开发集性质共同限制结论，不改变分数和选参复算通过的事实。\n"
    report_path.write_text(report)
print("AUDIT_SCOPE_DISCLOSURE_ATTACHED")
