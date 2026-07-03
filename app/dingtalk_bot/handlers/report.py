# -*- coding: utf-8 -*-
"""报告推送 handler：生成 PDF/Excel + 上传钉钉。"""
from __future__ import annotations

import logging
from typing import Any

from dingtalk_bot.report_pusher import push_report_to_chat

logger = logging.getLogger(__name__)


def handle(text: str, conversation_id: str) -> list[dict[str, str]]:
    """处理报告推送请求。"""
    messages: list[dict[str, str]] = []

    try:
        result = push_report_to_chat(conversation_id, report_type="both")

        lines = ["## 分析报告推送\n"]

        if result.get("pdf_path"):
            lines.append(f"- 📄 PDF 报告已生成并上传")
        else:
            lines.append(f"- ⚠️ PDF 生成失败（可能未安装 Edge/Chrome）")

        if result.get("excel_path"):
            lines.append(f"- 📊 Excel 明细已生成并上传")
        else:
            lines.append(f"- ⚠️ Excel 生成失败")

        uploads = result.get("uploads", [])
        success_uploads = [u for u in uploads if "error" not in u]
        failed_uploads = [u for u in uploads if "error" in u]

        if success_uploads:
            lines.append(f"\n✅ 成功上传 {len(success_uploads)} 个文件到钉钉")
        if failed_uploads:
            lines.append(f"\n❌ {len(failed_uploads)} 个文件上传失败")

        lines.append("\n> 请在聊天文件中查看已上传的报告。")

        messages.append({
            "type": "markdown",
            "title": "报告推送",
            "text": "\n".join(lines),
        })
    except Exception as exc:
        logger.error("报告推送失败: %s", exc)
        messages.append({
            "type": "markdown",
            "title": "报告推送失败",
            "text": f"## 推送失败\n\n```\n{exc}\n```",
        })

    return messages
