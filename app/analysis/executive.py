from __future__ import annotations

import pandas as pd


def kpis(bundle: dict) -> list[tuple[str, str, str | None]]:
    tables = bundle.get("tables", pd.DataFrame())
    candidates = bundle.get("candidates", pd.DataFrame())
    issues = bundle.get("issues", pd.DataFrame())
    usage = bundle.get("usage", pd.DataFrame())
    field_summary = bundle.get("field_summary", {}) or {}
    return [
        ("非噪声表", f"{field_summary.get('non_noise_table_count', len(tables)):,}", "清洗后更接近可分析业务表"),
        ("业务候选表", f"{len(candidates):,}", None),
        ("生产用料记录", f"{len(usage):,}", None),
        ("质量问题", f"{len(issues):,}", None),
    ]


def module_series(bundle: dict) -> pd.Series:
    summary = bundle.get("summary", {}) or {}
    module_counts = summary.get("module_counts") or {}
    if module_counts:
        return pd.Series(module_counts).sort_values(ascending=False)
    candidates = bundle.get("candidates", pd.DataFrame())
    if not candidates.empty and "module_label" in candidates.columns:
        return candidates["module_label"].value_counts()
    return pd.Series(dtype=float)


def insights(bundle: dict) -> list[str]:
    series = module_series(bundle)
    lines = []
    if not series.empty:
        lines.append(f"当前业务候选表最多的模块是 {series.index[0]}，共有 {int(series.iloc[0])} 张候选表。")
    issues = bundle.get("issues", pd.DataFrame())
    if not issues.empty and "issue_type" in issues.columns:
        top_issue = issues["issue_type"].value_counts().index[0]
        lines.append(f"数据质量问题中最常见的是 {top_issue}，会影响后续指标可信度。")
    lines.append("管理层页面应优先关注业务规模、异常风险和可分析主题覆盖度，而不是底层字段细节。")
    return lines
