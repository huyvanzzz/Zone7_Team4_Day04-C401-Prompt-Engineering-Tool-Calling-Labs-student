from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def telegram_updates(limit: int = 20, offset: int = 0) -> dict[str, Any]:
    try:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise RuntimeError("Missing TELEGRAM_BOT_TOKEN env var")

        params: dict[str, Any] = {"limit": max(1, min(int(limit or 20), 100))}
        if offset:
            params["offset"] = int(offset)

        response = requests.get(
            f"https://api.telegram.org/bot{token}/getUpdates",
            params=params,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        updates: list[dict[str, Any]] = []
        chat_ids: list[int] = []
        for item in payload.get("result", []) or []:
            message = item.get("message") or item.get("channel_post") or item.get("edited_message")
            member = item.get("my_chat_member")
            chat = None
            if isinstance(message, dict):
                chat = message.get("chat")
            elif isinstance(member, dict):
                chat = member.get("chat")

            chat_info = None
            if isinstance(chat, dict):
                chat_id = chat.get("id")
                if isinstance(chat_id, int) and chat_id not in chat_ids:
                    chat_ids.append(chat_id)
                chat_info = {
                    "id": chat_id,
                    "type": chat.get("type"),
                    "title": chat.get("title"),
                    "username": chat.get("username"),
                }

            updates.append({
                "update_id": item.get("update_id"),
                "chat": chat_info,
                "has_message": message is not None,
                "has_member_update": member is not None,
            })

        return {
            "tool": "telegram_updates",
            "ok": payload.get("ok", False),
            "count": len(updates),
            "last_update_id": updates[-1]["update_id"] if updates else None,
            "chat_ids": chat_ids,
            "updates": updates,
        }
    except Exception as exc:
        return err("telegram_updates", exc)
