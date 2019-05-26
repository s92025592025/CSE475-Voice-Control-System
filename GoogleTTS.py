from google.cloud import texttospeech
import vlc

class GoogleTTS:
	def __init__(self):
		print("Not yet implemented")
		self.__CLIENT = texttospeech.TextToSpeechClient()
		self.__VOICE = texttospeech.types.VoiceSelectionParams(
				language_code='en-US',
				ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL
		)
		self.__AUDIO_CONFIG = texttospeech.types.AudioConfig(
				audio_encoding=texttospeech.enums.AudioEncoding.MP3
		)

		self.__VLC_INSTANCE = vlc.Instance()
		self.__MUSIC_PLAYER = self.__VLC_INSTANCE.media_player_new()
