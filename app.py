import os
from dotenv import load_dotenv
from flask import Flask
from src.database import Database
from src.twilio_bot import TwilioBot
from src.open_ai_api import OpenAIAPI
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
load_dotenv()

api_key = os.environ.get("CHAT_GPT_API_KEY")
open_ai_api = OpenAIAPI(Database("message_gepeto.json"), api_key)
bot = TwilioBot(open_ai_api)
app.logger.info("Starting server...")

@app.route("/", methods=["POST"])
def start_bot():
    bot.handle_request()

@app.route("/test", methods=["GET"])
def test():
    return "Hello World!"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))