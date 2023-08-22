import asyncio
import os
import re
from pyrogram import Client, compose, filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
from DataBackup import DataBackup
from KeywordChatMatrix import KeywordChatMatrix

from NotifierBot import NotifierBot


async def main():
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    user_app = Client("my_account", api_id, api_hash)

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

    async def my_handler(client, message: Message):
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
                        await notifier_bot.bot_app.send_message(
                            chat_id=chat_id,
                            text=f"New message in {message.chat.title} matched the set keywords.\n\nMessage text:\n\n{message.text}",
                        )
                        forward_dest_list.append(chat_id)

    MessageHandler(my_handler)
    user_app.add_handler(MessageHandler(my_handler, filters=filters.chat(church_group_id)))

    apps = [user_app, notifier_bot.bot_app]

    await compose(apps)


if __name__ == "__main__":
    asyncio.run(main())
