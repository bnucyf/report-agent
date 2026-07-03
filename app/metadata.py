from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from db import fetch_all


@dataclass(frozen=True)
class TableRef:
    schema_name: str
    table_name: str
    row_count: int

    @property
    def full_name(self) -> str:
        return f"{self.schema_name}.{self.table_name}"


def scan_tables() -> list[dict[str, Any]]:
    sql = """
    SELECT
        s.name AS schema_name,
        t.name AS table_name,
        SUM(CASE WHEN p.index_id IN (0, 1) THEN p.rows ELSE 0 END) AS row_count,
        t.create_date,
        t.modify_date
    FROM sys.tables t WITH (NOLOCK)
    INNER JOIN sys.schemas s WITH (NOLOCK) ON t.schema_id = s.schema_id
    LEFT JOIN sys.partitions p WITH (NOLOCK) ON t.object_id = p.object_id
    WHERE t.is_ms_shipped = 0
    GROUP BY s.name, t.name, t.create_date, t.modify_date
    ORDER BY row_count DESC, s.name, t.name
    """
    return fetch_all(sql)


def scan_columns(table_names: list[str] | None = None) -> list[dict[str, Any]]:
    # 注意：必须先拉全表（不传 IN 过滤），否则上万个表名会让 SQL Server 查询超时
    sql = """
    SELECT
        s.name AS schema_name,
        t.name AS table_name,
        c.name AS column_name,
        c.column_id AS ordinal_position,
        ty.name AS data_type,
        c.max_length,
        c.precision AS numeric_precision,
        c.scale AS numeric_scale,
        CASE WHEN c.is_nullable = 1 THEN 'YES' ELSE 'NO' END AS is_nullable
    FROM sys.columns c WITH (NOLOCK)
    INNER JOIN sys.tables t WITH (NOLOCK) ON c.object_id = t.object_id
    INNER JOIN sys.schemas s WITH (NOLOCK) ON t.schema_id = s.schema_id
    INNER JOIN sys.types ty WITH (NOLOCK) ON c.user_type_id = ty.user_type_id
    WHERE t.is_ms_shipped = 0
    ORDER BY s.name, t.name, c.column_id
    """
    rows = fetch_all(sql)
    if table_names:
        name_set = set(table_names)
        rows = [r for r in rows if r.get("table_name") in name_set]
    return rows


def scan_indexes(table_names: list[str] | None = None) -> list[dict[str, Any]]:
    sql = """
    SELECT
        s.name AS schema_name,
        t.name AS table_name,
        i.name AS index_name,
        i.is_primary_key,
        i.is_unique,
        c.name AS column_name,
        ic.key_ordinal
    FROM sys.indexes i WITH (NOLOCK)
    INNER JOIN sys.tables t WITH (NOLOCK) ON i.object_id = t.object_id
    INNER JOIN sys.schemas s WITH (NOLOCK) ON t.schema_id = s.schema_id
    INNER JOIN sys.index_columns ic WITH (NOLOCK) ON i.object_id = ic.object_id AND i.index_id = ic.index_id
    INNER JOIN sys.columns c WITH (NOLOCK) ON ic.object_id = c.object_id AND ic.column_id = c.column_id
    WHERE t.is_ms_shipped = 0 AND i.index_id > 0
    ORDER BY s.name, t.name, i.name, ic.key_ordinal
    """
    rows = fetch_all(sql)
    if table_names:
        name_set = set(table_names)
        rows = [r for r in rows if r.get("table_name") in name_set]
    return rows


def build_column_map(columns: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for col in columns:
        key = f"{col['schema_name']}.{col['table_name']}"
        result.setdefault(key, []).append(col)
    return result
