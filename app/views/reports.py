from __future__ import annotations

import streamlit as st

from data_loader import REPORT_DIR, SNAPSHOT_DIR, latest_file, latest_report
from ui.components import metric_cards, section


SNAPSHOT_PATTERNS = [
    ("表清单", "tables_*.csv"),
    ("字段清单", "columns_*.csv"),
    ("索引清单", "indexes_*.csv"),
    ("业务候选表", "business_candidates_*.csv"),
    ("质量问题", "quality_issues_*.csv"),
    ("生产加工用料", "production_material_usage_*.csv"),
    ("字段资产目录", "field_inventory_*.csv"),
]

REPORT_PATTERNS = [
    ("智能报表 HTML", "smart-report-demo_*.html"),
    ("字段分析 HTML", "database-field-analysis-report_*.html"),
]

DICT_REPORT_PATTERNS = [
    ("数据字典字段补充", "chm_field_supplement.csv"),
]


def render(bundle: dict | None = None) -> None:
    section("报告导出", "集中下载最新扫描快照、HTML 报告、字段资产分析结果以及数据字典补充说明。")
    render_report_downloads()
    render_snapshot_downloads()
    render_dict_supplement()
    render_refresh_tip()


def render_report_downloads() -> None:
    st.subheader("HTML 报告")
    latest_smart_report = latest_report()
    latest_field_report = latest_file("database-field-analysis-report_*.html", REPORT_DIR)
    metric_cards([
        ("最新智能报表", latest_smart_report.name if latest_smart_report else "暂无", None),
        ("最新字段报告", latest_field_report.name if latest_field_report else "暂无", None),
    ])

    for label, pattern in REPORT_PATTERNS:
        path = latest_file(pattern, REPORT_DIR)
        if not path:
            st.info(f"暂无{label}。")
            continue
        st.caption(f"{label}: {path.name}")
        st.download_button(
            f"下载{label}",
            path.read_bytes(),
            file_name=path.name,
            mime="text/html",
            key=f"download_report_{pattern}",
        )


def render_snapshot_downloads() -> None:
    st.subheader("数据快照")
    for label, pattern in SNAPSHOT_PATTERNS:
        path = latest_file(pattern, SNAPSHOT_DIR)
        if not path:
            st.info(f"暂无{label}快照。")
            continue
        st.caption(f"{label}: {path.name}")
        st.download_button(
            f"下载{label}",
            path.read_bytes(),
            file_name=path.name,
            mime="text/csv",
            key=f"download_snapshot_{pattern}",
        )


def render_dict_supplement() -> None:
    st.subheader("数据字典字段补充")
    path = REPORT_DIR / "chm_field_supplement.csv"
    if not path.exists():
        st.info("暂无数据字典字段补充报告。请在命令行运行 `python app/chm_parser.py` 生成。")
        return
    metric_cards([
        ("补充报告", path.name, None),
    ])
    st.caption(f"该报告将 field_inventory 快照与 TPlus160 数据字典匹配，补充表说明和字段说明。")
    st.download_button(
        "下载数据字典字段补充",
        path.read_bytes(),
        file_name=path.name,
        mime="text/csv",
        key="download_chm_supplement",
    )


def render_refresh_tip() -> None:
    st.subheader("刷新数据")
    st.info(
        "页面只读取 outputs/snapshots 和 outputs/reports 下的最新快照文件。"
        "需要刷新数据时，先在命令行运行 `python app/scan.py` 或字段资产扫描脚本，再重新打开页面。"
    )
