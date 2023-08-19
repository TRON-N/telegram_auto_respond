from datetime import datetime
import pickle


class KeywordChatMatrix:
    def __init__(self):
        self._chat_id_keyword_dict: dict[int: set[str]] = {}
        self._keyword_chat_id_dict: dict[str: set[int]] = {}
        current_time = datetime.now()
        self.last_updated = current_time
        self.last_dump = current_time

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
        self.last_updated = datetime.now()

    def try_remove_keyword(self, keyword: list[str], chat_id: int) -> bool:
        if self._does_dict_key_chat_id_exist(chat_id):
            try:
                self._chat_id_keyword_dict[chat_id].remove(keyword.lower())
                self.last_updated = datetime.now()
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
        
    def load_from_file(self, file_name: str):
        try:    
            file_load = pickle.load(open(file_name, 'rb'))
            self._keyword_chat_id_dict = file_load[0]
            self._chat_id_keyword_dict = file_load[1]
            print(f"Successfully loaded backup data from file '{file_name}'")
        except EOFError:
            print(f"No data to read from backup file '{file_name}'")
    
    def dump_to_file(self, file_name: str):
        file_dump = (self._keyword_chat_id_dict, self._chat_id_keyword_dict)
        pickle.dump(file_dump, open(file_name, 'wb'))
        self.last_dump = datetime.now()
        print(f"Dumped data to file '{file_name}'")