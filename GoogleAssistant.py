import click
import sys
import io
import json
import google.oauth2.credentials
import google.auth.transport.requests
import google.auth.transport.grpc
from google.assistant.embedded.v1alpha2 import embedded_assistant_pb2_grpc 

try:
	from googlesamples.assistant.grpc import (
			assistant_helpers,
			audio_helpers
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

	def __init__(self):
		self.__CREDENTIAL_FILE = click.get_app_dir('google-oauthlib-tool') + "/credentials.json"
		self.__authentication()
		self.__audioSetup()
		self.__create_assistant()

	
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
		print("GRPC Channel Created")
		self.assistant = embedded_assistant_pb2_grpc.EmbeddedAssistantStub(self.channel)
		print("Created Google Assistant API gRPC client.")

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

		self.conversation_stream = audio_helpers.ConversationStream(
										source=self.audioSource,
										sink=self.audioSink,
										iter_size=self.audio_iter_size,
										sample_width=self.audio_sample_width
									)


	"""
	Start a Assistant request
	"""
	def startAssist(self):
		print("StartAssist() Not implemented")
		self.__assistantAudioSetup()


	"""
	Generates the conversation request for Google Assistant API
	"""
	def converseRequestGenerator(self):
		print("converseRequestGenerator() Not yet implemented")
