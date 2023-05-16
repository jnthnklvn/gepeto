import azure.cognitiveservices.speech as speechsdk
import logging


class AzureSpeechRecognizer:
    def __init__(self, speech_key: str, speech_region: str):
        """
        Initialize the Azure Speech Recognizer.

        Args:
            speech_key: The Azure Speech Service subscription key.
            speech_region: The Azure region for the Speech Service.
        """

        # Set up the speech configuration
        self._speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, region=speech_region)
        self._speech_config.speech_recognition_language = "pt-BR"

    def convert_speech_to_text(self, filename) -> str:
        """
        Convert speech audio file to text using Azure Speech Service.

        Args:
            filename: The audio filename.

        Returns:
            The text converted from speech.
        """

        audio_config = speechsdk.audio.AudioConfig(filename=filename)
        speech_recognizer = speechsdk.SpeechRecognizer(
            language=self._speech_config.speech_recognition_language,
            speech_config=self._speech_config, audio_config=audio_config)

        result = speech_recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return result.text
        elif result.reason == speechsdk.ResultReason.NoMatch:
            logging.error("Speech not recognized.")
        elif result.reason == speechsdk.ResultReason.Canceled:
            logging.error("Speech recognition canceled.")
        else:
            logging.error("Unknown speech recognition error.")
        return None
