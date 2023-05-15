from telebot import TeleBot
from src.open_ai_api import OpenAIAPI


class TelegramBot:
    """
    A Telegram bot for handling user requests.
    """

    def __init__(self, bot: TeleBot, openai_api: OpenAIAPI) -> None:
        """
        Initialize the Telegram bot.

        Args:
            bot: An instance of TeleBot.
            openai_api: An instance of the OpenAIAPI.
        """
        self._bot = bot
        self._openai_api = openai_api

    def handle_request(self, message) -> None:
        """
        Handle user requests and generate responses.

        Args:
            message: The incoming message from the user.
        """
        if "private" == message.chat.type or message.text.lower().find("gepeto") != -1:
            gpt_response = self._openai_api.ask_gpt(
                str(message.chat.id), message.text)
            self._bot.reply_to(message, ''.join(gpt_response))
        else:
            self._openai_api.insert_group_message(
                str(message.chat.id), message.text)
