# -*- coding: utf-8 -*-
"""互动卡片管理：创建 / 更新卡片实例。"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from dingtalk_bot import credential

logger = logging.getLogger(__name__)


def send_interactive_card(
    conversation_id: str,
    template_id: str,
    card_data: dict[str, str],
    open_space_id: str = "im_robot",
) -> str | None:
    """创建互动卡片实例，返回 out_track_id（用于后续更新）。"""
    out_track_id = str(uuid.uuid4())
    try:
        result = credential.create_card_instance(
            out_track_id=out_track_id,
            robot_code=credential.get_client_id(),
            conversation_id=conversation_id,
            card_template_id=template_id,
            card_data=card_data,
            open_space_id=open_space_id,
        )
        logger.info("互动卡片创建成功: out_track_id=%s, result=%s", out_track_id, result)
        return out_track_id
    except Exception as exc:
        logger.error("互动卡片创建失败: %s", exc)
        return None


def update_interactive_card(out_track_id: str, card_data: dict[str, str]) -> bool:
    """更新已有互动卡片数据。"""
    try:
        credential.update_card_instance(out_track_id, card_data)
        logger.info("互动卡片更新成功: out_track_id=%s", out_track_id)
        return True
    except Exception as exc:
        logger.error("互动卡片更新失败: %s", exc)
        return False
