# -*- coding: utf-8 -*-
"""钉钉机器人 Stream 入口：注册 ChatbotHandler + CardCallbackHandler。

启动方式:
    cd app
    python -m dingtalk_bot.bot

或:
    cd app/dingtalk_bot
    python bot.py

环境变量（从 .env 读取）:
    DINGTALK_CLIENT_ID       — 应用 AppKey
    DINGTALK_CLIENT_SECRET   — 应用 AppSecret
    DINGTALK_CORP_ID         — 企业 CorpId
    DINGTALK_AGENT_ID        — 应用 AgentId
    BOT_ADMIN_USER_ID        — 管理员 UserId（首次启动推送使用说明）
"""
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

# 确保 app/ 目录在 sys.path 中
_APP_DIR = str(Path(__file__).resolve().parents[1])
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

from dotenv import load_dotenv

# 加载 .env
ROOT_DIR = Path(__file__).resolve().parents[2]
_env_path = ROOT_DIR / ".env"
if _env_path.exists():
    load_dotenv(str(_env_path))

from dingtalk_bot import credential
from dingtalk_bot.router import match_intent, get_menu_text
from dingtalk_bot.handlers import production, quality, field_asset, scan, overview, report, help as help_handler

logger = logging.getLogger(__name__)

# ---------- 日志配置 ----------
LOG_DIR = ROOT_DIR / "outputs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOG_DIR / "bot.log"), encoding="utf-8"),
    ],
)


# ---------- handler 路由表 ----------

_HANDLER_MAP: dict[str, Any] = {
    "production": production,
    "quality": quality,
    "field_asset": field_asset,
    "scan": scan,
    "overview": overview,
    "report": report,
    "help": help_handler,
}


def dispatch(text: str, conversation_id: str) -> list[dict[str, str]]:
    """根据用户文本路由到对应 handler，返回消息列表。"""
    intent = match_intent(text)
    handler = _HANDLER_MAP.get(intent)
    if handler is None:
        return [{
            "type": "markdown",
            "title": "未识别",
            "text": get_menu_text(),
        }]
    try:
        return handler.handle(text, conversation_id)
    except Exception as exc:
        logger.error("handler %s 执行失败: %s", intent, exc, exc_info=True)
        return [{
            "type": "markdown",
            "title": "处理失败",
            "text": f"## 处理失败\n\n```\n{exc}\n```\n\n请重试或联系管理员。",
        }]


# ---------- Stream 回调 ----------

def _send_messages(conversation_id: str, messages: list[dict[str, str]]) -> None:
    """把 handler 返回的消息列表逐条发送。"""
    for msg in messages:
        msg_type = msg.get("type", "markdown")
        title = msg.get("title", "通知")
        text = msg.get("text", "")
        try:
            if msg_type == "markdown":
                credential.send_markdown_to_chatbot(conversation_id, title, text)
            elif msg_type == "action_card":
                credential.send_action_card(
                    conversation_id, title, text,
                    msg.get("btn_title", "查看详情"),
                    msg.get("btn_url", ""),
                )
            time.sleep(0.3)  # 避免消息发送过快被限流
        except Exception as exc:
            logger.error("发送消息失败 (type=%s, title=%s): %s", msg_type, title, exc)


def _on_chatbot_message(message: Any) -> None:
    """Stream 模式收到用户消息时的回调。"""
    try:
        # dingtalk-stream SDK 的消息结构
        incoming = message.data if hasattr(message, "data") else message
        text = ""
        conversation_id = ""
        sender_id = ""
        chat_type = ""

        if isinstance(incoming, dict):
            text = incoming.get("text", {}).get("content", "").strip()
            conversation_id = incoming.get("conversationId", "")
            sender_id = incoming.get("senderId", "")
            chat_type = incoming.get("conversationType", "")  # 1=单聊, 2=群聊
            # 群聊中 @ 机器人时 text 前面可能有 @机器人名，清理
            if chat_type == "2" and "@" in text:
                # 去掉 @机器人名 部分
                at_parts = text.split(" ", 1)
                if len(at_parts) > 1 and at_parts[0].startswith("@"):
                    text = at_parts[1].strip()
                else:
                    text = text.replace("@", "").strip()

        logger.info("收到消息: sender=%s, conv=%s, type=%s, text=%s",
                     sender_id, conversation_id, chat_type, text[:100])

        if not text:
            text = "帮助"

        messages = dispatch(text, conversation_id)
        _send_messages(conversation_id, messages)

        # SDK 需要 reply 或者不需要（取决于 SDK 版本）
        if hasattr(message, "reply"):
            try:
                message.reply("已处理")
            except Exception:
                pass

    except Exception as exc:
        logger.error("处理用户消息失败: %s", exc, exc_info=True)


def _on_card_callback(callback: Any) -> None:
    """互动卡片按钮回调。"""
    try:
        incoming = callback.data if hasattr(callback, "data") else callback
        if isinstance(incoming, dict):
            action = incoming.get("action", "")
            out_track_id = incoming.get("outTrackId", "")
            conversation_id = incoming.get("conversationId", "")
            logger.info("卡片回调: action=%s, out_track_id=%s", action, out_track_id)

            # 根据 action 重新查询并更新卡片
            # TODO: 实现卡片翻页/钻取逻辑
    except Exception as exc:
        logger.error("处理卡片回调失败: %s", exc, exc_info=True)


# ---------- 首次启动推送使用说明 ----------

def _push_welcome_if_first_run() -> None:
    """如果是首次运行（outputs/bot_first_run.flag 不存在），向管理员推送使用说明。"""
    flag_path = LOG_DIR / "bot_first_run.flag"
    admin_id = os.environ.get("BOT_ADMIN_USER_ID", "").strip()

    if flag_path.exists() or not admin_id:
        return

    try:
        from dingtalk_bot.credential import send_text_to_user
        welcome = (
            "🎉 智能报表机器人已上线！\n\n"
            "我是您的数据库分析助手，支持以下指令：\n"
            "• 发送\"生产用料\" — 查看加工用料明细\n"
            "• 发送\"质量\" — 查看数据质量诊断\n"
            "• 发送\"字段\" — 查看字段资产盘点\n"
            "• 发送\"扫描\" — 启动数据库扫描\n"
            "• 发送\"进度\" — 查看扫描进度\n"
            "• 发送\"报告\" — 下载分析报告\n"
            "• 发送\"帮助\" — 查看完整菜单\n\n"
            "在群聊中请 @机器人 触发。"
        )
        send_text_to_user(admin_id, welcome)
        flag_path.write_text("1", encoding="utf-8")
        logger.info("首次启动，已向管理员 %s 推送使用说明", admin_id)
    except Exception as exc:
        logger.warning("首次启动推送失败（不影响主流程）: %s", exc)
        flag_path.write_text("1", encoding="utf-8")


# ---------- 主入口 ----------

def main() -> int:
    """启动 Stream 长连接。"""
    logger.info("=" * 60)
    logger.info("智能报表机器人启动中...")
    logger.info("工作目录: %s", ROOT_DIR)
    logger.info("Python: %s", sys.executable)

    # 检查凭证
    client_id = credential.get_client_id()
    client_secret = credential.get_client_secret()
    if not client_id or not client_secret:
        logger.error("缺少钉钉凭证！请在 .env 中配置 DINGTALK_CLIENT_ID 和 DINGTALK_CLIENT_SECRET")
        return 1

    logger.info("Client ID: %s", client_id[:8] + "***")
    logger.info("Corp ID: %s", credential.get_corp_id()[:8] + "***" if credential.get_corp_id() else "(未配置)")

    # 尝试获取 access_token 验证凭证有效性
    try:
        token = credential.get_access_token()
        logger.info("access_token 获取成功，凭证有效")
    except Exception as exc:
        logger.error("access_token 获取失败，请检查凭证: %s", exc)
        return 1

    # 首次启动推送
    _push_welcome_if_first_run()

    # 启动 Stream
    try:
        from dingtalk_stream import DingTalkStreamClient
        from dingtalk_stream.chatbot import ChatbotHandler
        from dingtalk_stream.card import CardCallbackHandler
    except ImportError:
        logger.error("dingtalk-stream 未安装，请运行: pip install dingtalk-stream")
        logger.error("安装后重新启动本程序。")
        return 1

    # 注册 handler
    chatbot_handler = ChatbotHandler()
    chatbot_handler.register_callback_handler(_on_chatbot_message)

    try:
        card_handler = CardCallbackHandler()
        card_handler.register_callback_handler(_on_card_callback)
    except Exception:
        card_handler = None
        logger.warning("CardCallbackHandler 注册跳过（SDK 版本可能不支持）")

    # 创建客户端
    client = DingTalkStreamClient(
        credential.get_client_id(),
        credential.get_client_secret(),
    )
    client.register_callback_handler(chatbot_handler)
    if card_handler:
        client.register_callback_handler(card_handler)

    # 启动定时任务（可选）
    try:
        from dingtalk_bot.scheduler import start_scheduler
        start_scheduler()
        logger.info("定时任务调度器已启动")
    except Exception as exc:
        logger.warning("定时任务启动失败（不影响机器人运行）: %s", exc)

    logger.info("=" * 60)
    logger.info("🤖 机器人已就绪，等待消息...")
    logger.info("=" * 60)

    try:
        client.start_forever()
    except KeyboardInterrupt:
        logger.info("收到 Ctrl+C，机器人停止")
        return 0
    except Exception as exc:
        logger.error("Stream 连接异常: %s", exc, exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
