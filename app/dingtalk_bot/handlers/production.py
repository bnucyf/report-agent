# -*- coding: utf-8 -*-
"""生产用料 handler：查 production_material_usage 快照 + 实时 SQL。"""
from __future__ import annotations

import logging
from typing import Any

from data_loader import load_snapshot_bundle
from dingtalk_bot.card_builder import build_kpi_markdown, build_topn_markdown, build_table_markdown

logger = logging.getLogger(__name__)


def handle(text: str, conversation_id: str) -> list[dict[str, str]]:
    """处理生产用料查询，返回消息列表。

    返回格式: [{"type": "markdown", "title": "...", "text": "..."}, ...]
    """
    messages: list[dict[str, str]] = []
    bundle = load_snapshot_bundle()
    usage = bundle.get("usage")

    if usage is None or usage.empty:
        messages.append({
            "type": "markdown",
            "title": "生产用料",
            "text": "## 生产用料\n\n暂无快照数据。请先发送\"扫描\"启动数据库扫描。",
        })
        return messages

    # KPI 汇总
    total_orders = usage["manufacture_order_code"].nunique() if "manufacture_order_code" in usage.columns else 0
    total_products = usage["product_name"].nunique() if "product_name" in usage.columns else 0
    total_materials = usage["material_name"].nunique() if "material_name" in usage.columns else 0
    total_rows = len(usage)

    kpis = [
        ("加工单数", f"{total_orders:,}", None),
        ("产品种类", f"{total_products:,}", None),
        ("材料种类", f"{total_materials:,}", None),
        ("明细行数", f"{total_rows:,}", None),
    ]
    messages.append({
        "type": "markdown",
        "title": "生产用料总览",
        "text": build_kpi_markdown("生产用料总览", kpis),
    })

    # Top 10 产品（按加工单数）
    if "product_name" in usage.columns:
        top_products = usage.groupby("product_name")["manufacture_order_code"].nunique().sort_values(ascending=False).head(10)
        items = [(name, int(count)) for name, count in top_products.items()]
        messages.append({
            "type": "markdown",
            "title": "产品加工排行",
            "text": build_topn_markdown("产品加工单数 Top 10", items, " 单"),
        })

    # Top 10 材料（按使用次数）
    if "material_name" in usage.columns:
        top_materials = usage["material_name"].value_counts().head(10)
        items = [(name, int(count)) for name, count in top_materials.items()]
        messages.append({
            "type": "markdown",
            "title": "材料使用排行",
            "text": build_topn_markdown("材料使用频次 Top 10", items, " 次"),
        })

    # 明细前 10 行
    if not usage.empty:
        display_cols = ["order_date", "manufacture_order_code", "product_name", "material_name", "dispatched_quantity"]
        available_cols = [c for c in display_cols if c in usage.columns]
        rows = []
        for _, row in usage.head(10).iterrows():
            rows.append([str(row.get(c, "")) for c in available_cols])
        messages.append({
            "type": "markdown",
            "title": "用料明细",
            "text": build_table_markdown("用料明细（前 10 行）", available_cols, rows, max_rows=10),
        })

    return messages
