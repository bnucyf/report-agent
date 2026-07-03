from __future__ import annotations

import pandas as pd


def purchase_tables(field_inventory: pd.DataFrame) -> pd.DataFrame:
    if field_inventory.empty or "module" not in field_inventory.columns:
        return pd.DataFrame()
    return field_inventory[field_inventory["module"] == "采购"].copy()


def kpis(df: pd.DataFrame) -> list[tuple[str, str, str | None]]:
    if df.empty:
        return []
    tables = df["full_table_name"].nunique() if "full_table_name" in df.columns else 0
    vendor_fields = df["semantic_category"].astype(str).str.contains("客户供应商", na=False).sum() if "semantic_category" in df.columns else 0
    qty_fields = df["semantic_category"].astype(str).str.contains("数量", na=False).sum() if "semantic_category" in df.columns else 0
    amount_fields = df["semantic_category"].astype(str).str.contains("金额", na=False).sum() if "semantic_category" in df.columns else 0
    return [("采购相关表", f"{tables:,}", None), ("供应商字段", f"{vendor_fields:,}", None), ("数量字段", f"{qty_fields:,}", None), ("金额字段", f"{amount_fields:,}", None)]


def distribution(df: pd.DataFrame) -> pd.Series:
    if df.empty or "semantic_category" not in df.columns:
        return pd.Series(dtype=float)
    return df["semantic_category"].value_counts().head(20)


def insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    lines = ["采购模块适合建设到货趋势、供应商集中度、物料到货排行和价格波动分析。"]
    if "full_table_name" in df.columns and not df.empty:
        table = df["full_table_name"].value_counts().index[0]
        lines.append(f"字段覆盖最多的采购相关表是 {table}，建议优先确认其到货日期、供应商和金额字段。")
    return lines
