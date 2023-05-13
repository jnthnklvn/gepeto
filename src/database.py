from pysondb import db
from typing import List, Dict
import logging

class Database:
    def __init__(self, database_path: str):
        try:
            self._messageDb = db.getDb(database_path)
        except Exception as e:
            logging.error(f"Error connecting to database: {e}")

    def insert_message(self, user_sid: str, role: str, content: str) -> None:
        try:
            self._messageDb.add({"user_sid": user_sid, "role": role, "content": content})
        except Exception as e:
            logging.error(f"Error inserting message: {e}")

    def get_messages_by_user_sid(self, user_sid: str) -> List[Dict[str, str]]:
        try:
            result = self._messageDb.getBy({"user_sid": user_sid})
            messages = list(map(lambda x: {"role": x["role"], "content": x["content"]}, result))
            return messages
        except Exception as e:
            logging.error(f"Error retrieving messages: {e}")
