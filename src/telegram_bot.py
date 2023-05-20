from telebot import TeleBot, types
from src.open_ai_api import OpenAIAPI
from src.graph_ql_client import GraphQLClient
from src.azure_speech_recognizer import AzureSpeechRecognizer
from pydub import AudioSegment
import os
import wave


class TelegramBot:
    """
    A Telegram bot for handling user requests.
    """

    def __init__(self, bot: TeleBot, openai_api: OpenAIAPI) -> None:
        """
        Initialize the Telegram bot.

        Args:
            bot: An instance of TeleBot.
            openai_api: An instance of the OpenAIAPI.
        """
        self._bot = bot
        self._openai_api = openai_api

    def generate_images(self, message: types.Message) -> None:
        """
        Generates images and sends them as a media group to the user.

        Args:
            message: The incoming message from the user.
        """
        try:
            prompt = message.text.replace("/imagem", "")
            if prompt.strip() == "":
                self._bot.reply_to(message, "Você precisa digitar uma frase para gerar imagens.")
                return

            images = self._openai_api.generate_images(str(message.text))
            photos = list(map(lambda img: types.InputMediaPhoto(img["url"]), images))
            self._bot.send_media_group(message.chat.id, photos)
        except:
            self._bot.reply_to(message, "Desculpe, ocorreu um erro ao gerar as imagens.")

    def convert_text_to_speech(self, message: types.Message, speech_recognizer: AzureSpeechRecognizer) -> None:
        """
        Convert text to speech and send it as a voice message to the user.

        Args:
            message: The incoming message from the user.
            speech_recognizer: An instance of the AzureSpeechRecognizer.
        """
        try:
            reply = message.reply_to_message
            if reply == None or reply.text == None or reply.text.strip() == "":
                self._bot.reply_to(message, "Você precisa responder a uma mensagem para gerar o áudio dela.")
                return
            if len(reply.text) > 1500:
                self._bot.reply_to(message, "Essa mensagem ultrapassa o limite de 1500 caracteres.")
                return

            filename = f"{message.chat.id}.wav"
            audio_data = speech_recognizer.convert_text_to_speech(reply.text, filename)
            if audio_data == None:
                self._bot.reply_to(message, "Ocorreu um erro e não foi possível gerar o áudio.")
                return
            with open(filename, "rb") as file:
                self._bot.send_voice(message.chat.id, file)
            os.remove(filename)
        except:
            self._bot.reply_to(message, "Desculpe, ocorreu um erro ao gerar o áudio.")

    def handle_voice_message(self, message: types.Message, speech_recognizer: AzureSpeechRecognizer) -> None:
        """
        Handle user voice messages and generate responses.

        Args:
            message: The incoming message from the user.
            speech_recognizer: An instance of the AzureSpeechRecognizer.
        """
        try:
            filename = self._download_file(message.voice.file_id)
            AudioSegment.from_file(filename).export(filename, format="wav")
            with wave.open(filename) as audio:
                duration_seconds = audio.getnframes() / audio.getframerate()
                if duration_seconds > 30:
                    self._bot.reply_to(message, "Desculpe, não ouço áudio com mais de 30 segundos, tempo é dinheiro!")
                    return
            text = speech_recognizer.convert_speech_to_text(os.path.abspath(filename))
            os.remove(filename)
            if text == "" or text == None:
                self._bot.reply_to(message, "Não entendi o que você falou.")
            else:
                gpt_response = self._openai_api.ask_gpt(str(message.chat.id), text, "audio")
                self._bot.reply_to(message, "".join(gpt_response))
        except:
            self._bot.reply_to(message, "Desculpe, ocorreu um erro ao processar a mensagem de voz.")

    def _download_file(self, file_id: str) -> str:
        file_info = self._bot.get_file(file_id)
        file = self._bot.download_file(file_info.file_path)
        filename = file_info.file_path.split("/")[-1]
        with open(filename, "wb") as new_file:
            new_file.write(file)
        return filename

    def handle_text_message(self, message: types.Message) -> None:
        """
        Handle user text messages and generate responses.

        Args:
            message: The incoming message from the user.
        """
        try:
            if "private" == message.chat.type:
                gpt_response = self._openai_api.ask_gpt(str(message.chat.id), message.text)
                self._bot.reply_to(message, "".join(gpt_response))
        except:
            self._bot.reply_to(message, "Desculpe, ocorreu um erro ao processar a mensagem de texto.")

    def delete_user_messages(self, message: types.Message, client: GraphQLClient) -> None:
        """
        Delete all messages from a user.

        Args:
            message: The incoming message from the user.
            client: An instance of the GraphQLClient.
        """
        try:
            response = client.delete_user_messages(str(message.chat.id))
            deletedCount = response["deletedCount"]
            reply_message = ""
            if deletedCount == None:
                reply_message = "Ocorreu um erro e não foi possível deletar as mensagens."
            elif deletedCount == 0:
                reply_message = "Não há mensagens para serem deletadas."
            else:
                reply_message = f"Todas as mensagens ({deletedCount}) foram deletadas com sucesso!"
            self._bot.reply_to(message, reply_message)
        except:
            self._bot.reply_to(message, "Desculpe, ocorreu um erro ao deletar as mensagens.")
