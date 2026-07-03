from __future__ import annotations

import pandas as pd
import streamlit as st


def topn_filter(default: int = 20, key: str = "topn") -> int:
    return int(st.slider("Top N", min_value=5, max_value=50, value=default, step=5, key=key))


def select_filter(label: str, values: list[str], key: str) -> str:
    options = ["全部"] + sorted([str(v) for v in values if pd.notna(v) and str(v).strip()])
    return st.selectbox(label, options, key=key)


def apply_equals_filter(df: pd.DataFrame, column: str, value: str) -> pd.DataFrame:
    if value == "全部" or column not in df.columns:
        return df
    return df[df[column].astype(str) == value]


def date_range_filter(df: pd.DataFrame, column: str, key: str) -> pd.DataFrame:
    if column not in df.columns or df.empty:
        return df
    parsed = pd.to_datetime(df[column], errors="coerce")
    if parsed.dropna().empty:
        return df
    min_date = parsed.min().date()
    max_date = parsed.max().date()
    selected = st.date_input("日期范围", value=(min_date, max_date), min_value=min_date, max_value=max_date, key=key)
    if not isinstance(selected, tuple) or len(selected) != 2:
        return df
    start, end = selected
    return df[(parsed.dt.date >= start) & (parsed.dt.date <= end)]
