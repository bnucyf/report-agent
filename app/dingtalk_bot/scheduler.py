# -*- coding: utf-8 -*-
"""定时任务调度器：APScheduler + YAML 配置。

支持两种推送目标：
- chat_group: 推送到指定群（需 chat_id）
- single_chat: 推送到指定用户的单聊（需 user_id + robot 主动发消息）

配置文件: config/scheduler.yaml
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config" / "scheduler.yaml"

_scheduler = None


def _load_config() -> dict[str, Any]:
    """加载 YAML 配置。"""
    if not CONFIG_PATH.exists():
        logger.info("scheduler.yaml 不存在，跳过定时任务")
        return {}
    try:
        import yaml
        return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8")) or {}
    except ImportError:
        logger.warning("PyYAML 未安装，跳过定时任务配置")
        return {}
    except Exception as exc:
        logger.error("加载 scheduler.yaml 失败: %s", exc)
        return {}


def _get_conversation_id_for_group(chat_id: str) -> str:
    """群聊 chat_id 直接作为 conversation_id 使用。"""
    return chat_id


def _execute_job(action: str, target: str, chat_id: str | None, user_id: str | None, params: dict[str, Any]) -> None:
    """执行单个定时任务。"""
    logger.info("定时任务触发: action=%s, target=%s", action, target)

    # 确定 conversation_id
    conversation_id = ""
    if target == "chat_group" and chat_id:
        conversation_id = _get_conversation_id_for_group(chat_id)
    elif target == "single_chat" and user_id:
        # 单聊需要用 user_id 构造 conversation_id，或直接用 send API
        conversation_id = user_id  # 简化处理，实际场景可能需要额外转换
    else:
        logger.warning("定时任务目标无效: target=%s, chat_id=%s, user_id=%s", target, chat_id, user_id)
        return

    # 路由到对应 handler
    from dingtalk_bot.bot import dispatch

    # action → 用户文本（复用路由）
    action_to_text = {
        "send_production_usage": "生产用料",
        "send_quality_weekly": "质量",
        "send_field_inventory": "字段",
        "send_overview": "概览",
        "send_report": "报告",
        "run_full_scan": "重扫",
    }

    text = action_to_text.get(action, action)
    messages = dispatch(text, conversation_id)

    # 发送消息
    from dingtalk_bot.bot import _send_messages
    _send_messages(conversation_id, messages)

    logger.info("定时任务完成: action=%s, 发送 %d 条消息", action, len(messages))


def start_scheduler() -> None:
    """启动 APScheduler，加载 YAML 配置中的所有定时任务。"""
    global _scheduler

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.warning("APScheduler 未安装，定时任务不可用。请运行: pip install apscheduler")
        return

    config = _load_config()
    scheduler_config = config.get("scheduler", {})
    timezone = scheduler_config.get("timezone", "Asia/Shanghai")
    jobs = scheduler_config.get("jobs", [])

    if not jobs:
        logger.info("无定时任务配置")
        return

    _scheduler = BackgroundScheduler(timezone=timezone)

    for job in jobs:
        name = job.get("name", "unnamed")
        cron_expr = job.get("cron", "")
        action = job.get("action", "")
        target = job.get("target", "chat_group")
        chat_id = job.get("chat_id", "")
        user_id = job.get("user_id", "")
        params = job.get("params", {})

        if not cron_expr or not action:
            logger.warning("跳过无效任务: %s (缺少 cron 或 action)", name)
            continue

        try:
            # 解析 cron 表达式 "分 时 日 月 周"
            parts = cron_expr.split()
            if len(parts) == 5:
                trigger = CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4],
                    timezone=timezone,
                )
            else:
                logger.warning("cron 表达式格式错误 (%s): %s", name, cron_expr)
                continue

            _scheduler.add_job(
                _execute_job,
                trigger=trigger,
                args=[action, target, chat_id, user_id, params],
                id=name,
                name=name,
                replace_existing=True,
            )
            logger.info("注册定时任务: %s (cron=%s, action=%s)", name, cron_expr, action)
        except Exception as exc:
            logger.error("注册任务 %s 失败: %s", name, exc)

    _scheduler.start()
    logger.info("定时任务调度器已启动，共 %d 个任务", len(jobs))


def stop_scheduler() -> None:
    """停止调度器。"""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("定时任务调度器已停止")


def list_jobs() -> list[dict[str, str]]:
    """列出所有已注册的定时任务。"""
    if not _scheduler:
        return []
    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run": str(job.next_run_time) if job.next_run_time else "",
            "trigger": str(job.trigger),
        })
    return jobs
