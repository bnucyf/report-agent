from __future__ import annotations

import pandas as pd


def inventory_tables(field_inventory: pd.DataFrame) -> pd.DataFrame:
    if field_inventory.empty or "module" not in field_inventory.columns:
        return pd.DataFrame()
    return field_inventory[field_inventory["module"] == "库存/仓库"].copy()


def kpis(df: pd.DataFrame) -> list[tuple[str, str, str | None]]:
    if df.empty:
        return []
    tables = df["full_table_name"].nunique() if "full_table_name" in df.columns else 0
    amount_fields = df["semantic_category"].astype(str).str.contains("金额", na=False).sum() if "semantic_category" in df.columns else 0
    qty_fields = df["semantic_category"].astype(str).str.contains("数量", na=False).sum() if "semantic_category" in df.columns else 0
    time_fields = df["semantic_category"].astype(str).str.contains("日期时间", na=False).sum() if "semantic_category" in df.columns else 0
    return [("库存相关表", f"{tables:,}", None), ("数量字段", f"{qty_fields:,}", None), ("金额字段", f"{amount_fields:,}", None), ("时间字段", f"{time_fields:,}", None)]


def field_distribution(df: pd.DataFrame) -> pd.Series:
    if df.empty or "semantic_category" not in df.columns:
        return pd.Series(dtype=float)
    return df["semantic_category"].value_counts().head(20)


def top_tables(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    cols = ["full_table_name", "row_count", "column_name", "semantic_category"]
    view = df[[col for col in cols if col in df.columns]].copy()
    if "row_count" in view.columns:
        view = view.sort_values("row_count", ascending=False)
    return view


def insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    tables = df["full_table_name"].nunique() if "full_table_name" in df.columns else 0
    lines = [f"库存/仓库模块已识别 {tables} 张相关表，适合优先建设收发存和出入库流水分析。"]
    if "full_table_name" in df.columns and "row_count" in df.columns:
        top = df.sort_values("row_count", ascending=False).iloc[0]
        lines.append(f"记录规模最大的库存相关表是 {top['full_table_name']}，应优先确认其业务口径。")
    lines.append("后续需要补充仓库、物料、出入库类型筛选，形成按日/月的收发存趋势。")
    return lines
