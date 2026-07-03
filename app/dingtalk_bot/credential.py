# -*- coding: utf-8 -*-
"""凭证管理：access_token 缓存 + OpenAPI 调用封装。"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)

# ---------- 环境变量读取 ----------

def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def get_client_id() -> str:
    return _env("DINGTALK_CLIENT_ID")


def get_client_secret() -> str:
    return _env("DINGTALK_CLIENT_SECRET")


def get_corp_id() -> str:
    return _env("DINGTALK_CORP_ID")


def get_agent_id() -> str:
    return _env("DINGTALK_AGENT_ID")


# ---------- access_token 缓存 ----------

_token_cache: dict[str, Any] = {"token": "", "expire_at": 0.0}
_OAPI_BASE = "https://oapi.dingtalk.com"
_API_BASE = "https://api.dingtalk.com"


def get_access_token() -> str:
    """获取企业内部应用 access_token，带本地缓存（2h 有效，提前 5 分钟刷新）。"""
    if _token_cache["token"] and time.time() < _token_cache["expire_at"]:
        return _token_cache["token"]

    url = f"{_OAPI_BASE}/gettoken"
    params = {"appkey": get_client_id(), "appsecret": get_client_secret()}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    if data.get("errcode") != 0:
        raise RuntimeError(f"获取 access_token 失败: {data}")

    _token_cache["token"] = data["access_token"]
    _token_cache["expire_at"] = time.time() + int(data.get("expires_in", 7200)) - 300
    logger.info("access_token 刷新成功，有效期 %ss", data.get("expires_in"))
    return _token_cache["token"]


# ---------- OpenAPI 封装 ----------

def _oapi_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = params or {}
    params["access_token"] = get_access_token()
    resp = requests.get(f"{_OAPI_BASE}{path}", params=params, timeout=15)
    return resp.json()


def _oapi_post(path: str, body: dict[str, Any], params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = params or {}
    params["access_token"] = get_access_token()
    resp = requests.post(f"{_OAPI_BASE}{path}", json=body, params=params, timeout=15)
    return resp.json()


def _api_post(path: str, body: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
    headers = headers or {}
    headers["x-acs-dingtalk-access-token"] = get_access_token()
    resp = requests.post(f"{_API_BASE}{path}", json=body, headers=headers, timeout=15)
    return resp.json()


def _api_put(path: str, body: dict[str, Any], headers: dict[str, str] | None = None) -> dict[str, Any]:
    headers = headers or {}
    headers["x-acs-dingtalk-access-token"] = get_access_token()
    resp = requests.put(f"{_API_BASE}{path}", json=body, headers=headers, timeout=15)
    return resp.json()


# ---------- 机器人发消息 ----------

def send_text_to_user(user_id: str, content: str, agent_id: str | None = None) -> dict[str, Any]:
    """单聊发文本消息给指定用户。"""
    body = {
        "robotCode": get_client_id(),
        "userIds": [user_id],
        "msgKey": "sampleText",
        "msgParam": json.dumps({"content": content}, ensure_ascii=False),
    }
    aid = agent_id or get_agent_id()
    return _oapi_post(f"/topapi/message/corpconversation/asyncsend_v2", {**body, "agent_id": int(aid) if aid else 0})


def send_markdown_to_chatbot(conversation_id: str, title: str, text: str) -> dict[str, Any]:
    """通过机器人向会话（单聊/群聊）发 Markdown 消息。

    conversation_id 来自 ChatbotMessage 的 conversation_id 字段。
    """
    body = {
        "robotCode": get_client_id(),
        "conversationId": conversation_id,
        "msgKey": "sampleMarkdown",
        "msgParam": json.dumps({"title": title, "text": text}, ensure_ascii=False),
    }
    return _api_post("/v1.0/robot/oToMessages/batchSend", body)


def send_action_card(conversation_id: str, title: str, text: str, btn_title: str, btn_url: str) -> dict[str, Any]:
    """发 ActionCard（带跳转按钮）。"""
    markdown_text = f"### {title}\n\n{text}\n\n[{btn_title}]({btn_url})"
    body = {
        "robotCode": get_client_id(),
        "conversationId": conversation_id,
        "msgKey": "sampleActionCard",
        "msgParam": json.dumps({
            "title": title,
            "text": markdown_text,
            "singleTitle": btn_title,
            "singleURL": btn_url,
        }, ensure_ascii=False),
    }
    return _api_post("/v1.0/robot/oToMessages/batchSend", body)


# ---------- 互动卡片 ----------

def create_card_instance(
    out_track_id: str,
    robot_code: str,
    conversation_id: str,
    card_template_id: str,
    card_data: dict[str, Any],
    open_space_id: str = "im_robot",
) -> dict[str, Any]:
    """创建互动卡片实例。"""
    body = {
        "outTrackId": out_track_id,
        "robotCode": robot_code,
        "conversationId": conversation_id,
        "cardTemplateId": card_template_id,
        "cardData": {
            "cardParamMap": card_data,
        },
        "openSpaceId": open_space_id,
    }
    return _api_post("/v1.0/card/instances", body)


def update_card_instance(out_track_id: str, card_data: dict[str, Any]) -> dict[str, Any]:
    """更新互动卡片数据（用户点按钮后刷新同一张卡片）。"""
    body = {
        "outTrackId": out_track_id,
        "cardData": {
            "cardParamMap": card_data,
        },
    }
    return _api_put(f"/v1.0/card/instances", body)


# ---------- 文件上传 ----------

def upload_file(file_path: str, file_name: str | None = None) -> dict[str, Any]:
    """上传文件到钉钉，返回 media_id / download_code。"""
    import os
    name = file_name or os.path.basename(file_path)
    # 1) 获取上传凭证
    token = get_access_token()
    url = f"{_OAPI_BASE}/media/upload?access_token={token}&type=file"
    with open(file_path, "rb") as f:
        resp = requests.post(url, files={"media": (name, f)}, timeout=60)
    return resp.json()
