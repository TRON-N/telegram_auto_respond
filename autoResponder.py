import asyncio
import os
from pyrogram import Client, compose
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

from NotifierBot import KeywordChatMatrix, NotifierBot


async def main():
    api_id = os.getenv("TELEGRAM_API_ID")
    api_hash = os.getenv("TELEGRAM_API_HASH")

    user_app = Client("my_account", api_id, api_hash)

    bot_token = os.getenv("TELEGRAM_BOT_API_TOKEN")

    keyword_chat_matrix = KeywordChatMatrix()
    notifier_bot = NotifierBot(api_id, api_hash, bot_token, keyword_chat_matrix)
    
    church_group_id = int(os.getenv('GROUP_CHAT_ID'))
    notification_group_id = int(os.getenv('NOTIFICATION_GROUP_ID'))


    async def my_handler(client, message: Message):
        print(f"Message text: '{message.text}'")
        print(f"Chat ID: '{message.chat.id}' Chat Title: '{message.chat.title}'")
        if isinstance(message.text, str): #and message.chat.id == church_group_id
            message_word_list = message.text.split()
            keyword_chat_dict = keyword_chat_matrix.find_chats_for_keywords(message_word_list)
            print(f"Message matched {len(keyword_chat_dict)} keywords")
            forward_dest_list = []
            for matched_keyword, chat_id_set in keyword_chat_dict.items():
                for chat_id in chat_id_set:
                    if chat_id not in forward_dest_list and message.chat.id != chat_id:
                        print(f"Forwarding message {message.id} to chat {chat_id}")
                        await user_app.forward_messages(
                            chat_id=chat_id,
                            from_chat_id=message.chat.id,
                            message_ids=message.id
                        )
                        forward_dest_list.append(chat_id)

    MessageHandler(my_handler)
    user_app.add_handler(MessageHandler(my_handler))

    apps = [user_app, notifier_bot.bot_app]

    await compose(apps)


if __name__ == "__main__":
    asyncio.run(main())
