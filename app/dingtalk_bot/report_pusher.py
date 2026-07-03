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

from . import credential
from .card_builder import build_kpi_markdown

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


def push_report_to_chat(conversation_id: str, report_type: str = "both") -> dict[str, Any]:
    """推送报告到钉钉会话。

    report_type: "pdf" / "excel" / "both"
    返回 {pdf_path, excel_path, upload_results}
    """
    _ensure_dirs()
    results: dict[str, Any] = {"pdf_path": None, "excel_path": None, "uploads": []}

    # 1) 生成 Excel
    if report_type in ("excel", "both"):
        xlsx = generate_excel_from_csv("production_material_usage_*.csv", "生产用料明细")
        if xlsx:
            results["excel_path"] = str(xlsx)
            try:
                upload = credential.upload_file(str(xlsx))
                results["uploads"].append({"type": "excel", "result": upload})
            except Exception as exc:
                results["uploads"].append({"type": "excel", "error": str(exc)})

    # 2) 生成 PDF
    if report_type in ("pdf", "both"):
        pdf = generate_pdf_from_html()
        if pdf:
            results["pdf_path"] = str(pdf)
            try:
                upload = credential.upload_file(str(pdf))
                results["uploads"].append({"type": "pdf", "result": upload})
            except Exception as exc:
                results["uploads"].append({"type": "pdf", "error": str(exc)})

    # 3) 发送 Markdown 通知
    md_lines = ["## 分析报告已生成\n"]
    if results["pdf_path"]:
        md_lines.append(f"- 📄 PDF 报告：`{Path(results['pdf_path']).name}`")
    if results["excel_path"]:
        md_lines.append(f"- 📊 Excel 明细：`{Path(results['excel_path']).name}`")
    md_lines.append("\n> 文件已上传到钉钉，请在聊天文件中查看。")

    try:
        credential.send_markdown_to_chatbot(
            conversation_id,
            "分析报告",
            "\n".join(md_lines),
        )
    except Exception as exc:
        logger.error("报告通知发送失败: %s", exc)

    return results
