from __future__ import annotations

from typing import Any

from db import fetch_all, qualified_name, quote_name


TEXT_TYPES = {"char", "nchar", "varchar", "nvarchar", "text", "ntext"}
DATE_TYPES = {"date", "datetime", "datetime2", "smalldatetime", "time"}
NUMERIC_TYPES = {"int", "bigint", "smallint", "tinyint", "decimal", "numeric", "float", "real", "money", "smallmoney"}


def profile_table(schema_name: str, table_name: str, columns: list[dict[str, Any]], sample_rows: int = 1000) -> list[dict[str, Any]]:
    if not columns:
        return []

    qname = qualified_name(schema_name, table_name)
    select_parts: list[str] = []
    for col in columns:
        name = col["column_name"]
        qcol = quote_name(name)
        alias_prefix = name.replace("]", "_")
        dtype = str(col["data_type"]).lower()
        select_parts.append(f"SUM(CASE WHEN {qcol} IS NULL THEN 1 ELSE 0 END) AS {quote_name(alias_prefix + '__nulls')}")
        if dtype in TEXT_TYPES:
            select_parts.append(f"SUM(CASE WHEN LTRIM(RTRIM(CAST({qcol} AS NVARCHAR(MAX)))) = '' THEN 1 ELSE 0 END) AS {quote_name(alias_prefix + '__blanks')}")
        elif dtype in DATE_TYPES:
            select_parts.append(f"SUM(CASE WHEN {qcol} < '2000-01-01' OR {qcol} > DATEADD(year, 2, GETDATE()) THEN 1 ELSE 0 END) AS {quote_name(alias_prefix + '__date_outliers')}")
        elif dtype in NUMERIC_TYPES:
            select_parts.append(f"SUM(CASE WHEN {qcol} < 0 THEN 1 ELSE 0 END) AS {quote_name(alias_prefix + '__negative_values')}")

    sql = f"""
    SELECT COUNT(1) AS sampled_rows, {", ".join(select_parts)}
    FROM (SELECT TOP ({int(sample_rows)}) * FROM {qname} WITH (NOLOCK)) sampled
    """
    try:
        rows = fetch_all(sql)
    except Exception as exc:
        return [
            {
                "schema_name": schema_name,
                "table_name": table_name,
                "column_name": "*",
                "issue_type": "profile_failed",
                "issue_count": 1,
                "sampled_rows": 0,
                "issue_rate": 1.0,
                "detail": str(exc)[:300],
            }
        ]

    if not rows:
        return []
    row = rows[0]
    sampled_rows = int(row.get("sampled_rows") or 0)
    issues: list[dict[str, Any]] = []
    if sampled_rows == 0:
        return issues

    for col in columns:
        name = col["column_name"]
        for suffix, issue_type in [
            ("__nulls", "空值"),
            ("__blanks", "空字符串"),
            ("__date_outliers", "异常日期"),
            ("__negative_values", "负数值"),
        ]:
            key = name + suffix
            count = int(row.get(key) or 0)
            if count <= 0:
                continue
            issues.append(
                {
                    "schema_name": schema_name,
                    "table_name": table_name,
                    "column_name": name,
                    "issue_type": issue_type,
                    "issue_count": count,
                    "sampled_rows": sampled_rows,
                    "issue_rate": round(count / sampled_rows, 4),
                    "detail": "基于抽样统计，需结合业务口径确认是否为真实问题。",
                }
            )
    return sorted(issues, key=lambda item: item["issue_rate"], reverse=True)


def profile_candidate_tables(candidates: list[dict[str, Any]], column_map: dict[str, list[dict[str, Any]]], sample_rows: int = 1000, limit: int = 20) -> list[dict[str, Any]]:
    all_issues: list[dict[str, Any]] = []
    for candidate in candidates[:limit]:
        key = candidate["full_name"]
        cols = column_map.get(key, [])[:80]
        all_issues.extend(profile_table(candidate["schema_name"], candidate["table_name"], cols, sample_rows))
    return sorted(all_issues, key=lambda item: (item["issue_rate"], item["issue_count"]), reverse=True)
