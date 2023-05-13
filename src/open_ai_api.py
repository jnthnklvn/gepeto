import openai
from database import Database
from typing import List, Dict

class OpenAIAPI:
    def __init__(self, database: Database, api_key: str):
        self._database = database
        openai.api_key = api_key

    def _insert_initial_data(self, user_sid: str, user_msg: str) -> List[Dict[str, str]]:
            self._database.insert_user(user_sid)
            self._database.insert_message(user_sid, "user", user_msg)
            messages = self._database.get_messages_by_user_sid(user_sid)
            messages.insert(0, {"role": "system", "content": "Você é um amigo no whatsapp"})
            return messages

    def _get_response(self, user_sid: str, choices: List) -> List[str]:
        response: List[str] = []
        for choice in choices:
            self._database.insert_message(user_sid, choice.message.role, choice.message.content)
            response.append(choice.message.content)
        return response
         

    def ask_gpt(self, user_sid: str, user_msg: str) -> List[str]:
        try:
            messages = self._insert_initial_data(user_sid, user_msg)
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            return self._get_response(user_sid, completion.choices)
        except Exception as exc:
            raise ConnectionError(f"Error communicating with OpenAI: {exc}")
