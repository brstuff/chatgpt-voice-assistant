import logging
import os
import subprocess
import platform


from chatgpt_voice_assistant.bases.responder import Responder
from chatgpt_voice_assistant.bases.text_to_speech_client import TextToSpeechClient
from chatgpt_voice_assistant.exceptions.respond_error import RespondError


class ComputerVoiceResponder(Responder):
    """Responder that responds to the user with the Computer Voice"""

    def __init__(
        self,
        text_to_speech_client: TextToSpeechClient,
        audio_filename: str,
        speech_rate: float = 1.0,
    ) -> None:
        self._text_to_speech_client: TextToSpeechClient = text_to_speech_client
        self._audio_filename: str = os.path.join(
            os.getcwd(),
            audio_filename + self._text_to_speech_client.audio_extension,
        )
        self._speech_rate: float = speech_rate

    def respond(self, text_to_speak: str) -> None:
        """
        Speak the referenced text on the machine speakers.
        :param text_to_speak: the text to speak.
        :return: None
        """
        try:
            logging.debug(f"ComputerVoiceResponder.speak - '{text_to_speak}'")
            self._text_to_speech_client.convert_text_to_audio(
                text_to_speak, self._audio_filename
            )
            if platform.system() == 'Darwin':  # Verifica se o sistema é OSX
                cmd = ["afplay", "--rate", str(self._speech_rate), self._audio_filename]
            else:
                cmd = ["ffplay", self._audio_filename, "-autoexit", "-nodisp", "-loglevel", "quiet", "-stats"]

            logging.debug(cmd)
            subprocess.call(cmd)
        except Exception as e:
            raise RespondError(f"Error running computer voice response: {e}") from e
        finally:
            self._cleanup_temp_files()

    def _cleanup_temp_files(self) -> None:
        """
        Remove all temporary files and cleanup before shutting down.
        :return: None
        """
        logging.debug(
            f"ComputerVoiceResponder._cleanup_temp_files - {self._audio_filename}"
        )

        # Check if temporary file exists before trying to delete.
        if os.path.exists(self._audio_filename):
            os.remove(self._audio_filename)
