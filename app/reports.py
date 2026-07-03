from __future__ import annotations

import csv
import html
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from db import ROOT_DIR


SNAPSHOT_DIR = ROOT_DIR / "outputs" / "snapshots"
REPORT_DIR = ROOT_DIR / "outputs" / "reports"
DOCS_DIR = ROOT_DIR / "docs"


def ensure_dirs() -> None:
    for path in (SNAPSHOT_DIR, REPORT_DIR, DOCS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def save_outputs(tables: list[dict[str, Any]], columns: list[dict[str, Any]], indexes: list[dict[str, Any]], candidates: list[dict[str, Any]], issues: list[dict[str, Any]], production_usage: list[dict[str, Any]] | None = None) -> dict[str, Path]:
    ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    paths = {
        "tables_csv": SNAPSHOT_DIR / f"tables_{stamp}.csv",
        "columns_csv": SNAPSHOT_DIR / f"columns_{stamp}.csv",
        "indexes_csv": SNAPSHOT_DIR / f"indexes_{stamp}.csv",
        "candidates_csv": SNAPSHOT_DIR / f"business_candidates_{stamp}.csv",
        "issues_csv": SNAPSHOT_DIR / f"quality_issues_{stamp}.csv",
        "production_usage_csv": SNAPSHOT_DIR / f"production_material_usage_{stamp}.csv",
        "summary_json": SNAPSHOT_DIR / f"summary_{stamp}.json",
        "data_map": DOCS_DIR / "data-map.md",
        "html_report": REPORT_DIR / f"smart-report-demo_{stamp}.html",
    }

    write_csv(paths["tables_csv"], tables)
    write_csv(paths["columns_csv"], columns)
    write_csv(paths["indexes_csv"], indexes)
    write_csv(paths["candidates_csv"], candidates)
    production_usage = production_usage or []
    write_csv(paths["issues_csv"], issues)
    write_csv(paths["production_usage_csv"], production_usage)

    summary = build_summary(tables, columns, candidates, issues, production_usage)
    paths["summary_json"].write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    paths["data_map"].write_text(render_data_map(summary, candidates, issues), encoding="utf-8")
    paths["html_report"].write_text(render_html(summary, candidates, issues, production_usage), encoding="utf-8")
    return paths


def json_default(value: Any) -> str | float:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json_default(value) for key, value in row.items()})


def build_summary(tables: list[dict[str, Any]], columns: list[dict[str, Any]], candidates: list[dict[str, Any]], issues: list[dict[str, Any]], production_usage: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    total_rows = sum(int(row.get("row_count") or 0) for row in tables)
    non_empty = [row for row in tables if int(row.get("row_count") or 0) > 0]
    production_usage = production_usage or []
    module_counts: dict[str, int] = {}
    for item in candidates:
        module_counts[item["module_label"]] = module_counts.get(item["module_label"], 0) + 1
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "table_count": len(tables),
        "column_count": len(columns),
        "non_empty_table_count": len(non_empty),
        "estimated_total_rows": total_rows,
        "candidate_table_count": len(candidates),
        "quality_issue_count": len(issues),
        "production_usage_count": len(production_usage),
        "module_counts": module_counts,
        "top_tables": sorted(tables, key=lambda row: int(row.get("row_count") or 0), reverse=True)[:20],
        "top_issues": issues[:50],
    }


def render_data_map(summary: dict[str, Any], candidates: list[dict[str, Any]], issues: list[dict[str, Any]]) -> str:
    lines = [
        "# 智能报表数据地图",
        "",
        f"生成时间：{summary['generated_at']}",
        "",
        "## 数据库概览",
        "",
        f"- 表数量：{summary['table_count']}",
        f"- 字段数量：{summary['column_count']}",
        f"- 非空表数量：{summary['non_empty_table_count']}",
        f"- 估算总行数：{summary['estimated_total_rows']}",
        "",
        "## 业务表候选 Top 30",
        "",
        "| 模块 | 表 | 行数 | 命中关键词 |",
        "| --- | --- | ---: | --- |",
    ]
    for item in candidates[:30]:
        lines.append(f"| {item['module_label']} | `{item['full_name']}` | {item['row_count']} | {item['matched_keywords']} |")
    lines.extend(["", "## 数据质量问题 Top 30", "", "| 表 | 字段 | 问题 | 数量 | 比例 |", "| --- | --- | --- | ---: | ---: |"])
    for item in issues[:30]:
        lines.append(f"| `{item['schema_name']}.{item['table_name']}` | `{item['column_name']}` | {item['issue_type']} | {item['issue_count']} | {item['issue_rate']:.2%} |")
    lines.extend(["", "> 数据字典仅供参考，本数据地图以真实数据库扫描结果为准。"])
    return "\n".join(lines) + "\n"


def render_html(summary: dict[str, Any], candidates: list[dict[str, Any]], issues: list[dict[str, Any]], production_usage: list[dict[str, Any]] | None = None) -> str:
    def rows(items: list[dict[str, Any]], keys: list[str]) -> str:
        body = []
        for item in items:
            body.append("<tr>" + "".join(f"<td>{html.escape(str(json_default(item.get(key, ''))))}</td>" for key in keys) + "</tr>")
        return "\n".join(body)

    production_usage = production_usage or []
    usage_rows = rows(production_usage[:80], ["order_date", "manufacture_order_code", "product_name", "product_specification", "product_unit", "product_quantity", "material_name", "material_specification", "material_unit", "dispatched_quantity", "material_dispatch_code"])
    candidate_rows = rows(candidates[:40], ["module_label", "full_name", "row_count", "score", "matched_keywords"])
    issue_rows = rows(issues[:80], ["schema_name", "table_name", "column_name", "issue_type", "issue_count", "issue_rate", "detail"])
    top_table_rows = rows(summary["top_tables"], ["schema_name", "table_name", "row_count", "modify_date"])
    module_cards = "".join(f"<div class='card'><b>{k}</b><span>{v} 张候选表</span></div>" for k, v in summary["module_counts"].items())
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>智能报表 Demo 诊断报告</title>
<style>
:root {{ --bg:#f6f3ee; --panel:#fffdf8; --ink:#1f2933; --muted:#697386; --line:#e5ded2; --red:#c2410c; --blue:#1d4ed8; }}
body {{ margin:0; background:linear-gradient(135deg,#f6f3ee,#eef4ff); color:var(--ink); font-family:"Microsoft YaHei", "Segoe UI", sans-serif; }}
main {{ max-width:1180px; margin:0 auto; padding:36px 28px 64px; }}
h1 {{ font-size:34px; margin:0 0 8px; }}
h2 {{ margin-top:34px; border-left:5px solid var(--red); padding-left:12px; }}
.sub {{ color:var(--muted); margin-bottom:26px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:18px; box-shadow:0 12px 26px rgba(31,41,51,.07); }}
.card b {{ display:block; font-size:26px; color:var(--red); }}
.card span {{ color:var(--muted); }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); border-radius:14px; overflow:hidden; box-shadow:0 10px 22px rgba(31,41,51,.06); }}
th, td {{ padding:10px 12px; border-bottom:1px solid var(--line); text-align:left; font-size:13px; }}
th {{ background:#efe7da; color:#2f3a45; }}
.note {{ background:#fff7ed; border:1px solid #fed7aa; padding:14px 16px; border-radius:14px; color:#7c2d12; }}
</style>
</head>
<body><main>
<h1>智能报表 Demo 诊断报告</h1>
<div class="sub">生成时间：{summary['generated_at']}。数据字典仅供参考，本报告以真实数据库只读扫描结果为准。</div>
<div class="grid">
  <div class="card"><b>{summary['table_count']}</b><span>数据库表</span></div>
  <div class="card"><b>{summary['column_count']}</b><span>字段</span></div>
  <div class="card"><b>{summary['non_empty_table_count']}</b><span>非空表</span></div>
  <div class="card"><b>{summary['candidate_table_count']}</b><span>业务候选表</span></div>
  <div class="card"><b>{summary['production_usage_count']}</b><span>生产用料明细</span></div>
  <div class="card"><b>{summary['quality_issue_count']}</b><span>抽样质量问题</span></div>
</div>
<h2>业务分析：生产加工用料</h2>
<table><thead><tr><th>单据日期</th><th>加工单号</th><th>产品名称</th><th>规格型号</th><th>主单位</th><th>主数量</th><th>材料</th><th>材料规格</th><th>材料单位</th><th>出库数量</th><th>材料出库单号</th></tr></thead><tbody>{usage_rows}</tbody></table>
<h2>模块识别</h2>
<div class="grid">{module_cards}</div>
<h2>大表排行</h2>
<table><thead><tr><th>架构</th><th>表</th><th>估算行数</th><th>修改时间</th></tr></thead><tbody>{top_table_rows}</tbody></table>
<h2>核心业务表候选</h2>
<table><thead><tr><th>模块</th><th>表</th><th>行数</th><th>得分</th><th>命中关键词</th></tr></thead><tbody>{candidate_rows}</tbody></table>
<h2>数据质量问题抽样</h2>
<table><thead><tr><th>架构</th><th>表</th><th>字段</th><th>问题</th><th>数量</th><th>比例</th><th>说明</th></tr></thead><tbody>{issue_rows}</tbody></table>
<h2>下一步</h2>
<div class="note">请结合客户真实业务口径确认哪些空值、负数、异常日期属于业务允许情况。下一阶段应把客户人工报表样例映射到这些核心表上，形成正式经营指标。</div>
</main></body></html>"""
