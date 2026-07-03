from __future__ import annotations

import streamlit as st

from data_loader import load_snapshot_bundle
from menus import MAIN_MENU
from views import business, overview, quality, reports


st.set_page_config(page_title="智能报表 Demo", layout="wide")


def render_sidebar() -> str:
    st.sidebar.title("智能报表")
    st.sidebar.caption("业务分析与数据质量并重")
    return st.sidebar.radio("一级菜单", MAIN_MENU)


def main() -> None:
    bundle = load_snapshot_bundle()
    page = render_sidebar()

    if page == "概览":
        overview.render(bundle)
    elif page == "业务分析":
        business.render(bundle)
    elif page == "数据质量":
        quality.render(bundle)
    else:
        reports.render(bundle)


if __name__ == "__main__":
    main()
