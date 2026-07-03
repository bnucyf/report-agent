# -*- coding: utf-8 -*-
"""数据质量 handler：查 quality_issues 快照 + 按 issue_type 分类。"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_snapshot_bundle
from card_builder import build_kpi_markdown, build_topn_markdown, build_bar_chart_markdown, build_table_markdown

logger = logging.getLogger(__name__)


def handle(text: str, conversation_id: str) -> list[dict[str, str]]:
    """处理数据质量查询。"""
    messages: list[dict[str, str]] = []
    bundle = load_snapshot_bundle()
    issues = bundle.get("issues")

    if issues is None or issues.empty:
        messages.append({
            "type": "markdown",
            "title": "数据质量",
            "text": "## 数据质量\n\n暂无质量快照。请先发送\"扫描\"启动数据库扫描。",
        })
        return messages

    # KPI
    total_issues = len(issues)
    affected_tables = issues[["schema_name", "table_name"]].drop_duplicates().shape[0] if {"schema_name", "table_name"}.issubset(issues.columns) else 0
    affected_fields = issues["column_name"].nunique() if "column_name" in issues.columns else 0
    issue_sum = issues["issue_count"].sum() if "issue_count" in issues.columns else 0

    kpis = [
        ("问题记录", f"{total_issues:,}", None),
        ("涉及表", f"{affected_tables:,}", None),
        ("涉及字段", f"{affected_fields:,}", None),
        ("问题总数", f"{issue_sum:,.0f}", None),
    ]
    messages.append({
        "type": "markdown",
        "title": "质量总览",
        "text": build_kpi_markdown("数据质量总览", kpis),
    })

    # 问题类型分布
    if "issue_type" in issues.columns:
        dist = issues["issue_type"].value_counts()
        messages.append({
            "type": "markdown",
            "title": "问题类型分布",
            "text": build_bar_chart_markdown("问题类型分布", dict(dist)),
        })

    # 问题集中表 Top 15
    if {"schema_name", "table_name"}.issubset(issues.columns):
        temp = issues.copy()
        temp["表"] = temp["schema_name"].astype(str) + "." + temp["table_name"].astype(str)
        rank = temp["表"].value_counts().head(15)
        items = [(name, int(count)) for name, count in rank.items()]
        messages.append({
            "type": "markdown",
            "title": "问题集中表",
            "text": build_topn_markdown("问题集中表 Top 15", items, " 条"),
        })

    # 按用户关键词过滤
    if "空值" in text or "空字符串" in text or "字段完整性" in text:
        sub = issues[issues["issue_type"].astype(str).str.contains("空值|空字符串", na=False)]
        if not sub.empty:
            messages.append({
                "type": "markdown",
                "title": "字段完整性",
                "text": build_topn_markdown("空值/空字符串 Top 15", _to_items(sub), " 条"),
            })

    if "异常" in text or "负数" in text or "异常值" in text:
        sub = issues[issues["issue_type"].astype(str).str.contains("异常|负", na=False)]
        if not sub.empty:
            messages.append({
                "type": "markdown",
                "title": "异常值检测",
                "text": build_topn_markdown("异常日期/负数值 Top 15", _to_items(sub), " 条"),
            })

    return messages


def _to_items(df) -> list[tuple[str, int]]:
    """从 DataFrame 生成 (表名, 数量) 列表。"""
    if {"schema_name", "table_name"}.issubset(df.columns):
        temp = df.copy()
        temp["表"] = temp["schema_name"].astype(str) + "." + temp["table_name"].astype(str)
        return [(name, int(count)) for name, count in temp["表"].value_counts().head(15).items()]
    return []
