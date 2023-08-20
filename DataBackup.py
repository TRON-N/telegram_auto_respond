from time import sleep
from datetime import timedelta, datetime
import threading
from KeywordChatMatrix import KeywordChatMatrix


class DataBackup:
    def __init__(
        self,
        keyword_chat_matrix: KeywordChatMatrix,
        backup_file_name: str,
        sleep_duration_in_seconds: int,
        backup_time_wait_in_minutes,
    ):
        self._keyword_chat_matrix = keyword_chat_matrix
        self._backup_file_name = backup_file_name
        self._sleep_duration_in_seconds = sleep_duration_in_seconds
        self._backup_time_wait_in_minutes = backup_time_wait_in_minutes
        self._thread = threading.Thread(
            target=self._backup_runner, name="Backup Runner", daemon=True
        )

    def _backup_runner(self):
        while True:
            last_updated = self._keyword_chat_matrix.last_updated
            last_dump = self._keyword_chat_matrix.last_dump
            time_delta = timedelta(minutes=self._backup_time_wait_in_minutes)
            # We want to leave some room, so that we don't try to dump while changes are being made to the data
            if datetime.now() - last_updated > time_delta and last_dump < last_updated:
                print(f"{datetime.now()}: Backing up data")
                self._keyword_chat_matrix.dump_to_file(self._backup_file_name)
                print(f"{datetime.now()}: Backup finished")
            print(f"{datetime.now()}: Sleeping for {self._sleep_duration_in_seconds} seconds")
            sleep(self._sleep_duration_in_seconds)

    def start_runner(self):
        t = threading.Thread(target=self._backup_runner, name="Backup Runner")
        t.daemon = True
        t.start()
