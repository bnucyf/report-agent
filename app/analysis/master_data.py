from __future__ import annotations

import pandas as pd


def master_tables(field_inventory: pd.DataFrame) -> pd.DataFrame:
    if field_inventory.empty or "module" not in field_inventory.columns:
        return pd.DataFrame()
    return field_inventory[field_inventory["module"] == "基础档案"].copy()


def kpis(df: pd.DataFrame) -> list[tuple[str, str, str | None]]:
    if df.empty:
        return []
    tables = df["full_table_name"].nunique() if "full_table_name" in df.columns else 0
    inventory_fields = df["semantic_category"].astype(str).str.contains("存货物料", na=False).sum() if "semantic_category" in df.columns else 0
    partner_fields = df["semantic_category"].astype(str).str.contains("客户供应商", na=False).sum() if "semantic_category" in df.columns else 0
    status_fields = df["semantic_category"].astype(str).str.contains("状态", na=False).sum() if "semantic_category" in df.columns else 0
    return [("基础档案表", f"{tables:,}", None), ("存货字段", f"{inventory_fields:,}", None), ("往来单位字段", f"{partner_fields:,}", None), ("状态字段", f"{status_fields:,}", None)]


def distribution(df: pd.DataFrame) -> pd.Series:
    if df.empty or "semantic_category" not in df.columns:
        return pd.Series(dtype=float)
    return df["semantic_category"].value_counts().head(20)


def insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    lines = ["主数据专题应重点关注存货、单位、客户、供应商、仓库等基础档案的完整性和重复风险。"]
    if "full_table_name" in df.columns:
        top = df["full_table_name"].value_counts().index[0]
        lines.append(f"字段覆盖最多的基础档案表是 {top}，适合作为主数据治理样例。")
    return lines
