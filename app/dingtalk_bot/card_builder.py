# -*- coding: utf-8 -*-
"""模板卡片构建器：构造钉钉 Markdown + 模板卡片 JSON。

钉钉 Markdown 不支持表格语法，复杂多列数据用以下策略：
1. KPI 指标 → 纯 Markdown 列表
2. Top N 排行 → Markdown 列表（每行一条）
3. 明细长表 → 生成 HTML 文件链接 + ActionCard 跳转
4. 可视化图表 → 简单字符柱状图嵌入 Markdown
"""
from __future__ import annotations

from typing import Any


def build_kpi_markdown(title: str, kpis: list[tuple[str, str, str | None]]) -> str:
    """构建 KPI 指标 Markdown。"""
    lines = [f"## {title}\n"]
    for label, value, hint in kpis:
        line = f"- **{label}**：{value}"
        if hint:
            line += f" _{hint}_"
        lines.append(line)
    return "\n".join(lines)


def build_topn_markdown(title: str, items: list[tuple[str, Any]], unit: str = "") -> str:
    """构建 Top N 排行 Markdown。

    items: [(名称, 数值), ...] 按 value 降序。
    """
    if not items:
        return f"## {title}\n\n暂无数据。"
    lines = [f"## {title}\n"]
    for i, (name, value) in enumerate(items[:20], 1):
        lines.append(f"{i}. {name}：**{value:,}{unit}**")
    return "\n".join(lines)


def build_bar_chart_markdown(title: str, data: dict[str, int | float], max_bars: int = 15) -> str:
    """构建简易字符柱状图 Markdown。"""
    if not data:
        return f"## {title}\n\n暂无数据。"
    lines = [f"## {title}\n"]
    items = sorted(data.items(), key=lambda x: x[1], reverse=True)[:max_bars]
    max_val = max(v for _, v in items) or 1
    for name, value in items:
        bar_len = int(float(value) / max_val * 20)
        bar = "█" * max(bar_len, 1)
        lines.append(f"`{name[:12]:>12}` {bar} {value:,}")
    return "\n".join(lines)


def build_table_markdown(title: str, headers: list[str], rows: list[list[Any]], max_rows: int = 15) -> str:
    """构建表格 Markdown（钉钉不支持 | 语法，用列表模拟）。"""
    if not rows:
        return f"## {title}\n\n暂无数据。"
    lines = [f"## {title}\n"]
    for row in rows[:max_rows]:
        parts = [f"**{h}**: {v}" for h, v in zip(headers, row)]
        lines.append("- " + " | ".join(parts))
    lines.append(f"\n_共 {len(rows)} 行，此处展示前 {min(len(rows), max_rows)} 行。完整明细请下载报告。_")
    return "\n".join(lines)


def build_scan_progress_markdown(state: dict[str, Any]) -> str:
    """构建扫描进度 Markdown。"""
    done = state.get("done_count", 0)
    total = state.get("candidate_tables", 0)
    pct = state.get("progress_pct", 0)
    failed = state.get("failed_count", 0)
    current = state.get("current_table", "")
    is_complete = state.get("is_complete", False)
    is_paused = state.get("is_paused", False)

    if is_complete:
        status = "✅ 扫描完成"
    elif is_paused:
        status = "⏸ 已暂停"
    else:
        status = "🔄 扫描中"

    lines = [
        f"## 数据库扫描状态\n",
        f"- **状态**：{status}",
        f"- **进度**：{done}/{total} ({pct}%)",
        f"- **失败**：{failed}",
    ]
    if current and not is_complete:
        lines.append(f"- **当前表**：`{current}`")
    if state.get("database_name"):
        lines.append(f"- **数据库**：{state['database_name']}")
    if state.get("analyzed_at"):
        lines.append(f"- **更新时间**：{state['analyzed_at']}")
    return "\n".join(lines)
