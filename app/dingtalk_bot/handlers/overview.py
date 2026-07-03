# -*- coding: utf-8 -*-
"""概览 handler：全局 KPI 汇总。"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_snapshot_bundle
from card_builder import build_kpi_markdown, build_bar_chart_markdown, build_topn_markdown
from scan_state import state_summary

logger = logging.getLogger(__name__)


def handle(text: str, conversation_id: str) -> list[dict[str, str]]:
    """处理概览查询。"""
    messages: list[dict[str, str]] = []
    bundle = load_snapshot_bundle()

    tables = bundle.get("tables")
    candidates = bundle.get("candidates")
    issues = bundle.get("issues")
    usage = bundle.get("usage")
    fields = bundle.get("field_inventory")

    # 核心指标
    table_count = len(tables) if tables is not None else 0
    candidate_count = len(candidates) if candidates is not None else 0
    issue_count = len(issues) if issues is not None else 0
    usage_count = len(usage) if usage is not None else 0
    field_count = len(fields) if fields is not None else 0

    kpis = [
        ("数据库表", f"{table_count:,}", None),
        ("业务候选表", f"{candidate_count:,}", None),
        ("质量问题", f"{issue_count:,}", None),
        ("生产用料行", f"{usage_count:,}", None),
        ("字段总数", f"{field_count:,}", None),
    ]
    messages.append({
        "type": "markdown",
        "title": "数据总览",
        "text": build_kpi_markdown("数据库总览", kpis),
    })

    # 扫描状态
    scan = state_summary()
    if scan.get("has_state"):
        from card_builder import build_scan_progress_markdown
        messages.append({
            "type": "markdown",
            "title": "扫描状态",
            "text": build_scan_progress_markdown(scan),
        })

    # 模块分布（从 candidates）
    if candidates is not None and not candidates.empty:
        if "module" in candidates.columns:
            module_counts = dict(candidates["module"].value_counts().head(10))
            messages.append({
                "type": "markdown",
                "title": "模块分布",
                "text": build_bar_chart_markdown("业务表模块分布", module_counts),
            })

    # Top 10 大表（从 tables）
    if tables is not None and not tables.empty:
        if "row_count" in tables.columns and "table_name" in tables.columns:
            top = tables.nlargest(10, "row_count")
            items = [(str(row.get("table_name", "")), int(row.get("row_count", 0))) for _, row in top.iterrows()]
            messages.append({
                "type": "markdown",
                "title": "大表排行",
                "text": build_topn_markdown("数据量 Top 10 表", items, " 行"),
            })

    return messages
