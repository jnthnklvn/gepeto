import time
from twilio.twiml.messaging_response import MessagingResponse
from flask import  request
from src.open_ai_api import OpenAIAPI
import logging


class TwilioBot:
    def __init__(self, api: OpenAIAPI):
        self._api = api

    def handle_request(self):
        try:
            user_msg = request.values.get('Body', '')
            msg_sid = request.values.get('MessageSid', '')
            user_sid = request.values.get('AccountSid', msg_sid)

            gpt_response = self._api.ask_gpt(user_sid, user_msg)

            response = MessagingResponse()
            for response_msg in gpt_response:
                response.message(response_msg)

            return str(response)
        except Exception as exc:
            logging.error(f"The bot has failed with: {exc}")