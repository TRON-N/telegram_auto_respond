import asyncio
import os
from pyrogram import Client, compose
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler



async def main():
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')

    user_app = Client("my_account", api_id, api_hash)

    bot_token = os.getenv('TELEGRAM_BOT_API_TOKEN')

    bot_app = Client(
        "online_group_notifier_bot",
        api_id=api_id, api_hash=api_hash,
        bot_token=bot_token
    )
    
    church_group_id = os.getenv('GROUP_CHAT_ID')
    notification_group_id = os.getenv('NOTIFICATION_GROUP_ID')

    async def my_handler(client, message: Message):
        if isinstance(message.text, str) and message.chat.id == church_group_id:
            if message.text.lower().find('online') != -1:
                await bot_app.send_message(chat_id=notification_group_id, text=f'Quick, {message.from_user.username} might need an online group for someone.')
                # await message.forward('me')

    MessageHandler(my_handler)
    user_app.add_handler(MessageHandler(my_handler))

    apps = [
        user_app,
        bot_app
    ]

    await compose(apps)

if __name__ == '__main__':
    asyncio.run(main())

