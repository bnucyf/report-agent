# -*- coding: utf-8 -*-
"""钉钉机器人 Stream 入口：基于 dingtalk-stream SDK 0.20+ 异步 Handler。

启动方式:
    cd app
    python -m dingtalk_bot.bot

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


# ---------- Stream 回调 Handler ----------

class ReportChatbotHandler:
    """包装 SDK 的 ChatbotHandler，将消息转给业务 dispatch。

    注意：不直接继承 AsyncChatbotHandler，而是在运行时按 SDK 实际 API 选择继承，
    避免不同版本之间类签名差异导致启动失败。
    """

    @staticmethod
    def build(base_cls: type) -> type:
        """返回一个继承自 base_cls 的具体 Handler 类。"""

        class _Handler(base_cls):
            def process(self, callback_message: Any):
                try:
                    msg = self._parse_message(callback_message)
                    if not msg.get("conversation_id"):
                        logger.warning("收到无 conversation_id 的消息，忽略")
                        return

                    text = msg.get("text", "").strip()
                    conversation_id = msg["conversation_id"]
                    sender_id = msg.get("sender_id", "")
                    chat_type = msg.get("chat_type", "")

                    logger.info("收到消息: sender=%s, conv=%s, type=%s, text=%s",
                                sender_id, conversation_id, chat_type, text[:100])

                    if not text:
                        text = "帮助"

                    messages = dispatch(text, conversation_id)
                    _send_messages(conversation_id, messages)
                except Exception as exc:
                    logger.error("处理用户消息失败: %s", exc, exc_info=True)

            def _parse_message(self, callback_message: Any) -> dict[str, Any]:
                """把 SDK CallbackMessage / ChatbotMessage 转成统一字典。"""
                # 优先使用 ChatbotMessage.from_dict 解析 data
                data = getattr(callback_message, "data", callback_message)
                if not isinstance(data, dict):
                    logger.warning("消息 data 不是字典: %s", type(data))
                    return {}

                try:
                    from dingtalk_stream.chatbot import ChatbotMessage
                    chat_msg = ChatbotMessage.from_dict(data)
                except Exception:
                    chat_msg = None

                if chat_msg is not None:
                    text = ""
                    if chat_msg.text and getattr(chat_msg.text, "content", None):
                        text = chat_msg.text.content
                    chat_type = str(chat_msg.conversation_type or "")
                    # 群聊中 @ 机器人时清理 @机器人名
                    if chat_type == "2" and "@" in text:
                        at_parts = text.split(" ", 1)
                        if len(at_parts) > 1 and at_parts[0].startswith("@"):
                            text = at_parts[1].strip()
                        else:
                            text = text.replace("@", "").strip()
                    return {
                        "text": text,
                        "conversation_id": chat_msg.conversation_id or "",
                        "sender_id": chat_msg.sender_id or "",
                        "chat_type": chat_type,
                    }

                # 兜底：直接读字典
                text = data.get("text", {}).get("content", "") if isinstance(data.get("text"), dict) else ""
                chat_type = str(data.get("conversationType", ""))
                if chat_type == "2" and "@" in text:
                    at_parts = text.split(" ", 1)
                    if len(at_parts) > 1 and at_parts[0].startswith("@"):
                        text = at_parts[1].strip()
                    else:
                        text = text.replace("@", "").strip()
                return {
                    "text": text,
                    "conversation_id": data.get("conversationId", ""),
                    "sender_id": data.get("senderId", ""),
                    "chat_type": chat_type,
                }

        return _Handler


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

    # 加载 SDK，按实际可用 API 组装 Handler
    try:
        from dingtalk_stream import DingTalkStreamClient
        from dingtalk_stream.credential import Credential as StreamCredential
        from dingtalk_stream.chatbot import ChatbotMessage, AsyncChatbotHandler
    except ImportError as exc:
        logger.error("dingtalk-stream 未安装或导入失败: %s", exc)
        logger.error("请运行: %s -m pip install -r requirements.txt", sys.executable)
        return 1

    handler_cls = ReportChatbotHandler.build(AsyncChatbotHandler)
    chatbot_handler = handler_cls()

    # 创建客户端并注册 handler
    try:
        stream_credential = StreamCredential(client_id, client_secret)
        client = DingTalkStreamClient(stream_credential)
        client.register_callback_handler(ChatbotMessage.TOPIC, chatbot_handler)
    except Exception as exc:
        logger.error("Stream 客户端初始化失败: %s", exc, exc_info=True)
        return 1

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
