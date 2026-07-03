# -*- coding: utf-8 -*-
"""字段资产 handler：查 field_inventory 快照。"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_snapshot_bundle
from card_builder import build_kpi_markdown, build_topn_markdown, build_bar_chart_markdown

logger = logging.getLogger(__name__)


def handle(text: str, conversation_id: str) -> list[dict[str, str]]:
    """处理字段资产查询。"""
    messages: list[dict[str, str]] = []
    bundle = load_snapshot_bundle()
    fields = bundle.get("field_inventory")
    summary = bundle.get("field_summary", {})

    if fields is None or fields.empty:
        messages.append({
            "type": "markdown",
            "title": "字段资产",
            "text": "## 字段资产\n\n暂无字段资产快照。请先发送\"扫描\"启动数据库扫描。",
        })
        return messages

    # KPI（优先从 summary 拿，兜底从 DataFrame 算）
    table_count = summary.get("table_count", fields.get("full_table_name", fields).nunique() if hasattr(fields, "get") else 0)
    col_count = summary.get("column_count", len(fields))
    time_fields = summary.get("time_field_count", 0)
    amount_fields = summary.get("amount_field_count", 0)
    quantity_fields = summary.get("quantity_field_count", 0)

    kpis = [
        ("表总数", f"{table_count:,}", None),
        ("字段总数", f"{col_count:,}", None),
        ("时间字段", f"{time_fields:,}", None),
        ("金额字段", f"{amount_fields:,}", None),
        ("数量字段", f"{quantity_fields:,}", None),
    ]
    messages.append({
        "type": "markdown",
        "title": "字段资产总览",
        "text": build_kpi_markdown("字段资产总览", kpis),
    })

    # 模块分布
    module_counts = summary.get("module_table_counts", {})
    if not module_counts and "module" in fields.columns:
        module_counts = dict(fields["module"].value_counts())
    if module_counts:
        messages.append({
            "type": "markdown",
            "title": "模块分布",
            "text": build_bar_chart_markdown("模块表数量分布", module_counts),
        })

    # 字段类型分布
    type_counts = summary.get("type_counts", {})
    if not type_counts and "type_category" in fields.columns:
        type_counts = dict(fields["type_category"].value_counts())
    if type_counts:
        messages.append({
            "type": "markdown",
            "title": "字段类型",
            "text": build_bar_chart_markdown("字段类型分类", type_counts),
        })

    # Top 15 大表
    top_tables = summary.get("top_tables", [])
    if top_tables:
        items = [(f"{t.get('schema_name','')}.{t.get('table_name','')}", int(t.get("row_count", 0))) for t in top_tables[:15]]
        messages.append({
            "type": "markdown",
            "title": "大表排行",
            "text": build_topn_markdown("重点大表 Top 15", items, " 行"),
        })

    return messages
