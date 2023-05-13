import configparser
from flask import Flask
from database import Database
from twilio_bot import TwilioBot
from open_ai_api import OpenAIAPI
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

def create_app():
    app = Flask(__name__)
    cfg = configparser.ConfigParser()
    cfg.read(".env")

    api_key = cfg.get("CHAT_GPT", "API_KEY")
    open_ai_api = OpenAIAPI(Database("gepeto.db"), api_key)

    return app, TwilioBot(open_ai_api)

if __name__ == "__main__":
    app, bot = create_app()
    app.logger.info("Starting server...")
    app.route("/", methods=["POST"])(bot.handle_request)
    app.run(debug=True)