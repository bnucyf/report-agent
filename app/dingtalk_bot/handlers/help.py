# -*- coding: utf-8 -*-
"""帮助 handler：使用说明 + 菜单。"""
from __future__ import annotations

import logging

from dingtalk_bot.router import get_menu_text

logger = logging.getLogger(__name__)


def handle(text: str, conversation_id: str) -> list[dict[str, str]]:
    """返回使用说明。"""
    return [{
        "type": "markdown",
        "title": "使用说明",
        "text": get_menu_text(),
    }]
