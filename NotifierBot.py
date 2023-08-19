from pyrogram import Client, filters
from pyrogram.types import Message, BotCommand
from pyrogram.handlers import MessageHandler


class NotifierBot:
    def __init__(self, api_id, api_hash, bot_token):
        self.command_dictionary: dict[str, tuple[str, function]] = {
            "set": (
                "Sets a keyword for the bot to look out for (case insensitive).",
                self.set_key_word,
            ),
            "list": (
                "Lists the keywords that the bot is currently watching.",
                self.list_key_words,
            ),
            "remove": (
                "Removes a keyword so that the bot no longer watches for it.",
                self.remove_key_word,
            ),
        }
        self.bot_app = Client(
            "online_group_notifier_bot",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
        )

    def _set_commands(self):
        self.bot_app.set_bot_commands(
            [
                BotCommand(key, value[0])
                for key, value in self.command_dictionary.items()
            ]
        )

    def _set_command_handler(self):
        self.bot_app.add_handler(
            MessageHandler(
                self._command_handler,
                filters.command([key for key in self.command_dictionary.keys()]),
            )
        )

    def set_key_word(self, message: Message):
        print("Triggered set keyword")
        print(message)

    def list_key_words(self, message: Message):
        print("Triggered list keyword")
        print(message)

    def remove_key_word(self, message: Message):
        print("Triggered remove keyword")
        print(message)

    async def _command_handler(self, client: Client, message: Message):
        for command in message.command:
            self.command_dictionary[command][1](message)