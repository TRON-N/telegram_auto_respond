import shlex
from typing import Awaitable, Callable

from telethon import TelegramClient, events
from telethon.tl.custom.message import Message
from telethon.tl.functions.bots import SetBotCommandsRequest
from telethon.tl.types import BotCommand, BotCommandScopeDefault

from KeywordChatMatrix import KeywordChatMatrix


class NotifierBot:
    def __init__(
        self,
        api_id: str,
        api_hash: str,
        bot_token: str,
        keyword_chat_matrix: KeywordChatMatrix,
    ):
        self.command_dictionary: dict[str, tuple[str, Callable[..., Awaitable[None]]]] = {
            "set": (
                "Sets a keyword for the bot to look out for (case insensitive).",
                self.set_keyword,
            ),
            "list": (
                "Lists the keywords that the bot is currently watching.",
                self.list_keywords,
            ),
            "remove": (
                "Removes a keyword so that the bot no longer watches for it.",
                self.remove_keyword,
            ),
        }
        self.bot_token = bot_token
        self.bot_app = TelegramClient(
            "online_group_notifier_bot",
            api_id=api_id,
            api_hash=api_hash,
        )
        self._set_command_handler()
        self._keyword_chat_matrix = keyword_chat_matrix

    def _set_command_handler(self):
        self.bot_app.add_event_handler(
            self._command_handler,
            events.NewMessage(pattern=r"^/", incoming=True),
        )

    async def run(self) -> None:
        await self.bot_app.start(bot_token=self.bot_token)
        try:
            await self.bot_app(
                SetBotCommandsRequest(
                    scope=BotCommandScopeDefault(),
                    lang_code="en",
                    commands=[
                        BotCommand(command=k, description=v[0])
                        for k, v in self.command_dictionary.items()
                    ],
                )
            )
        except Exception as e:
            print(f"Failed to set bot commands: {e}")
        await self.bot_app.run_until_disconnected()

    async def set_keyword(self, message: Message, args: list[str]) -> None:
        print("Triggered set keyword")
        reply_message = "Incorrect usage, use '/set keyword' with one or more keywords to add them."
        if len(args) > 0:
            self._keyword_chat_matrix.add_keywords(args, message.chat_id)
            reply_message = "Added the following keywords:\n{}".format(
                "\n".join([f"-  {keyword}" for keyword in args])
            )
        await self.bot_app.send_message(
            message.chat_id, reply_message, reply_to=message.id
        )

    async def list_keywords(self, message: Message, args: list[str]) -> None:
        print("Triggered list keyword")
        reply_message = "No keywords are specified, use '/set keyword' with one or more keywords to add them."
        if self._keyword_chat_matrix.does_chat_have_keywords(message.chat_id):
            keyword_list = self._keyword_chat_matrix.find_keywords_for_chat(
                message.chat_id
            )
            keywords = "\n".join([f"-  {keyword}" for keyword in keyword_list])
            reply_message = (
                f"The keyword list contains the following words:\n{keywords}"
            )

        await self.bot_app.send_message(
            message.chat_id, reply_message, reply_to=message.id
        )

    async def remove_keyword(self, message: Message, args: list[str]) -> None:
        print("Triggered remove keyword")

        reply_message = ""
        if len(args) == 0:
            reply_message = "Incorrect usage, use '/remove keyword' with one or more keywords to remove them."
        elif not self._keyword_chat_matrix.does_chat_have_keywords(message.chat_id):
            reply_message = "No keywords exist, use '/set keyword' to add them."
        else:
            removed_list = []
            not_removed_list = []
            for keyword in args:
                if self._keyword_chat_matrix.try_remove_keyword(
                    keyword, message.chat_id
                ):
                    removed_list.append(keyword)
                else:
                    not_removed_list.append(keyword)
            if removed_list:
                reply_message = "Removed the following keywords:\n{}".format(
                    "\n".join([f"-  {keyword}" for keyword in removed_list])
                )
            if not_removed_list:
                if reply_message:
                    reply_message += "\n"
                reply_message += (
                    "Could not find the following keywords for removal:\n{}".format(
                        "\n".join([f"-  {keyword}" for keyword in not_removed_list])
                    )
                )
        await self.bot_app.send_message(
            message.chat_id, reply_message, reply_to=message.id
        )

    async def _command_handler(self, event):
        message: Message = event.message
        text = (event.message.text or "").strip()
        if not text.startswith("/"):
            return
        tokens = shlex.split(text)
        if not tokens:
            return
        cmd_token = tokens[0].lstrip("/").lower()
        cmd = cmd_token.split("@", 1)[0]
        args = tokens[1:] if len(tokens) > 1 else []
        if cmd not in self.command_dictionary:
            return
        await self.command_dictionary[cmd][1](message, args)
