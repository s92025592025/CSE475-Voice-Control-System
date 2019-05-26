import tempfile

from omxplayer.player import OMXPlayer
from google.cloud import texttospeech

"""
The class is responsable for getting TTS result from Google TSS Cloud and
play it out to user
"""
class GoogleTTS:
	def __init__(self):
		self.__CLIENT = texttospeech.TextToSpeechClient()
		self.__VOICE = texttospeech.types.VoiceSelectionParams(
				language_code='en-US',
				ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL
		)
		self.__AUDIO_CONFIG = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.MP3
		)

		self.__TTSCache = {}

	"""
	Turns user passed text in to audio and play it out
	@param text - The text to talk
	"""
	def text2Speech(self, text):
		if text not in self.__TTSCache:
			print("Not in cache")
			textInput = texttospeech.types.SynthesisInput(text=text)
			response = self.__CLIENT.synthesize_speech(textInput, 
													   self.__VOICE, 
													   self.__AUDIO_CONFIG)
			
			f = tempfile.NamedTemporaryFile(suffix=".mp3")
			f.write(response.audio_content)
			self.__TTSCache[text] = f.name
			print("Temp location: ", self.__TTSCache[text])

		try:
			player = OMXPlayer(self.__TTSCache[text])

			while player.is_playing():
				pass
		except Exception as e:
			print("only omxplayer works, but it is buggy as hell")

