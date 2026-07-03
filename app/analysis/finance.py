from __future__ import annotations

import pandas as pd


def finance_tables(field_inventory: pd.DataFrame) -> pd.DataFrame:
    if field_inventory.empty or "module" not in field_inventory.columns:
        return pd.DataFrame()
    return field_inventory[field_inventory["module"] == "财务/会计"].copy()


def kpis(df: pd.DataFrame) -> list[tuple[str, str, str | None]]:
    if df.empty:
        return []
    tables = df["full_table_name"].nunique() if "full_table_name" in df.columns else 0
    amount_fields = df["semantic_category"].astype(str).str.contains("金额", na=False).sum() if "semantic_category" in df.columns else 0
    partner_fields = df["semantic_category"].astype(str).str.contains("客户供应商", na=False).sum() if "semantic_category" in df.columns else 0
    date_fields = df["semantic_category"].astype(str).str.contains("日期时间", na=False).sum() if "semantic_category" in df.columns else 0
    return [("财务相关表", f"{tables:,}", None), ("金额字段", f"{amount_fields:,}", None), ("往来单位字段", f"{partner_fields:,}", None), ("日期字段", f"{date_fields:,}", None)]


def distribution(df: pd.DataFrame) -> pd.Series:
    if df.empty or "semantic_category" not in df.columns:
        return pd.Series(dtype=float)
    return df["semantic_category"].value_counts().head(20)


def insights(df: pd.DataFrame) -> list[str]:
    if df.empty:
        return []
    lines = ["财务往来模块适合优先做应收应付余额、账龄、核销进度和大额未核销风险分析。"]
    if "full_table_name" in df.columns:
        top = df["full_table_name"].value_counts().index[0]
        lines.append(f"字段覆盖最多的财务相关表是 {top}，建议优先确认其业务日期、金额方向和往来单位字段。")
    return lines
