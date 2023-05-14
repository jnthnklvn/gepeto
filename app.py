import os
import configparser
from threading import Thread
from flask import Flask
from telebot import TeleBot
from src.database import Database
from src.twilio_bot import TwilioBot
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

app = Flask(__name__)

cfg = configparser.ConfigParser()
cfg.read(".env")
api_key = cfg.get("CHAT_GPT", "API_KEY")
telegramToken = cfg.get("TELEGRAM", "TOKEN")

open_ai_api = OpenAIAPI(Database("message_gepeto.json"), api_key)
teleBot = TeleBot(telegramToken, parse_mode=None)
telegramBot = TelegramBot(teleBot, open_ai_api)
twilioBot = TwilioBot(open_ai_api)

app.logger.info("Starting server...")


@teleBot.message_handler(func=lambda _: True)
def handle_message(message):
    app.logger.info("Handling message...")
    telegramBot.handle_request(message)


@app.route("/", methods=["POST"])
def start_bot():
    return twilioBot.handle_request()


@app.route("/status", methods=["GET"])
def test():
    return "Hello World!"


if __name__ == "__main__":
    Thread(target=teleBot.infinity_polling).start()
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
