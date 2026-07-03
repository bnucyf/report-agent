from __future__ import annotations

import csv
import html
import json
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "app"))

from db import fetch_all  # noqa: E402
from reports import json_default, write_csv  # noqa: E402
from table_classifier import classify_tables, is_excluded_table  # noqa: E402

SNAPSHOT_DIR = ROOT_DIR / "outputs" / "snapshots"
REPORT_DIR = ROOT_DIR / "outputs" / "reports"
DOCS_DIR = ROOT_DIR / "docs"

TYPE_CATEGORY = {
    "date": "时间",
    "datetime": "时间",
    "datetime2": "时间",
    "smalldatetime": "时间",
    "time": "时间",
    "timestamp": "系统版本",
    "decimal": "金额/数量",
    "numeric": "金额/数量",
    "money": "金额/数量",
    "smallmoney": "金额/数量",
    "float": "金额/数量",
    "real": "金额/数量",
    "int": "编码/状态/外键",
    "bigint": "编码/状态/外键",
    "smallint": "编码/状态/外键",
    "tinyint": "编码/状态/外键",
    "bit": "布尔标记",
    "char": "文本/编码",
    "nchar": "文本/编码",
    "varchar": "文本/编码",
    "nvarchar": "文本/编码",
    "text": "文本/备注",
    "ntext": "文本/备注",
    "varbinary": "二进制/系统",
    "image": "二进制/系统",
}

SEMANTIC_KEYWORDS = [
    ("金额", ["amount", "money", "price", "cost", "tax", "fee", "balance", "debit", "credit", "金额", "价格", "成本", "税", "费用", "余额"]),
    ("数量", ["quantity", "count", "qty", "number", "数量", "件数"]),
    ("日期时间", ["date", "time", "year", "period", "日期", "时间", "年度", "期间"]),
    ("单据", ["voucher", "doc", "order", "code", "bill", "单据", "订单", "编号"]),
    ("存货物料", ["inventory", "material", "product", "sku", "batch", "存货", "物料", "产品", "批次"]),
    ("客户供应商", ["customer", "vendor", "supplier", "partner", "member", "客户", "供应商", "往来单位"]),
    ("仓库库存", ["warehouse", "stock", "rdrecord", "receive", "dispatch", "仓库", "库存", "出库", "入库"]),
    ("生产加工", ["manufacture", "bom", "process", "routing", "material", "生产", "加工", "工序", "材料"]),
    ("人员部门", ["person", "department", "clerk", "maker", "auditor", "员工", "部门", "制单", "审核"]),
    ("状态", ["state", "status", "flag", "disabled", "is", "状态", "标记", "是否"]),
    ("项目", ["project", "site", "construct", "项目", "工地", "施工"]),
]

MODULE_RULES = {
    "财务/会计": ["ar_", "ap_", "gl_", "fi_", "fa_", "voucher", "settle", "account", "receivable", "payable", "expense", "invoice"],
    "库存/仓库": ["st_", "rdrecord", "stock", "warehouse", "inventory", "subsidiarybook"],
    "生产/加工": ["mp_", "manufacture", "bom", "process", "material"],
    "销售": ["sa_", "sale", "dispatch", "customer"],
    "采购": ["pu_", "purchase", "arrival", "vendor", "supplier"],
    "基础档案": ["aa_", "inventoryentity", "unit", "partner", "department", "person"],
    "系统/流程": ["eap_", "sm_", "wfaudit", "message", "auth", "permission"],
}


def category_for_type(data_type: str) -> str:
    return TYPE_CATEGORY.get((data_type or "").lower(), "其他")


def semantic_for_column(table_name: str, column_name: str) -> str:
    text = f"{table_name} {column_name}".lower()
    hits = [label for label, words in SEMANTIC_KEYWORDS if any(word.lower() in text for word in words)]
    return ", ".join(hits) if hits else "未识别"


def module_for_table(table_name: str) -> str:
    name = table_name.lower()
    hits = [label for label, words in MODULE_RULES.items() if any(word in name for word in words)]
    return hits[0] if hits else "其他"


def fetch_tables() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            s.name AS schema_name,
            t.name AS table_name,
            SUM(CASE WHEN p.index_id IN (0, 1) THEN p.rows ELSE 0 END) AS row_count,
            t.create_date,
            t.modify_date
        FROM sys.tables t WITH (NOLOCK)
        INNER JOIN sys.schemas s WITH (NOLOCK) ON t.schema_id = s.schema_id
        LEFT JOIN sys.partitions p WITH (NOLOCK) ON t.object_id = p.object_id
        WHERE t.is_ms_shipped = 0
        GROUP BY s.name, t.name, t.create_date, t.modify_date
        ORDER BY row_count DESC, s.name, t.name
        """
    )


def fetch_columns() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT
            s.name AS schema_name,
            t.name AS table_name,
            c.name AS column_name,
            c.column_id,
            ty.name AS data_type,
            c.max_length,
            c.precision AS numeric_precision,
            c.scale AS numeric_scale,
            c.is_nullable,
            c.is_identity,
            CAST(NULL AS NVARCHAR(4000)) AS column_description
        FROM sys.columns c WITH (NOLOCK)
        INNER JOIN sys.tables t WITH (NOLOCK) ON c.object_id = t.object_id
        INNER JOIN sys.schemas s WITH (NOLOCK) ON t.schema_id = s.schema_id
        INNER JOIN sys.types ty WITH (NOLOCK) ON c.user_type_id = ty.user_type_id
        WHERE t.is_ms_shipped = 0
          AND t.name NOT LIKE 'TEMP[_]%'
          AND t.name NOT LIKE 'TMP[_]%'
          AND t.name NOT LIKE 'EAP[_]%'
          AND t.name NOT LIKE 'eap[_]%'
          AND t.name NOT LIKE '%[_]Rpt[_]%'
          AND t.name NOT LIKE '%Log%'
          AND t.name NOT LIKE '%Trace%'
          AND t.name NOT LIKE '%Backup%'
          AND t.name NOT LIKE '%[_]Index'
        ORDER BY s.name, t.name, c.column_id
        """
    )


def enrich_columns(tables: list[dict[str, Any]], columns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table_map = {f"{row['schema_name']}.{row['table_name']}": row for row in tables}
    enriched = []
    for col in columns:
        key = f"{col['schema_name']}.{col['table_name']}"
        table = table_map.get(key, {})
        table_name = str(col["table_name"])
        data_type = str(col["data_type"])
        enriched.append(
            {
                "schema_name": col["schema_name"],
                "table_name": table_name,
                "full_table_name": key,
                "module": module_for_table(table_name),
                "is_noise_table": is_excluded_table(table_name),
                "row_count": int(table.get("row_count") or 0),
                "table_create_date": table.get("create_date"),
                "table_modify_date": table.get("modify_date"),
                "column_id": col["column_id"],
                "column_name": col["column_name"],
                "data_type": data_type,
                "type_category": category_for_type(data_type),
                "semantic_category": semantic_for_column(table_name, str(col["column_name"])),
                "max_length": col["max_length"],
                "numeric_precision": col["numeric_precision"],
                "numeric_scale": col["numeric_scale"],
                "is_nullable": bool(col["is_nullable"]),
                "is_identity": bool(col["is_identity"]),
                "column_description": col.get("column_description"),
            }
        )
    return enriched


def summarize(tables: list[dict[str, Any]], columns: list[dict[str, Any]]) -> dict[str, Any]:
    non_noise_tables = [t for t in tables if not is_excluded_table(str(t["table_name"]))]
    module_table_counts = Counter(module_for_table(str(t["table_name"])) for t in non_noise_tables)
    module_row_counts = defaultdict(int)
    for table in non_noise_tables:
        module_row_counts[module_for_table(str(table["table_name"]))] += int(table.get("row_count") or 0)
    type_counts = Counter(c["type_category"] for c in columns)
    semantic_counts = Counter(c["semantic_category"] for c in columns)
    time_fields = [c for c in columns if c["type_category"] == "时间" or "日期时间" in c["semantic_category"]]
    amount_fields = [c for c in columns if "金额" in c["semantic_category"]]
    quantity_fields = [c for c in columns if "数量" in c["semantic_category"]]
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "table_count": len(tables),
        "non_noise_table_count": len(non_noise_tables),
        "column_count": len(columns),
        "estimated_total_rows": sum(int(t.get("row_count") or 0) for t in tables),
        "module_table_counts": dict(module_table_counts.most_common()),
        "module_row_counts": dict(sorted(module_row_counts.items(), key=lambda item: item[1], reverse=True)),
        "type_counts": dict(type_counts.most_common()),
        "semantic_counts": dict(semantic_counts.most_common()),
        "time_field_count": len(time_fields),
        "amount_field_count": len(amount_fields),
        "quantity_field_count": len(quantity_fields),
        "top_tables": sorted(non_noise_tables, key=lambda t: int(t.get("row_count") or 0), reverse=True)[:40],
        "important_time_fields": sorted(time_fields, key=lambda c: c["row_count"], reverse=True)[:120],
        "important_amount_fields": sorted(amount_fields, key=lambda c: c["row_count"], reverse=True)[:120],
        "important_quantity_fields": sorted(quantity_fields, key=lambda c: c["row_count"], reverse=True)[:120],
    }


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")


def table_html(rows: list[dict[str, Any]], keys: list[str], headers: list[str] | None = None, limit: int = 100) -> str:
    headers = headers or keys
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = []
    for row in rows[:limit]:
        body.append("<tr>" + "".join(f"<td>{html.escape(str(json_default(row.get(k, ''))))}</td>" for k in keys) + "</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def dict_bar_html(data: dict[str, Any], title: str) -> str:
    if not data:
        return ""
    max_value = max(float(v or 0) for v in data.values()) or 1
    rows = []
    for label, value in data.items():
        width = min(100, float(value or 0) / max_value * 100)
        rows.append(f"<div class='bar-row'><span>{html.escape(str(label))}</span><div class='bar-bg'><div class='bar' style='width:{width:.1f}%'></div></div><b>{value}</b></div>")
    return f"<h3>{html.escape(title)}</h3><div class='bars'>{''.join(rows)}</div>"


def render_markdown(summary: dict[str, Any], columns: list[dict[str, Any]]) -> str:
    lines = [
        "# SQL Server 数据库字段内容整理与业务分析报告",
        "",
        f"生成时间：{summary['generated_at']}",
        "",
        "## 1. 数据资产概览",
        "",
        f"- 表总数：{summary['table_count']}",
        f"- 清洗后非噪声表数：{summary['non_noise_table_count']}",
        f"- 字段总数：{summary['column_count']}",
        f"- 估算总行数：{summary['estimated_total_rows']}",
        f"- 时间字段数：{summary['time_field_count']}",
        f"- 金额字段数：{summary['amount_field_count']}",
        f"- 数量字段数：{summary['quantity_field_count']}",
        "",
        "## 2. 模块分布",
        "",
        "| 模块 | 表数量 | 估算行数 |",
        "| --- | ---: | ---: |",
    ]
    for module, count in summary["module_table_counts"].items():
        lines.append(f"| {module} | {count} | {summary['module_row_counts'].get(module, 0)} |")

    lines.extend([
        "",
        "## 3. 重点大表",
        "",
        "| 表 | 行数 | 创建时间 | 修改时间 |",
        "| --- | ---: | --- | --- |",
    ])
    for table in summary["top_tables"][:30]:
        lines.append(f"| `{table['schema_name']}.{table['table_name']}` | {table['row_count']} | {json_default(table.get('create_date'))} | {json_default(table.get('modify_date'))} |")

    lines.extend([
        "",
        "## 4. 字段类型与语义",
        "",
        "### 字段类型分类",
        "",
        "| 类型分类 | 字段数 |",
        "| --- | ---: |",
    ])
    for label, count in summary["type_counts"].items():
        lines.append(f"| {label} | {count} |")

    lines.extend(["", "### 字段语义分类", "", "| 语义 | 字段数 |", "| --- | ---: |"])
    for label, count in summary["semantic_counts"].items():
        lines.append(f"| {label} | {count} |")

    lines.extend([
        "",
        "## 5. 时间字段样例",
        "",
        "| 模块 | 表 | 字段 | 类型 | 行数 | 含义推断 |",
        "| --- | --- | --- | --- | ---: | --- |",
    ])
    for col in summary["important_time_fields"][:80]:
        lines.append(f"| {col['module']} | `{col['full_table_name']}` | `{col['column_name']}` | {col['data_type']} | {col['row_count']} | {col['semantic_category']} |")

    lines.extend([
        "",
        "## 6. 金额字段样例",
        "",
        "| 模块 | 表 | 字段 | 类型 | 精度 | 行数 | 含义推断 |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ])
    for col in summary["important_amount_fields"][:80]:
        lines.append(f"| {col['module']} | `{col['full_table_name']}` | `{col['column_name']}` | {col['data_type']} | {col['numeric_precision']},{col['numeric_scale']} | {col['row_count']} | {col['semantic_category']} |")

    lines.extend([
        "",
        "## 7. 数量字段样例",
        "",
        "| 模块 | 表 | 字段 | 类型 | 精度 | 行数 | 含义推断 |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ])
    for col in summary["important_quantity_fields"][:80]:
        lines.append(f"| {col['module']} | `{col['full_table_name']}` | `{col['column_name']}` | {col['data_type']} | {col['numeric_precision']},{col['numeric_scale']} | {col['row_count']} | {col['semantic_category']} |")

    lines.extend([
        "",
        "## 8. 岗位可做分析方向",
        "",
        "### 财务/会计",
        "",
        "- 应收应付账龄、回款/付款进度、客户/供应商往来余额分析。",
        "- 单据金额、税额、折扣、费用、成本字段联动分析。",
        "- 存货成本、出入库金额、生产材料成本、成本差异分析。",
        "- 凭证、结算、开票、核销、对账相关分析，前提是确认 AR/AP/GL 表口径。",
        "- 月度期间、会计年度、单据日期、审核日期维度下的趋势分析。",
        "",
        "### 仓库/库存",
        "",
        "- 出入库流水、库存台账、仓库库存结构、批次库存、呆滞料分析。",
        "- 材料出库与生产加工单关联追溯。",
        "- 安全库存、上下限库存、负库存、异常出入库分析。",
        "",
        "### 生产/加工",
        "",
        "- 加工单成品产量、材料领用、计划用料与实际出库差异。",
        "- BOM 用量、替代料、追加料、倒冲/领料模式分析。",
        "- 加工单状态、开工/完工日期、延期与未完工分析。",
        "",
        "### 销售/采购",
        "",
        "- 销售订单、发货、退货、客户维度收入与交付分析。",
        "- 采购订单、到货、入库、供应商交付与价格分析。",
        "",
        "### 管理层",
        "",
        "- 经营看板：收入、成本、毛利、库存、应收、应付、生产进度。",
        "- 数据可信度看板：关键字段缺失、异常日期、单据断链、基础档案缺失。",
        "",
        "## 9. 后续项目建议",
        "",
        "1. 先确定 3 个业务主题：生产用料、库存出入库、财务往来。",
        "2. 每个主题建立一张可解释宽表和一套可追溯明细。",
        "3. 用真实字段目录替代数据字典假设，数据字典仅辅助解释。",
        "4. 让客户提供现有 Excel 报表样例，用来反推口径。",
        "5. 对金额、数量、日期、状态字段建立统一指标口径表。",
    ])
    return "\n".join(lines) + "\n"


def render_html(summary: dict[str, Any], columns: list[dict[str, Any]]) -> str:
    top_tables = table_html(summary["top_tables"], ["schema_name", "table_name", "row_count", "create_date", "modify_date"], ["架构", "表", "行数", "创建时间", "修改时间"], 30)
    time_fields = table_html(summary["important_time_fields"], ["module", "full_table_name", "column_name", "data_type", "row_count", "semantic_category"], ["模块", "表", "字段", "类型", "行数", "含义推断"], 80)
    amount_fields = table_html(summary["important_amount_fields"], ["module", "full_table_name", "column_name", "data_type", "numeric_precision", "numeric_scale", "row_count", "semantic_category"], ["模块", "表", "字段", "类型", "精度", "小数", "行数", "含义推断"], 80)
    quantity_fields = table_html(summary["important_quantity_fields"], ["module", "full_table_name", "column_name", "data_type", "numeric_precision", "numeric_scale", "row_count", "semantic_category"], ["模块", "表", "字段", "类型", "精度", "小数", "行数", "含义推断"], 80)
    module_bars = dict_bar_html(summary["module_table_counts"], "模块表数量")
    type_bars = dict_bar_html(summary["type_counts"], "字段类型分类")
    semantic_bars = dict_bar_html(summary["semantic_counts"], "字段语义分类")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>数据库字段内容整理与业务分析报告</title>
<style>
:root {{ --bg:#f7f4ee; --panel:#fffdf8; --ink:#1f2933; --muted:#687385; --line:#e7ded1; --red:#b7410e; --blue:#2454a6; --green:#0f766e; }}
body {{ margin:0; background:linear-gradient(135deg,#f7f4ee,#edf5ff); color:var(--ink); font-family:"Microsoft YaHei", "Segoe UI", sans-serif; }}
main {{ max-width:1220px; margin:0 auto; padding:34px 28px 68px; }}
h1 {{ font-size:34px; margin:0 0 8px; }}
h2 {{ margin-top:38px; padding-left:12px; border-left:5px solid var(--red); }}
h3 {{ margin-top:24px; }}
.sub {{ color:var(--muted); margin-bottom:24px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:14px; }}
.card {{ background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:18px; box-shadow:0 10px 24px rgba(31,41,51,.07); }}
.card b {{ display:block; font-size:28px; color:var(--red); }}
.card span {{ color:var(--muted); }}
table {{ width:100%; border-collapse:collapse; background:var(--panel); border-radius:14px; overflow:hidden; box-shadow:0 10px 22px rgba(31,41,51,.05); margin-top:12px; }}
th, td {{ padding:9px 11px; border-bottom:1px solid var(--line); text-align:left; font-size:13px; vertical-align:top; }}
th {{ background:#efe7da; color:#2f3a45; }}
.bars {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:14px; }}
.bar-row {{ display:grid; grid-template-columns:160px 1fr 90px; gap:10px; align-items:center; margin:8px 0; font-size:13px; }}
.bar-bg {{ height:12px; background:#eadfce; border-radius:99px; overflow:hidden; }}
.bar {{ height:12px; background:linear-gradient(90deg,var(--red),#f59e0b); }}
.note {{ background:#fff7ed; border:1px solid #fed7aa; padding:14px 16px; border-radius:14px; color:#7c2d12; }}
.cols {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:18px; }}
li {{ margin:7px 0; }}
</style>
</head>
<body><main>
<h1>数据库字段内容整理与业务分析报告</h1>
<div class="sub">生成时间：{summary['generated_at']}。本报告基于 SQL Server 真实元数据，只读扫描，不依赖数据字典。</div>
<div class="grid">
  <div class="card"><b>{summary['table_count']}</b><span>表总数</span></div>
  <div class="card"><b>{summary['non_noise_table_count']}</b><span>清洗后非噪声表</span></div>
  <div class="card"><b>{summary['column_count']}</b><span>字段总数</span></div>
  <div class="card"><b>{summary['time_field_count']}</b><span>时间字段</span></div>
  <div class="card"><b>{summary['amount_field_count']}</b><span>金额字段</span></div>
  <div class="card"><b>{summary['quantity_field_count']}</b><span>数量字段</span></div>
</div>
<h2>模块与字段结构</h2>
<div class="cols"><div>{module_bars}</div><div>{type_bars}</div></div>
{semantic_bars}
<h2>重点大表</h2>{top_tables}
<h2>时间字段样例</h2>{time_fields}
<h2>金额字段样例</h2>{amount_fields}
<h2>数量字段样例</h2>{quantity_fields}
<h2>岗位可做业务分析</h2>
<div class="cols">
<div class="card"><h3>财务/会计</h3><ul><li>应收应付账龄、回款/付款进度、客户/供应商往来余额。</li><li>金额、税额、费用、折扣、成本与期间趋势。</li><li>凭证、结算、开票、核销、对账分析。</li><li>存货成本、材料成本、出入库金额、生产成本差异。</li></ul></div>
<div class="card"><h3>库存/仓库</h3><ul><li>出入库流水、库存台账、仓库结构、批次库存。</li><li>负库存、呆滞料、安全库存、上下限预警。</li><li>材料出库与生产加工单追溯。</li></ul></div>
<div class="card"><h3>生产/加工</h3><ul><li>加工单产量、计划用料、实际出库、差异分析。</li><li>BOM 用量、替代料、追加料、倒冲领料。</li><li>开工、完工、延期、未完工状态分析。</li></ul></div>
<div class="card"><h3>销售/采购</h3><ul><li>订单、发货、退货、客户收入与交付。</li><li>采购、到货、入库、供应商交付与价格。</li></ul></div>
</div>
<h2>后续规划建议</h2>
<div class="note">优先围绕生产用料、库存出入库、财务往来建立三条主题数据链路；每条链路产出一张可解释宽表、一份追溯明细和一组可视化指标。字段口径以真实数据库为准，数据字典只作为辅助说明。</div>
</main></body></html>"""


def main() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("Fetching tables", flush=True)
    tables = fetch_tables()
    print(f"Fetching columns for {len(tables)} tables", flush=True)
    columns = fetch_columns()
    enriched = enrich_columns(tables, columns)
    summary = summarize(tables, enriched)

    field_csv = SNAPSHOT_DIR / f"field_inventory_{stamp}.csv"
    summary_json = SNAPSHOT_DIR / f"field_inventory_summary_{stamp}.json"
    md_path = DOCS_DIR / "database-field-analysis-report.md"
    html_path = REPORT_DIR / f"database-field-analysis-report_{stamp}.html"

    write_csv(field_csv, enriched)
    write_json(summary_json, summary)
    md_path.write_text(render_markdown(summary, enriched), encoding="utf-8")
    html_path.write_text(render_html(summary, enriched), encoding="utf-8")

    print("Report completed.", flush=True)
    print(f"field_csv: {field_csv}", flush=True)
    print(f"summary_json: {summary_json}", flush=True)
    print(f"markdown_report: {md_path}", flush=True)
    print(f"html_report: {html_path}", flush=True)


if __name__ == "__main__":
    main()
