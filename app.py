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


@tele_bot.message_handler(commands=['audio'])
def audio_command(message):
    telegram_bot.convert_text_to_speech(message, speech_recognizer)


@tele_bot.message_handler(commands=['imagem'])
def generate_images(message):
    telegram_bot.generate_images(message)


@tele_bot.message_handler(commands=['codigofonte'])
def explain_source_code(message):
    explanation = "O projeto Gepeto é um chatbot que utiliza o modelo OpenAI GPT-3 e integra com um bot do Telegram. " \
                  "Ele pode manter conversas com os usuários e gerar respostas com base nas previsões do modelo " \
                  "OpenAI.\n\nAlém disso, o Gepeto também oferece recursos adicionais, como reconhecimento de voz e " \
                  "conversão de texto para discurso usando o SDK Speech da Azure, e geração de imagens com o modelo " \
                  "DALL-E 2 da OpenAI.\n\nO código-fonte do projeto está disponível em um repositório de código aberto " \
                  "no GitHub. Você pode acessar o repositório em: " \
                  "https://github.com/jnthnklvn/gepeto.\n\nFique à vontade para explorar o código e contribuir com o " \
                  "projeto se desejar!"

    tele_bot.reply_to(message, explanation)


@tele_bot.message_handler(commands=['help'])
def help_command(message):
    help_message = "Olá! Eu sou o Gepeto, um chatbot desenvolvido com o modelo OpenAI GPT-3. " \
                   "Aqui estão os comandos que você pode usar:" \
                   "\n\n/audio - Converte o texto de uma mensagem em um áudio e envia como mensagem de voz." \
                   "\n/codigofonte - Retorna uma breve explicação sobre o projeto e um link para o código-fonte." \
                   "\n/imagem - Gera imagens com base em uma frase e envia como uma sequência de fotos." \
                   "\n/limpar - Deleta todas as suas mensagens enviadas para o bot (inclusive as criadas por ele) do banco de dados." \
                   "\n\nFique à vontade para explorar e conversar comigo!"

    tele_bot.reply_to(message, help_message)


@tele_bot.message_handler(commands=['start'])
def start_command(message):
    intro_message = "Olá! Eu sou o Gepeto, um chatbot desenvolvido com o modelo OpenAI GPT-3. " \
                    "Estou aqui para conversar com você e responder às suas perguntas.\n\n" \
                    "Além disso, posso ajudar nas seguintes tarefas:\n" \
                    "- Gerar e enviar imagens com base nas frases fornecidas.\n" \
                    "- Converter o texto de uma mensagem em áudio.\n" \
                    "- Deletar todas as mensagens dessa conversa do nosso banco de dados.\n\n" \
                    "Para conhecer todos os comandos disponíveis, por favor, utilize o comando /help.\n\n" \
                    "Lembre-se de não enviar informações sensíveis, como senhas ou dados pessoais, para garantir sua segurança."

    tele_bot.reply_to(message, intro_message)


@tele_bot.message_handler(commands=['limpar'])
def clear_command(message):
    telegram_bot.delete_user_messages(message, gqlClient)


@tele_bot.message_handler(content_types=['voice'])
def handle_voice_message(message) -> None:
    telegram_bot.handle_voice_message(message, speech_recognizer)


@tele_bot.message_handler(func=lambda _: True)
def handle_message(message):
    telegram_bot.handle_text_message(message)


tele_bot.infinity_polling()
