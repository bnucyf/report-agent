from __future__ import annotations

import pandas as pd

from data_loader import as_number


def prepare(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    result = df.copy()
    for col in ["dispatched_quantity", "planned_material_quantity", "requisitioned_quantity", "product_quantity"]:
        if col in result.columns:
            result[col] = as_number(result[col])
    for col in ["order_date", "material_dispatch_date"]:
        if col in result.columns:
            result[col] = pd.to_datetime(result[col], errors="coerce")
    return result


def kpis(df: pd.DataFrame) -> list[tuple[str, str, str | None]]:
    if df.empty:
        return []
    return [
        ("加工单数", f"{df.get('manufacture_order_code', pd.Series(dtype=str)).nunique():,}", None),
        ("成品数", f"{df.get('product_name', pd.Series(dtype=str)).nunique():,}", None),
        ("材料种类", f"{df.get('material_name', pd.Series(dtype=str)).nunique():,}", None),
        ("实际出库量", f"{df.get('dispatched_quantity', pd.Series(dtype=float)).sum():,.2f}", None),
    ]


def material_rank(df: pd.DataFrame, topn: int = 20) -> pd.Series:
    if df.empty or not {"material_name", "dispatched_quantity"}.issubset(df.columns):
        return pd.Series(dtype=float)
    return df.groupby("material_name", dropna=False)["dispatched_quantity"].sum().sort_values(ascending=False).head(topn)


def monthly_trend(df: pd.DataFrame) -> pd.Series:
    if df.empty or "order_date" not in df.columns:
        return pd.Series(dtype=float)
    temp = df.dropna(subset=["order_date"]).copy()
    if temp.empty:
        return pd.Series(dtype=float)
    temp["月份"] = temp["order_date"].dt.to_period("M").astype(str)
    return temp.groupby("月份")["dispatched_quantity"].sum()


def matrix(df: pd.DataFrame, topn: int = 12) -> pd.DataFrame:
    if df.empty or not {"manufacture_order_code", "product_name", "material_name", "dispatched_quantity"}.issubset(df.columns):
        return pd.DataFrame()
    top_materials = material_rank(df, topn).index.tolist()
    temp = df[df["material_name"].isin(top_materials)].copy()
    temp["加工单/成品"] = temp["manufacture_order_code"].astype(str) + " | " + temp["product_name"].fillna("未命名成品").astype(str)
    return temp.pivot_table(index="加工单/成品", columns="material_name", values="dispatched_quantity", aggfunc="sum", fill_value=0)


def insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    lines = []
    rank = material_rank(df, 3)
    if not rank.empty:
        lines.append(f"材料消耗最高的是 {rank.index[0]}，出库数量 {rank.iloc[0]:,.2f}。")
    if {"planned_material_quantity", "dispatched_quantity"}.issubset(df.columns):
        diff = (df["planned_material_quantity"] - df["dispatched_quantity"]).abs().sum()
        lines.append(f"计划用量与实际出库量的绝对差异合计约 {diff:,.2f}，建议优先核对差异较大的加工单。")
    lines.append("该专题适合向客户展示从加工单到材料出库单的业务追溯能力。")
    return lines
