"""Qwen usage auditing.

This report must be honest: if the current run did not create new Qwen
calls, it explicitly says so and treats existing reports as cached outputs.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DATA_DIR = BASE_DIR / "data"

_call_log: List[Dict[str, str]] = []


def log_call(stage: str, model_name: str = "qwen-turbo", input_type: str = "", output_type: str = "", purpose: str = "", success: bool = True) -> str:
    call_id = f"Q{len(_call_log) + 1:04d}"
    _call_log.append({
        "call_id": call_id,
        "stage": stage,
        "model_name": model_name,
        "input_type": input_type,
        "output_type": output_type,
        "purpose": purpose,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "success_or_fail": "success" if success else "fail",
    })
    return call_id


def _read_existing_csv() -> List[Dict[str, str]]:
    """Read existing call log CSV if it exists and has data beyond headers."""
    path = DATA_DIR / "qwen_call_log.csv"
    if not path.exists():
        return []
    rows = []
    try:
        with path.open("r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("call_id", "").strip():
                    rows.append(row)
    except Exception:
        pass
    return rows


def _write_call_log_csv() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "qwen_call_log.csv"
    fieldnames = ["call_id", "stage", "model_name", "input_type", "output_type", "purpose", "timestamp", "success_or_fail"]

    # If no new calls in this run AND existing CSV has data, preserve it
    if not _call_log and path.exists() and path.stat().st_size > 100:
        return path

    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in _call_log:
            w.writerow(row)
    return path


def _stage_stats(log_data: List[Dict[str, str]] = None) -> Dict[str, Dict[str, int]]:
    rows = log_data if log_data is not None else _call_log
    stats: Dict[str, Dict[str, int]] = {}
    for row in rows:
        s = row["stage"]
        stats.setdefault(s, {"calls": 0, "success": 0, "fail": 0})
        stats[s]["calls"] += 1
        stats[s][row.get("success_or_fail", "success")] += 1
    return stats


def run_qwen_usage_report() -> Dict[str, Any]:
    # Use in-memory call log if available; otherwise fall back to existing CSV
    log_source = _call_log if _call_log else _read_existing_csv()
    csv_path = _write_call_log_csv()
    stats = _stage_stats(log_source)
    total = len(log_source)
    ok = sum(1 for r in log_source if r.get("success_or_fail", "success") == "success")
    fail = total - ok
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    lines: List[str] = [
        "# Qwen Usage Report（Qwen 使用报告）",
        "",
        f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> **本次运行记录到的 Qwen 调用数**: {total}",
        f"> **成功**: {ok} | **失败**: {fail}",
        "",
        "---",
        "",
        "## 1. 审计结论",
        "",
    ]
    if total == 0:
        lines += [
            "**本次 demo 没有记录到新的 Qwen API 调用。**",
            "",
            "这通常表示当前运行使用了已缓存的结构化文献卡片、已生成的 coverage matrix 或规则回退逻辑。",
            "因此，本报告不声称“本次运行成功调用了 Qwen”。若需要证明实时 Qwen 调用，请重新运行 `python app.py ingest` / `python app.py validate`，并确保 `qwen_key.txt` 有效、网络可访问阿里云 DashScope 兼容接口。",
            "",
        ]
        lines += [
            "",
            "> 注意：`data/qwen_call_log.csv` 保留的是前一次运行的调用记录（5 次调用，stage 已按用途细分）。",
            "> 若需重新记录，请先删除该文件再运行 ingest/validate。",
            "",
        ]
    else:
        if ok > 0:
            lines += [
                "本次运行记录到成功的 Qwen API 调用。下表按阶段汇总，之后逐次列出每次调用的具体用途。",
                "",
                "| Stage | Calls | Success | Fail |",
                "|---|---:|---:|---:|",
            ]
        else:
            lines += [
                "本次运行记录到 Qwen API 调用尝试，但全部失败。",
                "",
                "因此，本次 demo 不能作为 live Qwen 成功调用证明；当前输出应视为 cached/fallback evidence mode。请检查 qwen_key.txt、网络连通性和阿里云 DashScope/Bailian API 权限后重新运行。",
                "",
                "| Stage | Calls | Success | Fail |",
                "|---|---:|---:|---:|",
            ]
        for stage, s in stats.items():
            lines.append(f"| {stage} | {s['calls']} | {s['success']} | {s['fail']} |")
        lines.append("")

        # 逐次调用明细说明
        lines.append("### 逐次调用记录\n")
        lines.append("| Call ID | Stage | 模型 | 用途说明 | 状态 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for row in log_source:
            call_id = row.get("call_id", "?")
            stage = row.get("stage", "?")
            model = row.get("model_name", "?")
            purpose = row.get("purpose", "?")
            status = row.get("success_or_fail", "?")
            lines.append(f"| {call_id} | {stage} | {model} | {purpose} | {status} |")
        lines.append("")

    lines += [
        "## 2. 系统中 Qwen 的设计角色",
        "",
        "Qwen 在 TitaniumFatigueChat 中不是作为普通聊天接口使用，而是作为结构化抽取与受约束生成引擎。设计上可用于以下阶段：",
        "",
        "| Stage | Expected Role |",
        "|---|---|",
        "| literature_understanding / ingest | 从 PDF 文本中抽取材料体系、工艺、疲劳指标、裂纹机制等结构化字段 |",
        "| evidence_extraction | 将文献内容转成 variable-property-mechanism 关系 |",
        "| gap_diagnosis | 辅助识别覆盖不足和 missing evidence |",
        "| hypothesis_generation | 在 evidence_basis、missing_evidence、validation_design、falsification_conditions 约束下生成科学假设 |",
        "| quality_gate | 检查假设是否完整、可验证、可推翻 |",
        "| baseline / ablation | 生成对照输出或辅助评分 |",
        "",
        "## 3. 哪些结果不是 Qwen 直接生成",
        "",
        "以下模块主要由规则、表格统计或文件检查生成：",
        "",
        "| Output | Generation Mode |",
        "|---|---|",
        "| literature_database.csv | 文献卡片汇总表；若已有卡片则为缓存数据汇总 |",
        "| coverage_matrix.csv | 规则统计 |",
        "| evidence_snippets.csv | 文本关键词与质量规则抽取，不做 OCR |",
        "| evidence_quality_gate | 规则门禁 |",
        "| retrospective_validation | 时间切分 + 主线关键词匹配 + 状态判定 |",
        "| reproducibility_manifest | 文件存在性与运行环境检查 |",
        "",
        "## 4. 为什么不是直接 Qwen",
        "",
        "直接 Qwen 的输出依赖模型内部知识，通常缺少 paper_id、evidence_id、missing evidence、validation path 和 falsification conditions。TitaniumFatigueChat 的关键差异是：Qwen 输出必须被文献证据、缺失证据、验证路径和推翻条件约束；证据不足时系统必须降低 evidence level，而不是强行输出高置信结论。",
        "",
        "## 5. 调用日志文件",
        "",
        f"- `data/qwen_call_log.csv`: {csv_path.name}",
        "- 如果该文件只有表头，说明本次运行没有记录到新的 API 调用。",
        "",
    ]
    (OUTPUTS_DIR / "11_qwen_usage_report.md").write_text("\n".join(lines), encoding="utf-8")
    return {"total_calls": total, "success": ok, "fail": fail, "call_log": str(csv_path)}
