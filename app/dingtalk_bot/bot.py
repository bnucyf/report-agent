# -*- coding: utf-8 -*-
"""钉钉机器人 Stream 入口：基于 dingtalk-stream SDK 官方 ChatbotHandler 模式。

启动方式:
    cd app
    python -m dingtalk_bot.bot

环境变量（从 .env 读取）:
    DINGTALK_CLIENT_ID       — 应用 AppKey
    DINGTALK_CLIENT_SECRET   — 应用 AppSecret
    DINGTALK_CORP_ID         — 企业 CorpId
    DINGTALK_AGENT_ID        — 应用 AgentId
    BOT_ADMIN_USER_ID        — 管理员 UserId（首次启动推送使用说明）

SDK 参考模式（官方示例）:
    class MyHandler(dingtalk_stream.ChatbotHandler):
        async def process(self, callback: dingtalk_stream.CallbackMessage):
            incoming = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
            self.reply_markdown(title, text, incoming)
            return dingtalk_stream.AckMessage.STATUS_OK, 'OK'
"""
from __future__ import annotations

import asyncio
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


def dispatch(
    text: str,
    conversation_id: str,
    chat_type: str = "1",
    sender_staff_id: str = "",
    session_webhook: str = "",
) -> list[dict[str, str]]:
    """根据用户文本路由到对应 handler，返回消息列表。

    透传额外的会话上下文给需要它们的 handler（目前只有 report 需要 session_webhook
    来发文件消息）。
    """
    intent = match_intent(text)
    handler = _HANDLER_MAP.get(intent)
    if handler is None:
        return [{
            "type": "markdown",
            "title": "未识别",
            "text": get_menu_text(),
        }]
    try:
        # 透传上下文参数（report handler 才会用，其他 handler 自动忽略）
        return handler.handle(
            text,
            conversation_id,
            chat_type=chat_type,
            sender_staff_id=sender_staff_id,
            session_webhook=session_webhook,
        )
    except TypeError:
        # 兼容老 handler（只接受 text, conversation_id）
        try:
            return handler.handle(text, conversation_id)
        except Exception as exc:
            logger.error("handler %s 执行失败: %s", intent, exc, exc_info=True)
            return [{
                "type": "markdown",
                "title": "处理失败",
                "text": f"## 处理失败\n\n```\n{exc}\n```\n\n请重试或联系管理员。",
            }]
    except Exception as exc:
        logger.error("handler %s 执行失败: %s", intent, exc, exc_info=True)
        return [{
            "type": "markdown",
            "title": "处理失败",
            "text": f"## 处理失败\n\n```\n{exc}\n```\n\n请重试或联系管理员。",
        }]


# ---------- Stream 回调 Handler（官方 ChatbotHandler 模式）----------

class ReportChatbotHandler:
    """基于 SDK 官方 ChatbotHandler 的消息处理类。

    使用 async def process(callback) + ChatbotMessage.from_dict(callback.data)
    + self.reply_markdown(title, text, incoming) 通过 sessionWebhook 回复。

    当 sessionWebhook 缺失时，回退到 REST API：
    - 单聊: /v1.0/robot/oToMessages/batchSend（需 userIdList）
    - 群聊: /v1.0/robot/oToMessages/sendToGroupConversation
    """

    @staticmethod
    def build(base_cls: type) -> type:
        """返回一个继承自 base_cls 的具体 Handler 类。

        base_cls 应为 dingtalk_stream.ChatbotHandler（含 reply_markdown 等方法）。
        """

        class _Handler(base_cls):

            async def process(self, callback_message: Any):
                """处理收到的机器人消息，返回 ACK 状态。

                官方模式：
                - 从 callback_message.data 解析 ChatbotMessage
                - 使用 self.reply_markdown() 通过 sessionWebhook 回复
                - 返回 (AckMessage.STATUS_OK, 'OK')

                如果 sessionWebhook 缺失，回退到 REST API。
                """
                try:
                    # 1. 从 CallbackMessage 中提取原始 data 字典
                    data = getattr(callback_message, "data", callback_message)
                    if not isinstance(data, dict):
                        logger.warning("消息 data 不是字典: type=%s", type(data))
                        from dingtalk_stream import AckMessage
                        return AckMessage.STATUS_OK, "skip"

                    # 打印原始 data 中的关键字段（便于排查 sessionWebhook 缺失）
                    has_webhook = "sessionWebhook" in data
                    webhook_url = data.get("sessionWebhook", "")
                    logger.info("原始 data 字段: sessionWebhook=%s, conversationType=%s, senderStaffId=%s",
                                "有" if has_webhook else "无",
                                data.get("conversationType", "?"),
                                data.get("senderStaffId", "?"))

                    # 2. 使用 SDK 的 ChatbotMessage 解析
                    from dingtalk_stream.chatbot import ChatbotMessage
                    incoming = ChatbotMessage.from_dict(data)

                    # 3. 提取文本、会话类型等
                    text = ""
                    if incoming.text and getattr(incoming.text, "content", None):
                        text = incoming.text.content

                    chat_type = str(incoming.conversation_type or "")
                    conversation_id = incoming.conversation_id or ""
                    sender_staff_id = incoming.sender_staff_id or ""

                    # 群聊中 @ 机器人时清理 @机器人名
                    if chat_type == "2" and "@" in text:
                        at_parts = text.split(" ", 1)
                        if len(at_parts) > 1 and at_parts[0].startswith("@"):
                            text = at_parts[1].strip()
                        else:
                            text = text.replace("@", "").strip()

                    if not conversation_id:
                        logger.warning("收到无 conversation_id 的消息，忽略")
                        from dingtalk_stream import AckMessage
                        return AckMessage.STATUS_OK, "skip"

                    if not text:
                        text = "帮助"

                    logger.info("收到消息: sender=%s, conv=%s, type=%s, text=%s, webhook=%s",
                                sender_staff_id,
                                conversation_id,
                                chat_type,
                                text[:100],
                                "有" if incoming.session_webhook else "无")

                    # 4. 路由到业务 handler
                    logger.info("开始处理: text=%s", text[:50])
                    messages = dispatch(
                        text,
                        conversation_id,
                        chat_type=chat_type,
                        sender_staff_id=sender_staff_id,
                        session_webhook=incoming.session_webhook or "",
                    )
                    logger.info("路由完成，共 %s 条回复", len(messages))

                    # 5. 发送回复
                    self._send_replies(incoming, messages, chat_type, sender_staff_id, conversation_id)

                except Exception as exc:
                    logger.error("处理用户消息失败: %s", exc, exc_info=True)

                from dingtalk_stream import AckMessage
                return AckMessage.STATUS_OK, "OK"

            def _send_replies(
                self,
                incoming: Any,
                messages: list[dict[str, str]],
                chat_type: str,
                sender_staff_id: str,
                conversation_id: str,
            ) -> None:
                """发送回复消息。

                优先使用 sessionWebhook（self.reply_markdown，SDK 官方方式）；
                sessionWebhook 缺失时回退到 REST API（区分单聊/群聊）。
                """
                if not messages:
                    logger.info("没有需要回复的消息")
                    return

                for idx, msg in enumerate(messages):
                    msg_type = msg.get("type", "markdown")
                    title = msg.get("title", "通知")
                    text_content = msg.get("text", "")

                    logger.info("发送第 %s/%s 条 (type=%s, title=%s)",
                                idx + 1, len(messages), msg_type, title)

                    try:
                        if incoming.session_webhook:
                            # 方式 A：通过 sessionWebhook 回复（Stream 模式官方推荐）
                            if msg_type == "text":
                                result = self.reply_text(text_content, incoming)
                            else:
                                result = self.reply_markdown(title, text_content, incoming)
                            logger.info("sessionWebhook 回复结果: %s", result)
                        else:
                            # 方式 B：sessionWebhook 缺失，回退到 REST API
                            logger.warning("sessionWebhook 缺失，回退到 REST API (type=%s)", chat_type)
                            if chat_type == "1":
                                # 单聊回退：使用 batchSend + userIdList
                                result = credential.send_markdown_to_user(
                                    sender_staff_id, title, text_content)
                            elif chat_type == "2":
                                # 群聊回退：使用 sendToGroupConversation
                                result = credential.send_markdown_to_group(
                                    conversation_id, title, text_content)
                            else:
                                # 未知类型，尝试 batchSend
                                result = credential.send_markdown_to_user(
                                    sender_staff_id, title, text_content)
                            logger.info("REST API 回复结果: %s", result)

                        time.sleep(0.3)  # 避免消息发送过快被限流
                    except Exception as exc:
                        logger.error("发送消息失败 (type=%s, title=%s): %s",
                                     msg_type, title, exc, exc_info=True)
                        # 回退到 REST API
                        try:
                            if chat_type == "1":
                                result = credential.send_markdown_to_user(
                                    sender_staff_id, title, text_content)
                            else:
                                result = credential.send_markdown_to_group(
                                    conversation_id, title, text_content)
                            logger.info("回退 REST API 结果: %s", result)
                        except Exception as fallback_exc:
                            logger.error("REST API 回退也失败: %s", fallback_exc, exc_info=True)

                logger.info("全部 %s 条回复处理完成", len(messages))

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
            "智能报表机器人已上线！\n\n"
            "我是您的数据库分析助手，支持以下指令：\n"
            "- 发送\"生产用料\" -- 查看加工用料明细\n"
            "- 发送\"质量\" -- 查看数据质量诊断\n"
            "- 发送\"字段\" -- 查看字段资产盘点\n"
            "- 发送\"扫描\" -- 启动数据库扫描\n"
            "- 发送\"进度\" -- 查看扫描进度\n"
            "- 发送\"报告\" -- 下载分析报告\n"
            "- 发送\"帮助\" -- 查看完整菜单\n\n"
            "在群聊中请 @机器人 触发。"
        )
        send_text_to_user(admin_id, welcome)
        flag_path.write_text("1", encoding="utf-8")
        logger.info("首次启动，已向管理员 %s 推送使用说明", admin_id)
    except Exception as exc:
        logger.warning("首次启动推送失败（不影响主流程）: %s", exc)
        flag_path.write_text("1", encoding="utf-8")


# ---------- 进程互斥（防止多实例） ----------

def _check_single_instance() -> bool:
    """检查是否有其他 dingtalk_bot 进程正在运行。"""
    import subprocess
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5,
        )
        count = 0
        for line in result.stdout.splitlines():
            if "dingtalk_bot" in line.lower() or "python" in line.lower():
                # 进一步检查命令行是否包含 dingtalk_bot
                count += 1
        # 更精确：通过 WMIC 检查
        result2 = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'", "get", "processid,commandline", "/format:csv"],
            capture_output=True, text=True, timeout=5,
        )
        bot_count = 0
        for line in result2.stdout.splitlines():
            if "dingtalk_bot" in line:
                bot_count += 1
        if bot_count > 0:
            logger.warning("检测到已有 %d 个 dingtalk_bot 进程在运行，可能导致消息冲突", bot_count)
            logger.warning("建议先关闭旧进程：taskkill /F /IM python.exe /FI \"WINDOWTITLE eq dingtalk*\"")
            # 不强制退出，只警告
            return False
        return True
    except Exception as exc:
        logger.warning("进程检查失败（不影响启动）: %s", exc)
        return True


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

    # 加载 SDK，使用官方 ChatbotHandler 模式
    try:
        from dingtalk_stream import DingTalkStreamClient, AckMessage
        from dingtalk_stream.credential import Credential as StreamCredential
        from dingtalk_stream.chatbot import ChatbotMessage, ChatbotHandler
    except ImportError as exc:
        logger.error("dingtalk-stream 未安装或导入失败: %s", exc)
        logger.error("请运行: %s -m pip install -r requirements.txt", sys.executable)
        return 1

    # 使用 ChatbotHandler（含 reply_markdown/reply_text 方法）
    handler_cls = ReportChatbotHandler.build(ChatbotHandler)
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
    logger.info("[BOT] 机器人已就绪，等待消息...")
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
