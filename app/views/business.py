from __future__ import annotations

import pandas as pd
import streamlit as st

from analysis import executive, finance, inventory, master_data, production, purchase
from menus import BUSINESS_MENU
from ui.components import bar_chart, insight_box, metric_cards, safe_dataframe, section
from ui.filters import apply_equals_filter, date_range_filter, select_filter, topn_filter


def render(bundle: dict) -> None:
    section("业务分析", "面向经营、生产、仓库、采购、财务等岗位，按专题展示可分析内容和结论。")
    topic = st.sidebar.selectbox("业务分析子菜单", BUSINESS_MENU)
    if topic == "管理层经营总览":
        render_executive(bundle)
    elif topic == "生产加工用料":
        render_production(bundle)
    elif topic == "库存收发存":
        render_inventory(bundle)
    elif topic == "采购到货分析":
        render_purchase(bundle)
    elif topic == "财务往来分析":
        render_finance(bundle)
    else:
        render_master_data(bundle)


def render_executive(bundle: dict) -> None:
    st.subheader("管理层经营总览")
    metric_cards(executive.kpis(bundle))
    insight_box("管理层摘要", executive.insights(bundle))
    bar_chart(executive.module_series(bundle), "业务模块候选表分布")


def render_production(bundle: dict) -> None:
    df = production.prepare(bundle.get("usage", pd.DataFrame()))
    st.subheader("生产加工用料")
    if df.empty:
        st.warning("暂无生产加工用料快照。")
        return
    df = date_range_filter(df, "order_date", "production_order_date")
    product = select_filter("成品", df.get("product_name", pd.Series(dtype=str)).dropna().unique().tolist(), "production_product")
    material = select_filter("材料", df.get("material_name", pd.Series(dtype=str)).dropna().unique().tolist(), "production_material")
    df = apply_equals_filter(df, "product_name", product)
    df = apply_equals_filter(df, "material_name", material)
    topn = topn_filter(20, "production_topn")
    metric_cards(production.kpis(df))
    insight_box("生产用料结论", production.insights(df))
    bar_chart(production.material_rank(df, topn), "材料消耗排行")
    bar_chart(production.monthly_trend(df), "月度材料出库趋势")
    st.subheader("成品-材料消耗矩阵")
    safe_dataframe(production.matrix(df, min(topn, 15)), limit=200)
    st.subheader("生产用料明细")
    safe_dataframe(df, ["order_date", "manufacture_order_code", "product_name", "product_specification", "product_unit", "product_quantity", "material_name", "material_specification", "material_unit", "planned_material_quantity", "dispatched_quantity", "material_dispatch_code"], 1000)


def render_inventory(bundle: dict) -> None:
    df = inventory.inventory_tables(bundle.get("field_inventory", pd.DataFrame()))
    st.subheader("库存收发存")
    metric_cards(inventory.kpis(df))
    insight_box("库存分析结论", inventory.insights(df))
    bar_chart(inventory.field_distribution(df), "库存相关字段语义分布")
    st.subheader("库存相关重点字段")
    safe_dataframe(inventory.top_tables(df), limit=500)


def render_purchase(bundle: dict) -> None:
    df = purchase.purchase_tables(bundle.get("field_inventory", pd.DataFrame()))
    st.subheader("采购到货分析")
    metric_cards(purchase.kpis(df))
    insight_box("采购分析结论", purchase.insights(df))
    bar_chart(purchase.distribution(df), "采购相关字段语义分布")
    safe_dataframe(df, ["full_table_name", "column_name", "data_type", "semantic_category", "row_count"], 500)


def render_finance(bundle: dict) -> None:
    df = finance.finance_tables(bundle.get("field_inventory", pd.DataFrame()))
    st.subheader("财务往来分析")
    metric_cards(finance.kpis(df))
    insight_box("财务分析结论", finance.insights(df))
    bar_chart(finance.distribution(df), "财务相关字段语义分布")
    safe_dataframe(df, ["full_table_name", "column_name", "data_type", "semantic_category", "row_count"], 500)


def render_master_data(bundle: dict) -> None:
    df = master_data.master_tables(bundle.get("field_inventory", pd.DataFrame()))
    st.subheader("主数据资产分析")
    metric_cards(master_data.kpis(df))
    insight_box("主数据分析结论", master_data.insights(df))
    bar_chart(master_data.distribution(df), "基础档案字段语义分布")
    safe_dataframe(df, ["full_table_name", "column_name", "data_type", "semantic_category", "row_count"], 500)
