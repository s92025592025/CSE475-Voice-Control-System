import click
import sys
import io
import json
import re
import concurrent.futures

import google.oauth2.credentials
import google.auth.transport.requests
import google.auth.transport.grpc

from google.assistant.embedded.v1alpha2 import embedded_assistant_pb2_grpc 
from google.assistant.embedded.v1alpha2 import embedded_assistant_pb2 
from youtubePlayer import YoutubePlayer
from i2c import I2C
from i2c import Registers
from GoogleTTS import GoogleTTS
from TwitterAPI import TwitterAPI

try:
	from googlesamples.assistant.grpc import (
			assistant_helpers,
			audio_helpers,
			device_helpers
	)
except SystemError:
	import assistant_helpers
	import audio_helpers

"""
This class should serve as the a object that runs the setup and 
communication process with Google Assistant SDK(Service)
"""
class GoogleAssistant:
	ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'
	DEFAULT_GRPC_DEADLINE = 60 * 3 + 5

	# Custom command regexs
	PLAY_MUSIC_REG = re.compile("play .*", re.I)
	PAUSE_REG = re.compile("pause", re.I)
	RESUME_REG = re.compile("resume", re.I)
	ADD_2_QUEUE_RE = re.compile("put .* to playlist", re.I)
	NEXT_SONG_RE = re.compile("next song", re.I)
	PREVIOUS_SONG_RE = re.compile('previous song', re.I)
	CLEAR_QUEUE_RE = re.compile('clear playlist', re.I)
	SWITCH_MODE_REG = re.compile("switch to (manual|autonomous) mode", re.I)
	THANOS_SNAP_REG = re.compile("thanos snap", re.I)
	SELF_DESTRUCT_REG = re.compile("initiate self destruct sequence", re.I)
	READ_TWEET_REG = re.compile("read your tweet", re.I)


	"""
	@param i2c - The i2c communication needed to control the arduino
	"""
	def __init__(self, i2c):
		self.__i2c = i2c
		self.__CREDENTIAL_FILE = click.get_app_dir('google-oauthlib-tool') + "/credentials.json"
		deviceConfigFile = click.get_app_dir('googlesamples-assistant') + "/device_config.json"
		self.__deviceInformation(deviceConfigFile)
		self.__authentication()
		self.__audioSetup()
		self.deviceHandler = self.__deviceHandlerSetup()
		self.__create_assistant()

		self.__youtubePlayer = YoutubePlayer()
		self.__tts = GoogleTTS()
		self.__twitterApi = TwitterAPI()

	"""
	Grabs the device information for this assistant session
	@param configPath = The path to the device_config.json file
	@effects modelId - Sets to the model id of the device_config.json file
	@effects id - Sets to the id of the device_config.json file
	@effects clientType - Sets to the client_type if the device_config.json file
	"""
	def __deviceInformation(self, configPath):
		try:
			with io.open(configPath) as configFile:
				configJson = json.load(configFile)
				self.modelId = configJson['model_id']
				self.deviceId = configJson['id']
				self.clientType = configJson['client_type']
		except Exception as e:
			print("Read device config fail ", e)
			sys.exit(-1)
	
	"""
	Authenticate this device by searching default json location
	"""
	def __authentication(self):
		try:
			with io.open(self.__CREDENTIAL_FILE, 'r') as f:
				# Validate credential
				self.credential = google.oauth2.credentials.Credentials(token=None, 
																	**json.load(f))

				# Get an HTTP request function to refresh credentials.
				self.http_request = google.auth.transport.requests.Request()

				# Refresh the credential, don't know why but won't hurt
				self.credential.refresh(self.http_request)
				print("Credential Verified")
		except Exception as e:
			print("Something is wrong with the credential. ", e)
			sys.exit(-1)

	"""
	Sets up the device handler for this device. Must be set after device id
	was set
	"""
	def __deviceHandlerSetup(self):
		print("In device handler setup")
		deviceHandler = device_helpers.DeviceRequestHandler(self.deviceId)

		@deviceHandler.command('action.devices.commands.OnOff')
		def onoff(on):
			if on:
				print("Turned on")
			else:
				print("Turned off")

		return deviceHandler


	"""
	Setup audio information for before starting the assistant service
	"""
	def __audioSetup(self):
		self.audio_sample_rate = audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE
		self.audio_sample_width = audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH
		self.audio_iter_size = audio_helpers.DEFAULT_AUDIO_ITER_SIZE
		self.audio_block_size = audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE
		self.audio_flush_size = audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
		self.grpc_deadline = GoogleAssistant.DEFAULT_GRPC_DEADLINE
		self.conversation_state_bytes = None
		self.volume_percentage = 50

	"""
	Creates the Google Assistant API gRPC client, should be called before
	evoking an Assistant service
	"""
	def __create_assistant(self):
		self.channel = google.auth.transport.grpc.secure_authorized_channel(
												self.credential,
												self.http_request,
												GoogleAssistant.ASSISTANT_API_ENDPOINT)
		self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(self.channel)
		# To enable conversation with Google Assitant
		self.conversationStateBytes = None
		self.isNewConversation = True # Whenever API client is created, must be 
									  # new conversation

	"""
	Setup audio device information for Assistant API to read the audio request
	"""
	def __assistantAudioSetup(self):
		self.audioDevice = audio_helpers.SoundDeviceStream(
											sample_rate=self.audio_sample_rate,
							                sample_width=self.audio_sample_width,
											block_size=self.audio_block_size,
											flush_size=self.audio_flush_size
										)

		self.audioSource = self.audioDevice
		self.audioSink = self.audioDevice

		self.conversationStream = audio_helpers.ConversationStream(
										source=self.audioSource,
										sink=self.audioSink,
										iter_size=self.audio_iter_size,
										sample_width=self.audio_sample_width
									)


	"""
	Start a Assistant request
	"""
	def startAssist(self):
		pausedBefore = True
		if self.__youtubePlayer.isPlaying():
			self.__youtubePlayer.pause() # Stop music so Google Assistant can talk
			pausedBefore = False

		self.__assistantAudioSetup()

		runningActions = []
		ongoingConversation = True
		isCustomCommand = False
		userCommand = ""

		while ongoingConversation:
			self.conversationStream.start_recording()
			print("Google Assistant listening...")

			for response in self.assistant.Assist(self.converseRequestGenerator(), 
												  GoogleAssistant.DEFAULT_GRPC_DEADLINE):
				ongoingConversation = self.__responseAction(response, ongoingConversation)

				# If the user utterance has endded
				if response.event_type == embedded_assistant_pb2.AssistResponse.END_OF_UTTERANCE:
					print("End of Utterance")
					print("User said: ", userCommand)
					self.conversationStream.stop_recording()
					print("G Assistant Stop recording")

					isCustomCommand = self.__customCommands(userCommand)
					if isCustomCommand:
						self.conversationStream.stop_recording()
						self.conversationStream.stop_playback()
						# Is custom command, break out the loop
						break

				# If we got the transcript of the user speech
				if response.speech_results:
					userCommand = "".join(t.transcript for t in response.speech_results)

				if response.device_action.device_request_json:
					actionRequest = json.loads(response.device_action.device_request_json)

					# Received a handler to run
					fs = self.deviceHandler(actionRequest)
					# Check if there is a handler
					if fs:
						runningActions.extend(fs)

			if isCustomCommand:
				# Is custom command, break out the loop
				break

			if len(runningActions):
				print("Should wait for device action to be done: ", len(runningActions))
				concurrent.futures.wait(runningActions)

			self.conversationStream.stop_playback() # Has to be after all the responese
													# were done otherwise the Google
													# Assistant audio output will be shred
													# into pieces

		# Make audio devices free for snowboy
		try:
			self.conversationStream.close()
			print("G Assistant closed conversation stream")

			if self.__resumeMusicAfterAssist(userCommand, pausedBefore):
				self.__youtubePlayer.play()
		except Exception as e:
			print("G Assistant can't close conversation stream", e)
			sys.exit(-1)

	"""
	Do various action according to received response
	@param response - The response sent back from Assistant
	@param furtherConversation - The current state of whether need to
								 have further conversation or not
	@returns Whether need to continue the conversation or not. 
			 True if further conversation is needed, False otherwise
	"""
	def __responseAction(self, response, furtherConversation):
		# If there is audio to output to the user
		if len(response.audio_out.audio_data) > 0:
			# If the device is not playing audio output
			if not self.conversationStream.playing:
				self.conversationStream.stop_recording()
				self.conversationStream.start_playback()

			self.conversationStream.write(response.audio_out.audio_data)

		# Update conversation state
		if response.dialog_state_out.conversation_state:
			self.conversationStateBytes = response.dialog_state_out.conversation_state

		# If Google Assistant needs a follow up, make all audio device available
		# before call startAssist() again
		if response.dialog_state_out.microphone_mode == embedded_assistant_pb2.DialogStateOut.DIALOG_FOLLOW_ON:
			print("Google Assitant wants to talk more")
			return True
		
		# If Google Assistant decided to shutdown the mic, a.k.a she thinks 
		# you are annoying and don't want to listen 2 u
		if response.dialog_state_out.microphone_mode == embedded_assistant_pb2.DialogStateOut.CLOSE_MICROPHONE:
			print("Google Assistant don't want to listen 2 u")
			return False

		return furtherConversation

	"""
	Deals with the commands that is custom to this device. Current know custom commands
	are as follows:
		- Play <Music name/Playlist>
		- Switch [Manual/Autonomous] mode
		- Thanos Snap
		- Initinate Self Destruction Sequence
		- Read your tweet
	@param command - The command issued by the user
	@return True if command is a custom command, otherwise False
	"""
	def __customCommands(self, command):
		# Play music
		if GoogleAssistant.PLAY_MUSIC_REG.match(command):
			print("Play Music detected")
			songName = command[5:]
			print("Play ", songName)
			videoId = self.__youtubePlayer.searchSong(songName)
			if videoId:
				self.__youtubePlayer.stop()
			else:
				self.__tts.text2Speech("Sorry, I can't find proper " + songName + " to play")
				return True # If nothing is found, do nothing

			self.__youtubePlayer.add2Front(videoId)

			return True

		# Pause the music
		if GoogleAssistant.PAUSE_REG.fullmatch(command):
			print("Pause music detected")
			
			return True

		if GoogleAssistant.RESUME_REG.fullmatch(command):
			print("Resume detected")

			return True

		# Add songs to queue
		if GoogleAssistant.ADD_2_QUEUE_RE.match(command):
			print("Add 2 Queue detected")
			songName = command[4:-12]
			print("Add ", songName)
			videoId = self.__youtubePlayer.searchSong(songName)

			if not videoId:
				return True # If nothing is found, keep playing current

			self.__youtubePlayer.add2Queue(videoId)

			return True

		# Next song in the playlist
		if GoogleAssistant.NEXT_SONG_RE.fullmatch(command):
			print("Next song detected")
			self.__youtubePlayer.next()
			self.__youtubePlayer.pause()

			return True

		if GoogleAssistant.RESUME_REG.fullmatch(command):
			print("Resume detected")

			return True

		# Previous song in playlist
		if GoogleAssistant.PREVIOUS_SONG_RE.fullmatch(command):
			print("Previous song detected")
			self.__youtubePlayer.previous()
			self.__youtubePlayer.pause()

			return True

		# Clean playlist
		if GoogleAssistant.CLEAR_QUEUE_RE.fullmatch(command):
			print("Clear playlist detected")
			self.__youtubePlayer.stop()
			self.__youtubePlayer.cleanQueue()

			return True

		# Switch mode
		if GoogleAssistant.SWITCH_MODE_REG.match(command):
			print("Swithing mode")
			modeString = command[10:-5]
			print(modeString)

			if modeString == "manual":
				self.__i2c.changeDriveMode(Registers.MODE_MANUAL)
			elif modeString == "autonomous":
				self.__i2c.changeDriveMode(Registers.MODE_AUTO)

			return True

		# Thanos snap
		if GoogleAssistant.THANOS_SNAP_REG.match(command):
			print("You should have gone for the head")
			self.__tts.text2Speech("You should have gone for the head")
			sys.exit(0)

			return True

		# Self destruct
		if GoogleAssistant.SELF_DESTRUCT_REG.match(command):
			print("Self destruction")

			return True

		# Read Elon Musk tweet
		if GoogleAssistant.READ_TWEET_REG.match(command):
			print("Read tweet")
			self.__tts.text2Speech(self.__twitterApi.getElonLatestTweet())

			return True

		return False

	"""
	Determin whether the music player should resume playing right before
	ending the assistant
	@param command - The command user issued, used to determine whether 
					 the music should resume right before the assistant ended
	@param pausePreviously - Whether the music is paused before thst assistant
							 started. True for music is paused before the assistant
							 start, otherwise False
	@return True when the music should resume right before the assistant ended,
			otherwise False
	"""
	def __resumeMusicAfterAssist(self, command, pausePreviously):
		# Pause music when the user command to 
		if GoogleAssistant.PAUSE_REG.fullmatch(command):
			return False

		# Stop music when user cleared the playlist
		if GoogleAssistant.CLEAR_QUEUE_RE.fullmatch(command):
			return False

		# Play music if user command to
		if GoogleAssistant.PLAY_MUSIC_REG.match(command):
			return True

		# Play music if user add music to queue
		if GoogleAssistant.ADD_2_QUEUE_RE.match(command):
			return True

		# Play music user want next song
		if GoogleAssistant.NEXT_SONG_RE.fullmatch(command):
			return True

		# Play music if user want previous song
		if GoogleAssistant.PREVIOUS_SONG_RE.fullmatch(command):
			return True

		if GoogleAssistant.RESUME_REG.fullmatch(command):
			return True

		# Otherwise depends of whether music is paused before starting the assisatnt
		return not pausePreviously

	"""
	Yields: AssistRequest messages to send to the API.
	"""
	def converseRequestGenerator(self):
		assistantConfig = embedded_assistant_pb2.AssistConfig(
					audio_in_config=embedded_assistant_pb2.AudioInConfig(
						encoding='LINEAR16',
						sample_rate_hertz=self.conversationStream.sample_rate,
					),
					audio_out_config=embedded_assistant_pb2.AudioOutConfig(
						encoding='LINEAR16',
						sample_rate_hertz=self.conversationStream.sample_rate,
						volume_percentage=self.conversationStream.volume_percentage,
					),
					device_config=embedded_assistant_pb2.DeviceConfig(
						device_id=self.deviceId,
						device_model_id=self.modelId,
					),
					dialog_state_in=embedded_assistant_pb2.DialogStateIn(
						language_code='en-US',
						conversation_state=self.conversationStateBytes,
						is_new_conversation=self.isNewConversation,
					),
				)

		# The first request to send the the metadata about the voice request
		yield embedded_assistant_pb2.AssistRequest(config=assistantConfig)

		# Send the rest of the audio data
		for audioData in self.conversationStream:
			yield embedded_assistant_pb2.AssistRequest(audio_in=audioData)
