# -*- coding: utf-8 -*-
"""报告推送 handler：生成 PDF/Excel + 上传钉钉 + 作为消息发到聊天。"""
from __future__ import annotations

import logging
from typing import Any

from dingtalk_bot.report_pusher import push_report_to_chat

logger = logging.getLogger(__name__)


def handle(
    text: str,
    conversation_id: str,
    chat_type: str = "1",
    sender_staff_id: str = "",
    session_webhook: str = "",
) -> list[dict[str, str]]:
    """处理报告推送请求。

    真实流程：生成 PDF/Excel → 上传拿到 media_id → 通过 sessionWebhook（Stream 模式
    官方推荐）把文件作为消息发到聊天。中间任一步失败都会在 Markdown 通知里写明。
    """
    messages: list[dict[str, str]] = []

    try:
        result = push_report_to_chat(
            conversation_id=conversation_id,
            report_type="both",
            chat_type=chat_type,
            sender_staff_id=sender_staff_id,
            session_webhook=session_webhook,
        )

        lines = ["## 分析报告推送\n"]

        if result.get("pdf_path"):
            lines.append(f"- 📄 PDF 报告已生成并发送")
        else:
            lines.append(f"- ⚠️ PDF 生成失败（可能未安装 Edge/Chrome，或 HTML 报告不存在）")

        if result.get("excel_path"):
            lines.append(f"- 📊 Excel 明细已生成并发送")
        else:
            lines.append(f"- ⚠️ Excel 生成失败（可能 CSV 快照不存在）")

        send_results = result.get("send_results", [])
        success = [s for s in send_results if s.get("send_resp", {}).get("errcode") == 0]
        failed = [s for s in send_results if s.get("send_resp", {}).get("errcode") != 0]

        if success:
            lines.append(f"\n✅ 成功发送 {len(success)} 个文件到聊天")
        if failed:
            lines.append(f"\n❌ {len(failed)} 个文件发送失败：")
            for f in failed:
                err = f.get("send_resp", {}).get("errmsg", "未知错误")
                lines.append(f"  - {f.get('type')}: {err}")

        if not send_results:
            lines.append("\n> 没有可发送的文件，请检查浏览器/CSV 快照。")
        else:
            lines.append("\n> 请直接点击聊天中的文件卡片查看或下载。")

        messages.append({
            "type": "markdown",
            "title": "报告推送",
            "text": "\n".join(lines),
        })
    except Exception as exc:
        logger.error("报告推送失败: %s", exc, exc_info=True)
        messages.append({
            "type": "markdown",
            "title": "报告推送失败",
            "text": f"## 推送失败\n\n```\n{exc}\n```",
        })

    return messages
