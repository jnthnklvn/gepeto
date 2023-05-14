import configparser
from telebot import TeleBot
from src.graph_ql_client import GraphQLClient
from src.open_ai_api import OpenAIAPI
from src.telegram_bot import TelegramBot
import logging

cfg = configparser.ConfigParser()
cfg.read(".env")

logging.basicConfig(level=logging.WARNING)

api_key = cfg.get("CHAT_GPT", "API_KEY")
mongo_api_url = cfg.get("MONGO", "API_URL")
mongo_api_key = cfg.get("MONGO", "API_KEY")

gqlClient = GraphQLClient(mongo_api_url, mongo_api_key)
open_ai_api = OpenAIAPI(gqlClient, api_key)

telegramToken = cfg.get("TELEGRAM", "TOKEN")

teleBot = TeleBot(telegramToken, parse_mode=None)
telegramBot = TelegramBot(teleBot, open_ai_api)


@teleBot.message_handler(func=lambda _: True)
def handle_message(message):
    telegramBot.handle_request(message)


teleBot.infinity_polling()
