from __future__ import annotations

import pandas as pd
import streamlit as st

from analysis import quality
from menus import QUALITY_MENU
from ui.components import bar_chart, insight_box, metric_cards, safe_dataframe, section


def render(bundle: dict) -> None:
    section("数据质量", "面向数据治理和报表可信度建设，按问题类型展示风险和治理建议。")
    topic = st.sidebar.selectbox("数据质量子菜单", QUALITY_MENU)
    issues = bundle.get("issues", pd.DataFrame())
    fields = bundle.get("field_inventory", pd.DataFrame())
    if topic == "质量总览":
        render_overview(issues)
    elif topic == "字段完整性":
        render_issue_subset(issues, ["空值", "空字符串"], "字段完整性")
    elif topic == "异常值检测":
        render_issue_subset(issues, ["异常", "负"], "异常值检测")
    elif topic == "单据关联风险":
        render_relation_risk(issues, fields)
    elif topic == "业务一致性":
        render_business_consistency(issues)
    else:
        render_master_quality(fields)


def render_overview(issues: pd.DataFrame) -> None:
    metric_cards(quality.kpis(issues))
    insight_box("质量总览结论", quality.insights(issues))
    bar_chart(quality.issue_distribution(issues), "问题类型分布")
    bar_chart(quality.table_rank(issues, 20), "问题集中表 Top 20")
    safe_dataframe(issues, limit=500)


def render_issue_subset(issues: pd.DataFrame, keywords: list[str], title: str) -> None:
    subset = quality.filter_issue_type(issues, keywords)
    st.subheader(title)
    metric_cards(quality.kpis(subset))
    insight_box(f"{title}结论", quality.insights(subset))
    bar_chart(quality.table_rank(subset, 20), "问题集中表")
    safe_dataframe(subset, limit=500)


def render_relation_risk(issues: pd.DataFrame, fields: pd.DataFrame) -> None:
    st.subheader("单据关联风险")
    relation_fields = pd.DataFrame()
    if not fields.empty and "semantic_category" in fields.columns:
        relation_fields = fields[fields["semantic_category"].astype(str).str.contains("单据|存货物料|客户供应商", na=False)].copy()
    metric_cards([
        ("潜在关联字段", f"{len(relation_fields):,}", None),
        ("涉及表", f"{relation_fields.get('full_table_name', pd.Series(dtype=str)).nunique():,}", None),
    ])
    insight_box("关联风险结论", ["当前先基于字段语义识别潜在关联字段，后续需要补充主外键断链 SQL。", "生产、库存、采购、销售、财务专题都依赖单据链路完整性。"])
    safe_dataframe(relation_fields, ["module", "full_table_name", "column_name", "data_type", "semantic_category", "row_count"], 800)


def render_business_consistency(issues: pd.DataFrame) -> None:
    st.subheader("业务一致性")
    insight_box("一致性检查方向", ["生产：计划用量与实际出库量是否一致。", "采购：采购到货与库存入库是否一致。", "销售：销售订单与发货出库是否一致。", "财务：发生额、核销额、余额是否一致。"])
    safe_dataframe(issues, limit=300)


def render_master_quality(fields: pd.DataFrame) -> None:
    st.subheader("主数据质量")
    if fields.empty:
        st.warning("暂无字段资产快照。")
        return
    master = fields[fields.get("module", pd.Series(dtype=str)) == "基础档案"].copy()
    metric_cards([
        ("基础档案字段", f"{len(master):,}", None),
        ("基础档案表", f"{master.get('full_table_name', pd.Series(dtype=str)).nunique():,}", None),
    ])
    insight_box("主数据质量结论", ["优先检查存货、单位、客户、供应商、仓库档案的规格、单位、编码、停用状态。", "主数据问题会直接影响生产、库存、采购、财务等所有业务分析的可解释性。"])
    safe_dataframe(master, ["full_table_name", "column_name", "data_type", "semantic_category", "row_count"], 800)
