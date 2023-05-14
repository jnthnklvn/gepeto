import openai
from src.database import Database
from typing import List, Dict
import logging


class OpenAIAPI:
    def __init__(self, database: Database, api_key: str):
        self._database = database
        openai.api_key = api_key

    def _insert_initial_data(self, user_sid: str, user_msg: str) -> List[Dict[str, str]]:
        try:
            self._database.insert_message(user_sid, "user", user_msg)
            messages = self._database.get_messages_by_user_sid(user_sid)
            messages.insert(
                0, {"role": "system", "content": "Considere que seu nome é Gepeto e que esta conversa é com um amigo."})
            return messages
        except Exception as e:
            logging.error(f"Error starting the database connection: {e}")

    def _get_response(self, user_sid: str, choices: List) -> List[str]:
        try:
            response: List[str] = []
            for choice in choices:
                self._database.insert_message(
                    user_sid, choice.message.role, choice.message.content)
                response.append(choice.message.content)
            return response
        except Exception as e:
            logging.error(f"Error trying to insert choices from gpt: {e}")

    def insertGroupMessage(self, chat_id: str, chat_msg: str) -> None:
        self._database.insert_message(chat_id, "user", chat_msg)

    def ask_gpt(self, user_sid: str, user_msg: str) -> List[str]:
        messages = self._insert_initial_data(user_sid, user_msg)
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return self._get_response(user_sid, completion.choices)
        except Exception as exc:
            raise ConnectionError(f"Error communicating with OpenAI: {exc}")
