from __future__ import annotations

from typing import Iterable

import pandas as pd
import streamlit as st


def format_number(value: float | int, digits: int = 0) -> str:
    try:
        if digits <= 0:
            return f"{float(value):,.0f}"
        return f"{float(value):,.{digits}f}"
    except Exception:
        return "0"


def metric_cards(items: Iterable[tuple[str, object, str | None]]) -> None:
    items = list(items)
    if not items:
        return
    cols = st.columns(min(len(items), 4))
    for idx, (label, value, help_text) in enumerate(items):
        cols[idx % len(cols)].metric(label, value, help=help_text)


def insight_box(title: str, lines: list[str]) -> None:
    st.markdown(f"#### {title}")
    if not lines:
        st.info("暂无足够数据生成结论。")
        return
    st.info("\n".join(f"- {line}" for line in lines))


def safe_dataframe(df: pd.DataFrame, columns: list[str] | None = None, limit: int = 500) -> None:
    if df.empty:
        st.warning("暂无数据。")
        return
    view = df
    if columns:
        view = df[[col for col in columns if col in df.columns]]
    st.dataframe(view.head(limit), use_container_width=True)


def bar_chart(series: pd.Series, title: str) -> None:
    st.subheader(title)
    if series.empty:
        st.warning("暂无可绘制数据。")
        return
    st.bar_chart(series)


def section(title: str, caption: str | None = None) -> None:
    st.title(title)
    if caption:
        st.caption(caption)
