import configparser
from telebot import TeleBot
from src.database import Database
from src.open_ai_api import OpenAIAPI
from src.telegram_bot import TelegramBot
import logging

cfg = configparser.ConfigParser()
cfg.read(".env")

logging.basicConfig(level=logging.INFO)

logging.info(cfg.items('CHAT_GPT'))
logging.info(cfg.items('MONGO'))
logging.info(cfg.items('TELEGRAM'))

api_key = cfg.get("CHAT_GPT", "API_KEY")
db_name = cfg.get("MONGO", "DATABASE_NAME")
db_username = cfg.get("MONGO", "DATABASE_USERNAME")
db_password = cfg.get("MONGO", "DATABASE_PASSWORD")

database = Database(db_name, db_username, db_password)
open_ai_api = OpenAIAPI(database, api_key)

telegramToken = cfg.get("TELEGRAM", "TOKEN")

teleBot = TeleBot(telegramToken, parse_mode=None)
telegramBot = TelegramBot(teleBot, open_ai_api)


@teleBot.message_handler(func=lambda _: True)
def handle_message(message):
    telegramBot.handle_request(message)


teleBot.infinity_polling()
