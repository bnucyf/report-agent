from __future__ import annotations

import pandas as pd


def kpis(issues: pd.DataFrame) -> list[tuple[str, str, str | None]]:
    if issues.empty:
        return []
    table_count = issues[["schema_name", "table_name"]].drop_duplicates().shape[0] if {"schema_name", "table_name"}.issubset(issues.columns) else 0
    field_count = issues["column_name"].nunique() if "column_name" in issues.columns else 0
    issue_sum = pd.to_numeric(issues.get("issue_count", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
    return [("问题记录", f"{len(issues):,}", None), ("涉及表", f"{table_count:,}", None), ("涉及字段", f"{field_count:,}", None), ("问题数量", f"{issue_sum:,.0f}", None)]


def issue_distribution(issues: pd.DataFrame) -> pd.Series:
    if issues.empty or "issue_type" not in issues.columns:
        return pd.Series(dtype=float)
    return issues["issue_type"].value_counts()


def table_rank(issues: pd.DataFrame, topn: int = 20) -> pd.Series:
    if issues.empty or not {"schema_name", "table_name"}.issubset(issues.columns):
        return pd.Series(dtype=float)
    temp = issues.copy()
    temp["表"] = temp["schema_name"].astype(str) + "." + temp["table_name"].astype(str)
    return temp["表"].value_counts().head(topn)


def filter_issue_type(issues: pd.DataFrame, keywords: list[str]) -> pd.DataFrame:
    if issues.empty or "issue_type" not in issues.columns:
        return pd.DataFrame()
    pattern = "|".join(keywords)
    return issues[issues["issue_type"].astype(str).str.contains(pattern, case=False, na=False)].copy()


def insights(issues: pd.DataFrame) -> list[str]:
    if issues.empty:
        return []
    dist = issue_distribution(issues)
    lines = []
    if not dist.empty:
        lines.append(f"当前最多的问题类型是 {dist.index[0]}，共 {int(dist.iloc[0])} 条规则命中。")
    rank = table_rank(issues, 1)
    if not rank.empty:
        lines.append(f"问题最集中的表是 {rank.index[0]}，建议优先确认字段是否为业务允许空值。")
    lines.append("质量问题是规则命中结果，不直接等同业务错误，需要结合客户口径确认。")
    return lines
