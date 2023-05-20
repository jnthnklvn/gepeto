import azure.cognitiveservices.speech as speechsdk
import logging


class AzureSpeechRecognizer:
    """
    A class for performing speech recognition and speech synthesis using Azure Speech Service.
    """

    def __init__(self, speech_key: str, speech_region: str):
        """
        Initialize the Azure Speech Recognizer.

        Args:
            speech_key: The Azure Speech Service subscription key.
            speech_region: The Azure region for the Speech Service.
        """
        self._speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, region=speech_region)
        self._speech_config.speech_recognition_language = "pt-BR"
        self._speech_config.speech_synthesis_voice_name = "pt-BR-AntonioNeural"

    def convert_text_to_speech(self, text: str, filename: str) -> bool:
        """
        Convert text to speech audio file using Azure Speech Service.

        Args:
            text: The text to be converted to speech.
            filename: The audio filename.

        Returns:
            True if the speech synthesis is successful, False otherwise.
        """
        audio_config = speechsdk.audio.AudioOutputConfig(filename=filename)
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self._speech_config, audio_config=audio_config)

        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            logging.error("Speech synthesis canceled: {}".format(
                cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                logging.error("Error details: {}".format(
                    cancellation_details.error_details))
        else:
            logging.error("Unknown speech synthesis error.")
        return False

    def convert_speech_to_text(self, filename: str) -> str:
        """
        Convert speech audio file to text using Azure Speech Service.

        Args:
            filename: The audio filename.

        Returns:
            The text converted from speech, or None if the recognition fails.
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
