# -*- coding: utf-8 -*-
"""扫描 handler：启动扫描 + 查询扫描进度。"""
from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

from scan_state import load_state, state_summary
from dingtalk_bot.card_builder import build_scan_progress_markdown, build_kpi_markdown

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = ROOT_DIR / "app"
SCAN_SCRIPT = APP_DIR / "scan.py"


def handle(text: str, conversation_id: str) -> list[dict[str, str]]:
    """处理扫描相关指令。"""
    messages: list[dict[str, str]] = []

    if "重扫" in text or "全量" in text or "reset" in text.lower():
        return _start_scan(conversation_id, reset=True)
    elif "暂停" in text:
        return _pause_scan(conversation_id)
    elif "进度" in text or "扫描" in text:
        return _query_progress(conversation_id)
    else:
        return _start_scan(conversation_id, reset=False)


def _start_scan(conversation_id: str, reset: bool = False) -> list[dict[str, str]]:
    """启动扫描子进程。"""
    messages: list[dict[str, str]] = []

    # 检查是否已有扫描在跑
    state = load_state()
    if state.candidate_tables > 0 and not state.is_complete and not state.is_paused:
        messages.append({
            "type": "markdown",
            "title": "扫描进行中",
            "text": build_scan_progress_markdown(state_summary()),
        })
        messages.append({
            "type": "markdown",
            "title": "提示",
            "text": "扫描正在进行中，请等待完成。发送\"进度\"查看最新状态。",
        })
        return messages

    # 启动子进程
    try:
        python_exe = sys.executable or "python"
        args = [python_exe, str(SCAN_SCRIPT)]
        if reset:
            args.append("--reset")

        log_path = ROOT_DIR / "outputs" / "scan.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_fd = open(log_path, "a", encoding="utf-8")
        proc = subprocess.Popen(
            args,
            stdout=log_fd,
            stderr=log_fd,
            cwd=str(APP_DIR),
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        logger.info("扫描子进程已启动: PID=%s, args=%s", proc.pid, args)

        messages.append({
            "type": "markdown",
            "title": "扫描已启动",
            "text": f"## 数据库扫描已启动\n\n"
                    f"- **PID**：{proc.pid}\n"
                    f"- **模式**：{'全量重扫' if reset else '断点续扫'}\n"
                    f"- **日志**：`outputs/scan.log`\n\n"
                    f"> 扫描约需 10-60 分钟，完成后将自动生成所有报表。\n"
                    f"> 发送\"进度\"可随时查看扫描状态。",
        })
    except Exception as exc:
        logger.error("启动扫描失败: %s", exc)
        messages.append({
            "type": "markdown",
            "title": "扫描启动失败",
            "text": f"## 启动失败\n\n```\n{exc}\n```\n\n请检查 `outputs/scan.log` 获取详细信息。",
        })

    return messages


def _pause_scan(conversation_id: str) -> list[dict[str, str]]:
    """暂停扫描。"""
    from scan_state import write_control
    try:
        write_control("pause")
        return [{
            "type": "markdown",
            "title": "暂停信号已发送",
            "text": "## 扫描暂停\n\n暂停信号已写入，扫描进程将在当前表完成后暂停。\n\n发送\"扫描\"可继续。",
        }]
    except Exception as exc:
        return [{
            "type": "markdown",
            "title": "暂停失败",
            "text": f"## 暂停失败\n\n```\n{exc}\n```",
        }]


def _query_progress(conversation_id: str) -> list[dict[str, str]]:
    """查询扫描进度。"""
    summary = state_summary()
    if not summary.get("has_state"):
        return [{
            "type": "markdown",
            "title": "无扫描记录",
            "text": "## 暂无扫描记录\n\n发送\"扫描\"启动数据库扫描。",
        }]

    messages: list[dict[str, str]] = []
    messages.append({
        "type": "markdown",
        "title": "扫描进度",
        "text": build_scan_progress_markdown(summary),
    })

    if summary.get("is_complete"):
        messages.append({
            "type": "markdown",
            "title": "扫描完成",
            "text": "## ✅ 扫描已完成\n\n所有报表已自动生成。\n\n"
                    "- 发送\"生产用料\"查看业务分析\n"
                    "- 发送\"质量\"查看数据质量\n"
                    "- 发送\"字段\"查看字段资产\n"
                    "- 发送\"报告\"下载完整报告",
        })

    return messages
