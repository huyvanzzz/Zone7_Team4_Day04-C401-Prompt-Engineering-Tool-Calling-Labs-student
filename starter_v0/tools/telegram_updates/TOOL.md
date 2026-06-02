---
name: telegram_updates
track: bonus
kind: live_api
provider: Telegram Bot API
requires_env: [TELEGRAM_BOT_TOKEN]
inputs: [limit, offset]
outputs: [chat_ids, updates]
side_effect: false
---
# telegram_updates

Reads recent Telegram bot updates and extracts candidate chat IDs.

Use this tool when the bot has already been added to a group and you need the
numeric `chat_id` for that group, or when you want to verify that the bot is
receiving updates.

Do not use this tool to send messages.
