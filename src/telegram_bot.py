import telebot
from src.open_ai_api import OpenAIAPI


class TelegramBot:
    def __init__(self, bot: telebot.TeleBot, openai_api: OpenAIAPI):
        self.bot = bot
        self.openai_api = openai_api
        
    def handle_request(self, message):
        if "private" == message.chat.type or message.text.lower().find("gepeto") != -1:
            gpt_response = self.openai_api.ask_gpt(str(message.chat.id), message.text)
            self.bot.reply_to(message, ''.join(gpt_response))
        else:
            self.openai_api.insertGroupMessage(str(message.chat.id), message.text)
