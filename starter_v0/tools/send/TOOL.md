---
name: send
track: bonus
kind: action
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN]
inputs: [text, confirmed, chat_id]
outputs: [status, chat_id]
side_effect: true
---
# send

Posts text to a Telegram channel. The message is only sent when `confirmed` is true.

`chat_id` is optional. If omitted, the tool uses `TELEGRAM_CHAT_ID` from the environment.
