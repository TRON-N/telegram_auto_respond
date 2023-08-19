from pyrogram import Client, filters
from pyrogram.types import Message, BotCommand
from pyrogram.handlers import MessageHandler

class KeywordChatMatrix:
    def __init__(self):
        self._chat_id_keyword_dict: dict[int: set[str]] = {}
        self._keyword_chat_id_dict: dict[str: set[int]] = {}

    def _does_dict_key_keyword_exist(self, keyword: str) -> bool:
        return keyword in self._keyword_chat_id_dict.keys()
    
    def _does_dict_key_chat_id_exist(self, chat_id: int) -> bool:
        return chat_id in self._chat_id_keyword_dict.keys()

    def add_keywords(self, keyword_list: list[str], chat_id: int):
        if not self._does_dict_key_chat_id_exist(chat_id):
            self._chat_id_keyword_dict[chat_id] = set()
        for keyword in keyword_list:
            normalized_keyword = keyword.lower()
            self._chat_id_keyword_dict[chat_id].add(normalized_keyword)

            if not self._does_dict_key_keyword_exist(normalized_keyword):
                self._keyword_chat_id_dict[normalized_keyword] = set()
            self._keyword_chat_id_dict[normalized_keyword].add(chat_id)

    def try_remove_keyword(self, keyword: list[str], chat_id: int) -> bool:
        if self._does_dict_key_chat_id_exist(chat_id):
            try:
                self._chat_id_keyword_dict[chat_id].remove(keyword.lower())
                return True
            except:
                return False
        else:
            return False


    def find_chats_for_keywords(self, keyword_list: list[str]) -> dict[str: set[int]]:
        result_dict = {}
        for keyword in keyword_list:
            normalized_keyword = keyword.lower()
            if self._does_dict_key_keyword_exist(normalized_keyword):
                result_dict[normalized_keyword] = self._keyword_chat_id_dict[normalized_keyword]
        return result_dict


    def find_keywords_for_chat(self, chat_id: int) -> set[str]:
        if self._does_dict_key_chat_id_exist(chat_id):
            return self._chat_id_keyword_dict[chat_id]
        else:
            return set()

    def does_chat_have_keywords(self, chat_id: int) -> bool:
        if self._does_dict_key_chat_id_exist(chat_id):
            return bool(self._chat_id_keyword_dict[chat_id])
        else:
            return False

class NotifierBot:
    def __init__(self, api_id: str, api_hash: str, bot_token: str, keyword_chat_matrix: KeywordChatMatrix):
        self.command_dictionary: dict[str, tuple[str, function]] = {
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
        self.bot_app = Client(
            "online_group_notifier_bot",
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
        )
        self._set_command_handler()
        self._keyword_chat_matrix = keyword_chat_matrix

    # async def set_commands(self):
    #     await self.bot_app.set_bot_commands(
    #         [
    #             BotCommand(key, value[0])
    #             for key, value in self.command_dictionary.items()
    #         ]
    #     )

    def _set_command_handler(self):
        self.bot_app.add_handler(
            MessageHandler(
                self._command_handler,
                filters.command([key for key in self.command_dictionary.keys()]),
            )
        )

    async def set_keyword(self, message: Message):
        print("Triggered set keyword")
        reply_message = "Incorrect usage, use '/set keyword' with one or more keywords to remove them."
        if len(message.command) > 1:
            self._keyword_chat_matrix.add_keywords(message.command[1:], message.chat.id)
            reply_message = "Added the following keywords:\n{}".format(
                "\n".join([f"-  {keyword}" for keyword in message.command[1:]])
            )
        await self.bot_app.send_message(
            chat_id=message.chat.id,
            text=reply_message,
            reply_to_message_id=message.id
        )

    async def list_keywords(self, message: Message):
        print("Triggered list keyword")
        reply_message = "No keywords are specified, use '/set keyword' with one or more keywords to remove them."
        if self._keyword_chat_matrix.does_chat_have_keywords(message.chat.id):
            keyword_list = self._keyword_chat_matrix.find_keywords_for_chat(message.chat.id)
            keywords = "\n".join([f"-  {keyword}" for keyword in keyword_list])
            reply_message = f"The keyword list contains the following words:\n{keywords}"

        await self.bot_app.send_message(
            chat_id=message.chat.id,
            text=reply_message,
            reply_to_message_id=message.id
        )

    async def remove_keyword(self, message: Message):
        print("Triggered remove keyword")

        reply_message = ""
        if len(message.command) == 1:
            reply_message = "Incorrect usage, use '/remove keyword' with one or more keywords to remove them."
        elif not self._keyword_chat_matrix.does_chat_have_keywords(message.chat.id):
            reply_message = "No keywords exist, use '/set keyword' to add them."
        else:
            removed_list = []
            not_removed_list = []
            for keyword in message.command[1:]:
                if self._keyword_chat_matrix.try_remove_keyword(keyword, message.chat.id):
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
            chat_id=message.chat.id,
            text=reply_message,
            reply_to_message_id=message.id
        )

    async def _command_handler(self, client: Client, message: Message):
        for command in message.command:
            if command in self.command_dictionary.keys():
                await self.command_dictionary[command][1](message)
