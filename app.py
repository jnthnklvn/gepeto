import configparser
from telebot import TeleBot
from src.database import Database
from src.open_ai_api import OpenAIAPI
from src.telegram_bot import TelegramBot
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

cfg = configparser.ConfigParser()
cfg.read(".env")
api_key = cfg.get("CHAT_GPT", "API_KEY")
telegramToken = cfg.get("TELEGRAM", "TOKEN")

open_ai_api = OpenAIAPI(Database("message_gepeto.json"), api_key)
teleBot = TeleBot(telegramToken, parse_mode=None)
telegramBot = TelegramBot(teleBot, open_ai_api)


@teleBot.message_handler(func=lambda _: True)
def handle_message(message):
    telegramBot.handle_request(message)


teleBot.infinity_polling()
