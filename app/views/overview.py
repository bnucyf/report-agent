from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from analysis import executive
from db import ROOT_DIR
from scan_state import (
    CONTROL_PATH,
    STATE_PATH,
    load_control,
    load_state,
    progress_rows,
    state_summary,
    write_control,
)
from ui.components import bar_chart, insight_box, metric_cards, safe_dataframe, section

PYTHON_EXE = Path(r"C:/Users/22411/.workbuddy/binaries/python/envs/default/Scripts/python.exe")
SCAN_SCRIPT = ROOT_DIR / "app" / "scan.py"


def _run_subprocess(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR / "app")
    return subprocess.run(
        [str(PYTHON_EXE), str(SCAN_SCRIPT), *args],
        cwd=str(ROOT_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def render(bundle: dict) -> None:
    section("智能报表概览", "基于真实 SQL Server 只读扫描快照，展示当前数据资产、业务主题和主要风险。")

    render_analysis_control()

    metric_cards(executive.kpis(bundle))
    insight_box("概览结论", executive.insights(bundle))

    st.subheader("业务模块分布")
    bar_chart(executive.module_series(bundle), "")

    st.subheader("数据库大表概览")
    tables = bundle.get("tables", pd.DataFrame())
    safe_dataframe(tables, ["schema_name", "table_name", "row_count", "create_date", "modify_date"], 80)


def render_analysis_control() -> None:
    st.subheader("数据扫描控制")
    state = load_state()
    summary = state_summary()
    control = load_control()

    # 状态提示
    pct = summary.get("progress_pct", 0.0)
    cand = summary.get("candidate_tables", 0)
    done = summary.get("done_count", 0)
    failed = summary.get("failed_count", 0)
    pending = summary.get("pending_count", 0)

    if state.is_complete and cand > 0 and pending == 0:
        st.success(
            f"✅ 所有非噪声业务表已完成分析（{done}/{cand}，失败 {failed}，进度 {pct}%）。无更新。"
        )
    elif state.is_paused:
        st.warning(
            f"⏸ 已暂停：当前完成 {done}/{cand}（失败 {failed}），进度 {pct}%。"
            "点击下方“继续扫描”会从断点继续。"
        )
    elif summary.get("has_state") and done + failed > 0:
        st.info(
            f"🔄 扫描进行中或可继续：完成 {done}/{cand}（失败 {failed}），进度 {pct}%。"
            "支持随时暂停/继续。"
        )
    else:
        st.info("尚未开始分析。点击下方“开始扫描”将逐表分析所有非噪声业务表。")

    # 当前正在扫描的表
    if state.current_table:
        st.caption(f"当前正在扫描：`{state.current_table}`")

    # 三个按钮：开始/继续  /  暂停  /  全部重新扫描
    col1, col2, col3 = st.columns(3)
    with col1:
        start_label = "🚀 开始扫描" if done == 0 else f"▶ 继续扫描（剩 {pending} 张）"
        if st.button(start_label, key="start_scan", use_container_width=True):
            _start_scan()

    with col2:
        pause_disabled = not (not state.is_complete and done + failed < cand) or control.action == "pause"
        if st.button("⏸ 暂停扫描", key="pause_scan", disabled=pause_disabled, use_container_width=True):
            _pause_scan()

    with col3:
        if st.button("🔁 全部重新扫描", key="reset_scan", use_container_width=True):
            _reset_scan()

    # 状态详情：逐表进度
    with st.expander(f"逐表扫描进度（已完成 {done}，失败 {failed}，待扫描 {pending}）", expanded=False):
        rows = progress_rows()
        if not rows:
            st.caption("暂无逐表进度。请点击“开始扫描”。")
        else:
            df = pd.DataFrame(rows)
            # 状态翻译
            status_map = {
                "done": "✅ 已完成",
                "scanning": "⏳ 扫描中",
                "failed": "❌ 失败",
                "pending": "• 待扫描",
                "skipped": "⏭ 跳过",
            }
            df["状态"] = df["status"].map(lambda s: status_map.get(s, s))
            display_cols = ["table", "状态", "started_at", "finished_at", "issue_count", "column_count", "error"]
            df = df[display_cols].rename(columns={
                "table": "表",
                "started_at": "开始时间",
                "finished_at": "结束时间",
                "issue_count": "问题数",
                "column_count": "字段数",
                "error": "错误",
            })
            st.dataframe(df, use_container_width=True, hide_index=True, height=320)

    # 自动刷新：扫描中时每 3 秒拉一次新状态
    if not state.is_complete and (state.current_table or done + failed > 0) and not state.is_paused:
        st.caption("页面将在 3 秒后自动刷新以显示最新进度…")
        time.sleep(3)
        st.rerun()


def _start_scan() -> None:
    if not PYTHON_EXE.exists():
        st.error(f"未找到 Python 解释器：{PYTHON_EXE}")
        return
    if not SCAN_SCRIPT.exists():
        st.error(f"未找到扫描脚本：{SCAN_SCRIPT}")
        return
    # 异步启动（不被阻塞），使用 Popen 让 UI 立即返回
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR / "app")
    log_path = ROOT_DIR / "outputs" / "scan.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fh = log_path.open("a", encoding="utf-8")
    # 写一行启动标记，便于排查"按钮点击了但子进程没起"
    log_fh.write(f"\n--- [scan] launch at {time.strftime('%Y-%m-%d %H:%M:%S')} pid=?\n")
    log_fh.flush()
    proc = subprocess.Popen(
        [str(PYTHON_EXE), str(SCAN_SCRIPT)],
        cwd=str(ROOT_DIR),
        env=env,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_fh.write(f"--- [scan] Popen started, pid={proc.pid}\n")
    log_fh.flush()
    # 等待最多 10 秒，检查子进程是否进入主循环（scan_state.json 中 current_table 有值）
    startup_ok = False
    state_path = ROOT_DIR / "outputs" / "scan_state.json"
    for _ in range(20):
        time.sleep(0.5)
        if proc.poll() is not None:
            break  # 子进程已退出
        if state_path.exists():
            try:
                import json as _json
                cur = _json.loads(state_path.read_text(encoding="utf-8")).get("current_table", "")
                if cur:
                    startup_ok = True
                    break
            except Exception:
                pass
    if proc.poll() is not None and proc.returncode != 0:
        st.error(
            f"扫描子进程启动后立即退出（returncode={proc.returncode}）。"
            f"请查看 outputs/scan.log 末尾的错误堆栈。"
        )
    elif startup_ok:
        st.success(f"扫描已启动（pid={proc.pid}），3 秒后自动刷新查看进度。日志见 outputs/scan.log。")
    else:
        st.warning(
            f"扫描子进程已启动（pid={proc.pid}），但 10 秒内未进入主循环。"
            f"通常首次扫描需 60-120 秒拉取元数据（13K+ 张表），请耐心等待或查看 outputs/scan.log。"
        )
    time.sleep(1)
    st.rerun()


def _pause_scan() -> None:
    write_control("pause")
    st.warning("已写入暂停信号，扫描将在当前表结束后停止。")


def _reset_scan() -> None:
    """全部重新扫描：清空历史进度 + 立即启动新扫描。"""
    if STATE_PATH.exists():
        STATE_PATH.unlink()
    if CONTROL_PATH.exists():
        CONTROL_PATH.unlink()
    prog = ROOT_DIR / "outputs" / "scan_progress.json"
    if prog.exists():
        prog.unlink()
    st.success("历史扫描记录已清空。正在启动全量重新扫描…")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR / "app")
    log_path = ROOT_DIR / "outputs" / "scan.log"
    log_fh = log_path.open("a", encoding="utf-8")
    log_fh.write(f"\n--- [scan] reset+launch at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    log_fh.flush()
    proc = subprocess.Popen(
        [str(PYTHON_EXE), str(SCAN_SCRIPT), "--reset"],
        cwd=str(ROOT_DIR),
        env=env,
        stdout=log_fh,
        stderr=subprocess.STDOUT,
        text=True,
    )
    log_fh.write(f"--- [scan] reset Popen started, pid={proc.pid}\n")
    log_fh.flush()
    time.sleep(1)
    st.rerun()
