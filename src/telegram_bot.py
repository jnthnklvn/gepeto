from telebot import TeleBot
from src.open_ai_api import OpenAIAPI
from src.azure_speech_recognizer import AzureSpeechRecognizer
from pydub import AudioSegment
import os
import wave


class TelegramBot:
    """
    A Telegram bot for handling user requests.
    """

    def __init__(self, bot: TeleBot, speech_recognizer: AzureSpeechRecognizer, openai_api: OpenAIAPI) -> None:
        """
        Initialize the Telegram bot.

        Args:
            bot: An instance of TeleBot.
            openai_api: An instance of the OpenAIAPI.
            speech_recognizer: An instance of the AzureSpeechRecognizer.
        """
        self._bot = bot
        self._openai_api = openai_api
        self._speech_recognizer = speech_recognizer

    def handle_voice_message(self, message) -> None:
        """
        Handle user message and generate responses.

        Args:
            message: The incoming message from the user.
        """
        filename = self._download_file(message.voice.file_id)
        AudioSegment.from_file(filename).export(filename, format='wav')
        with wave.open(filename) as audio:
            duration_seconds = audio.getnframes() / audio.getframerate()
            if (duration_seconds > 30):
                self._bot.reply_to(
                    message, "Desculpe, não ouço áudio com mais de 30 segundos, tempo é dinheiro!")
                return
        text = self._speech_recognizer.convert_speech_to_text(
            os.path.abspath(filename))
        os.remove(filename)
        if (text == "" or text == None):
            self._bot.reply_to(message, "Não entendi o que você falou")
        else:
            gpt_response = self._openai_api.ask_gpt(str(message.chat.id), text)
            self._bot.reply_to(message, gpt_response)

    def handle_request(self, message) -> None:
        """
        Handle user requests and generate responses.

        Args:
            message: The incoming message from the user.
        """
        if "private" == message.chat.type:
            gpt_response = self._openai_api.ask_gpt(
                str(message.chat.id), message.text)
            self._bot.reply_to(message, ''.join(gpt_response))

    def _download_file(self, file_id):
        file_info = self._bot.get_file(file_id)
        file = self._bot.download_file(file_info.file_path)
        filename = file_info.file_path.split('/')[-1]
        with open(filename, 'wb') as new_file:
            new_file.write(file)
        return filename
