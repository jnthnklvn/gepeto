import sqlite3
import datetime
from typing import List, Dict
import logging

class Database:
    def __init__(self, database_path: str):
        try:
            self._con = sqlite3.connect(database_path, check_same_thread=False)
            self._cur = self._con.cursor()
            self._create_tables()
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")

    def _create_tables(self) -> None:
        try:
            self._cur.execute("CREATE TABLE IF NOT EXISTS user(user_sid TEXT)")
            self._cur.execute("CREATE TABLE IF NOT EXISTS message(user_sid TEXT, role TEXT, content TEXT, created_at TIMESTAMP)")
            self._con.commit()
        except sqlite3.Error as e:
            logging.error(f"Error creating tables: {e}")

    def insert_user(self, user_sid: str) -> None:
        try:
            self._cur.execute("INSERT INTO user (user_sid) VALUES (?)", (user_sid,))
            self._con.commit()
        except sqlite3.Error as e:
            pass

    def insert_message(self, user_sid: str, role: str, content: str) -> None:
        try:
            self._cur.execute("INSERT INTO message (user_sid, role, content, created_at) VALUES (?, ?, ?, ?)",
                        (user_sid, role, content, datetime.datetime.now()))
            self._con.commit()
        except sqlite3.Error as e:
            logging.error(f"Error inserting message: {e}")

    def get_messages_by_user_sid(self, user_sid: str) -> List[Dict[str, str]]:
        try:
            self._cur.execute("SELECT role, content FROM message WHERE user_sid=? ORDER BY created_at ASC", (user_sid,))
            rows = self._cur.fetchall()
            return [{"role": row[0], "content": row[1]} for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Error retrieving messages: {e}")
