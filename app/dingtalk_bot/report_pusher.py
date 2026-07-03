# -*- coding: utf-8 -*-
"""报告推送器：HTML→PDF 转换 + Excel 生成 + 钉钉文件上传。"""
from __future__ import annotations

import csv
import io
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dingtalk_bot import credential
from dingtalk_bot.card_builder import build_kpi_markdown

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT_DIR / "outputs" / "reports"
SNAPSHOT_DIR = ROOT_DIR / "outputs" / "snapshots"


def _ensure_dirs() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)


def generate_excel_from_csv(csv_pattern: str, output_name: str) -> Path | None:
    """从最新 CSV 快照生成 Excel 文件。"""
    try:
        import openpyxl
    except ImportError:
        logger.warning("openpyxl 未安装，跳过 Excel 生成")
        return None

    # 找最新 CSV
    files = sorted(SNAPSHOT_DIR.glob(csv_pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None

    csv_path = files[0]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    xlsx_path = REPORT_DIR / f"{output_name}_{stamp}.xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = output_name

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            ws.append(row)

    # 自动列宽
    for col in ws.columns:
        max_len = max(len(str(cell.value or "")) for cell in col[:100])
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 50)

    wb.save(xlsx_path)
    logger.info("Excel 生成: %s", xlsx_path)
    return xlsx_path


def generate_pdf_from_html(html_path: Path | None = None) -> Path | None:
    """HTML → PDF（使用 Edge 或 Chrome 无头模式）。"""
    if html_path is None:
        files = sorted(REPORT_DIR.glob("smart-report-demo_*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not files:
            return None
        html_path = files[0]

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = REPORT_DIR / f"smart-report-demo_{stamp}.pdf"

    # 尝试 Edge
    edge_paths = [
        os.environ.get("EDGE_PATH", ""),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    # 尝试 Chrome
    chrome_paths = [
        os.environ.get("CHROME_PATH", ""),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]

    browser_path = next((p for p in edge_paths + chrome_paths if p and os.path.isfile(p)), None)
    if not browser_path:
        logger.warning("未找到 Edge/Chrome，跳过 PDF 生成")
        return None

    import subprocess
    try:
        subprocess.run(
            [
                browser_path,
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                f"--print-to-pdf={pdf_path}",
                str(html_path),
            ],
            timeout=30,
            capture_output=True,
        )
        if pdf_path.exists():
            logger.info("PDF 生成: %s", pdf_path)
            return pdf_path
    except Exception as exc:
        logger.error("PDF 生成失败: %s", exc)

    return None


def push_report_to_chat(
    conversation_id: str,
    report_type: str = "both",
    chat_type: str = "1",
    sender_staff_id: str = "",
    session_webhook: str = "",
) -> dict[str, Any]:
    """推送报告到钉钉会话。

    report_type:     "pdf" / "excel" / "both"
    chat_type:       "1"=单聊 / "2"=群聊（决定 send_file_to_user/group）
    sender_staff_id: 单聊时必填（消息接收人）
    session_webhook: 若有，优先通过 sessionWebhook 发文件消息（Stream 模式推荐）

    返回 {pdf_path, excel_path, send_results}
    send_results: 包含每个文件的 {upload_media_id, send_result}，便于排查
    """
    _ensure_dirs()
    results: dict[str, Any] = {
        "pdf_path": None,
        "excel_path": None,
        "uploads": [],
        "send_results": [],
    }

    # 1) 生成 Excel 并上传+发送
    if report_type in ("excel", "both"):
        xlsx = generate_excel_from_csv("production_material_usage_*.csv", "生产用料明细")
        if xlsx:
            results["excel_path"] = str(xlsx)
            try:
                upload = credential.upload_file(str(xlsx))
                media_id = upload.get("media_id", "")
                logger.info("Excel 上传结果: media_id=%s, resp=%s", media_id, upload)
                results["uploads"].append({"type": "excel", "upload_resp": upload})

                if media_id and not media_id.startswith("@"):
                    # 旧 oapi 上传返回的 media_id 不带 @ 前缀，需要补
                    media_id = "@" + media_id

                # 真正把文件发到聊天
                send_result = _send_file_to_chat(
                    file_path=str(xlsx),
                    media_id=media_id,
                    chat_type=chat_type,
                    conversation_id=conversation_id,
                    sender_staff_id=sender_staff_id,
                    session_webhook=session_webhook,
                )
                results["send_results"].append({"type": "excel", "media_id": media_id, "send_resp": send_result})
                logger.info("Excel 发送结果: %s", send_result)
            except Exception as exc:
                logger.error("Excel 处理失败: %s", exc, exc_info=True)
                results["uploads"].append({"type": "excel", "error": str(exc)})

    # 2) 生成 PDF 并上传+发送
    if report_type in ("pdf", "both"):
        pdf = generate_pdf_from_html()
        if pdf:
            results["pdf_path"] = str(pdf)
            try:
                upload = credential.upload_file(str(pdf))
                media_id = upload.get("media_id", "")
                logger.info("PDF 上传结果: media_id=%s, resp=%s", media_id, upload)
                results["uploads"].append({"type": "pdf", "upload_resp": upload})

                if media_id and not media_id.startswith("@"):
                    media_id = "@" + media_id

                send_result = _send_file_to_chat(
                    file_path=str(pdf),
                    media_id=media_id,
                    chat_type=chat_type,
                    conversation_id=conversation_id,
                    sender_staff_id=sender_staff_id,
                    session_webhook=session_webhook,
                )
                results["send_results"].append({"type": "pdf", "media_id": media_id, "send_resp": send_result})
                logger.info("PDF 发送结果: %s", send_result)
            except Exception as exc:
                logger.error("PDF 处理失败: %s", exc, exc_info=True)
                results["uploads"].append({"type": "pdf", "error": str(exc)})

    # 3) 发送 Markdown 通知（汇报哪些文件已发送）
    md_lines = ["## 分析报告推送\n"]
    success_files = [s for s in results["send_results"] if s.get("send_resp", {}).get("errcode") == 0]
    failed_files = [s for s in results["send_results"] if s.get("send_resp", {}).get("errcode") != 0]

    if results["pdf_path"]:
        md_lines.append(f"- 📄 PDF 报告：`{Path(results['pdf_path']).name}`")
    if results["excel_path"]:
        md_lines.append(f"- 📊 Excel 明细：`{Path(results['excel_path']).name}`")

    if success_files:
        md_lines.append(f"\n✅ 已成功发送 {len(success_files)} 个文件到聊天")
    if failed_files:
        md_lines.append(f"\n❌ {len(failed_files)} 个文件发送失败，请查看日志")
        for f in failed_files:
            err = f.get("send_resp", {}).get("errmsg", "未知错误")
            md_lines.append(f"  - {f.get('type')}: {err}")
    if not results["send_results"]:
        md_lines.append("\n⚠️ 报告未生成，请检查浏览器是否安装（PDF）或 CSV 快照是否存在（Excel）")

    md_lines.append("\n> 文件已发送到聊天，请直接点击查看或下载。")

    try:
        credential.send_markdown_to_chatbot(
            conversation_id,
            "分析报告",
            "\n".join(md_lines),
        )
    except Exception as exc:
        logger.error("报告通知发送失败: %s", exc)

    return results


def _send_file_to_chat(
    file_path: str,
    media_id: str,
    chat_type: str,
    conversation_id: str,
    sender_staff_id: str,
    session_webhook: str,
) -> dict[str, Any]:
    """把上传好的文件（media_id）作为消息发到聊天。

    优先级：
    1. sessionWebhook 直接 POST（Stream 模式推荐，最稳定）
    2. batchSend / sendToGroupConversation（REST API 回退）
    """
    import os
    file_name = os.path.basename(file_path)

    if not media_id:
        return {"errcode": -1, "errmsg": "media_id 为空，上传可能失败"}

    # 优先级 1：通过 sessionWebhook 发送（Stream 模式官方推荐）
    if session_webhook:
        try:
            result = credential.send_file_via_session_webhook(session_webhook, file_name, media_id)
            if result.get("errcode") == 0:
                return result
            logger.warning("sessionWebhook 发文件失败，回退到 REST API: %s", result)
        except Exception as exc:
            logger.warning("sessionWebhook 发文件异常: %s", exc)

    # 优先级 2：REST API 回退
    if chat_type == "1":
        # 单聊：batchSend + userIds
        if not sender_staff_id:
            return {"errcode": -1, "errmsg": "单聊需要 sender_staff_id"}
        return credential.send_file_to_user(sender_staff_id, file_name, media_id)
    elif chat_type == "2":
        # 群聊：sendToGroupConversation
        return credential.send_file_to_group(conversation_id, file_name, media_id)
    else:
        # 未知类型,尝试单聊
        return credential.send_file_to_user(sender_staff_id, file_name, media_id)
