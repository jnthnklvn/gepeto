import configparser
from telebot import TeleBot
from src.graph_ql_client import GraphQLClient
from src.open_ai_api import OpenAIAPI
from src.telegram_bot import TelegramBot
from src.azure_speech_recognizer import AzureSpeechRecognizer
import logging

cfg = configparser.ConfigParser()
cfg.read(".env")

logging.basicConfig(level=logging.WARNING)

api_key = cfg.get("CHAT_GPT", "API_KEY")
mongo_api_url = cfg.get("MONGO", "API_URL")
mongo_api_key = cfg.get("MONGO", "API_KEY")

speech_key = cfg.get("AZURE", "SPEECH_KEY")
speech_region = cfg.get("AZURE", "SPEECH_REGION")

speech_recognizer = AzureSpeechRecognizer(speech_key, speech_region)
gqlClient = GraphQLClient(mongo_api_url, mongo_api_key)
openai_api = OpenAIAPI(gqlClient, api_key)

telegram_token = cfg.get("TELEGRAM", "TOKEN")

tele_bot = TeleBot(telegram_token, parse_mode=None)
telegram_bot = TelegramBot(tele_bot, openai_api)


@tele_bot.message_handler(commands=['clear'])
def clear_command(message):
    telegram_bot.delete_user_messages(message, gqlClient)


@tele_bot.message_handler(func=lambda _: True)
def handle_message(message):
    telegram_bot.handle_text_message(message)


@tele_bot.message_handler(content_types=['voice'])
def handle_voice_message(message) -> None:
    telegram_bot.handle_voice_message(message, speech_recognizer)


tele_bot.infinity_polling()
