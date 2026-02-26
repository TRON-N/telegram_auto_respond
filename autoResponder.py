import asyncio
import os
import re

from telethon import TelegramClient, events
from telethon.tl.custom.message import Message
from DataBackup import DataBackup
from KeywordChatMatrix import KeywordChatMatrix
from datetime import datetime

from NotifierBot import NotifierBot


print("Starting app")
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

user_app = TelegramClient('session_name', api_id, api_hash)

bot_token = os.getenv("TELEGRAM_BOT_API_TOKEN")

backup_file_name = "backup"
keyword_chat_matrix = KeywordChatMatrix()
keyword_chat_matrix.load_from_file(backup_file_name)
data_backup_service = DataBackup(
    keyword_chat_matrix,
    backup_file_name,
    sleep_duration_in_seconds=120,
    backup_time_wait_in_minutes=5,
)

data_backup_service.start_runner()

notifier_bot = NotifierBot(api_id, api_hash, bot_token, keyword_chat_matrix)

church_group_id = int(os.getenv("GROUP_CHAT_ID"))

print(f"api_id: {api_id}, api_hash: {api_hash}, bot_token: {bot_token}, group_chat_id: {church_group_id}")


def build_message_link(message: Message) -> str:
    chat = message.chat
    if chat is None:
        return "Could not generate a direct link for this message."
    if getattr(chat, "username", None):
        return f"https://t.me/{chat.username}/{message.id}"
    chat_id = str(message.chat_id)
    if chat_id.startswith("-100"):
        internal_chat_id = chat_id[4:]
        return f"https://t.me/c/{internal_chat_id}/{message.id}"
    return "Could not generate a direct link for this message."


@user_app.on(events.NewMessage(chats=[church_group_id]))
async def my_handler(event):
    message: Message = event.message
    print(f"Message text: '{message.text}'")
    print(f"Chat ID: '{message.chat.id}' Chat Title: '{message.chat.title}'")
    if isinstance(message.text, str):
        message_word_list = re.split('[^a-zA-Z0-9]', message.text)
        keyword_chat_dict = keyword_chat_matrix.find_chats_for_keywords(
            message_word_list
        )
        print(f"Message matched {len(keyword_chat_dict)} keywords")
        forward_dest_list = []
        for matched_keyword, chat_id_set in keyword_chat_dict.items():
            for chat_id in chat_id_set:
                if chat_id not in forward_dest_list and message.chat.id != chat_id:
                    print(f"Forwarding message {message.id} to chat {chat_id}")
                    message_link = build_message_link(message)
                    await notifier_bot.bot_app.send_message(
                        chat_id,
                        f"New message in the '{message.chat.title}' group matched a keyword.\n\nMessage text:\n\n{message.text}"
                        f"\n\nUse this link to go to the original message in the '{message.chat.title}' group:\n{message_link}",
                    )
                    forward_dest_list.append(chat_id)


async def main():
    await user_app.start()
    await asyncio.gather(*[notifier_bot.run()])


if __name__ == "__main__":
    asyncio.run(main())
