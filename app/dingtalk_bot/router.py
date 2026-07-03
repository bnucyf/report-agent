# -*- coding: utf-8 -*-
"""文本意图路由：关键词匹配 → 主题 handler。"""
from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ---------- 关键词 → handler 映射 ----------

_KEYWORD_MAP: list[dict[str, Any]] = [
    {
        "keywords": ["生产用料", "加工单", "材料出库", "生产分析"],
        "handler": "production",
        "description": "生产加工用料明细",
    },
    {
        "keywords": ["质量", "空值", "异常", "负数", "数据质量"],
        "handler": "quality",
        "description": "数据质量诊断",
    },
    {
        "keywords": ["字段", "资产", "盘点", "字段目录", "字段清单"],
        "handler": "field_asset",
        "description": "字段资产盘点",
    },
    {
        "keywords": ["扫描", "重扫", "重新扫描", "全量扫描", "开始分析"],
        "handler": "scan",
        "description": "重新扫描数据库",
    },
    {
        "keywords": ["报告", "报表导出", "下载报告", "推送报告"],
        "handler": "report",
        "description": "推送分析报告",
    },
    {
        "keywords": ["帮助", "菜单", "使用说明", "怎么用", "help"],
        "handler": "help",
        "description": "使用说明",
    },
    {
        "keywords": ["概览", "总览", "首页", "首页数据"],
        "handler": "overview",
        "description": "数据总览",
    },
]


def load_keywords_config() -> list[dict[str, Any]]:
    """从 config/bot_keywords.json 加载自定义关键词（如有）。

    如果文件不存在、内容格式不对或为空，则回退到内置的 _KEYWORD_MAP，
    避免因为空配置文件导致所有关键词失效。
    """
    config_path = Path(__file__).resolve().parents[2] / "config" / "bot_keywords.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(data, list) and len(data) > 0 and all(
                isinstance(item, dict) and "keywords" in item and "handler" in item
                for item in data
            ):
                return data
            logger.warning(
                "config/bot_keywords.json 内容无效（应为非空 list[dict]），使用内置关键词。"
            )
        except Exception as exc:
            logger.warning("读取 config/bot_keywords.json 失败: %s，使用内置关键词。", exc)
    return _KEYWORD_MAP


def match_intent(text: str) -> str:
    """从用户文本中匹配意图，返回 handler 名称。

    匹配规则：按优先级遍历关键词列表，第一个命中的即为意图。
    未命中任何关键词时返回 "help"（兜底菜单）。
    """
    text = text.strip().lower()
    if not text:
        return "help"

    for item in load_keywords_config():
        for kw in item["keywords"]:
            if kw.lower() in text:
                return item["handler"]

    return "help"


def get_menu_text() -> str:
    """生成菜单文本。"""
    lines = [
        "## 智能报表机器人",
        "",
        "支持以下指令，直接发送关键词即可：",
        "",
    ]
    for item in load_keywords_config():
        kws = " / ".join(item["keywords"][:3])
        desc = item.get("description", "")
        lines.append(f"**{kws}** —— {desc}")
    lines.append("")
    lines.append("> 提示：在群聊中需要 @机器人 触发；单聊直接发送即可。")
    return "\n".join(lines)
