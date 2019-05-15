import click
import sys
import io
import json
import google.oauth2.credentials
import google.auth.transport.requests
import google.auth.transport.grpc

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

	def __init__(self):
		self.__CREDENTIAL_FILE = click.get_app_dir('google-oauthlib-tool') + "/credentials.json"
		self.authentication()

	
	"""
	Authenticate this device by searching default json location
	"""
	def authentication(self):
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

		self.channel = google.auth.transport.grpc.secure_authorized_channel(
												self.credential,
												self.http_request,
												GoogleAssistant.ASSISTANT_API_ENDPOINT)

		#return self.channel

	def audioSetup(self):
		self.audio_sample_rate = audio_helpers.DEFAULT_AUDIO_SAMPLE_RATE
		self.audio_sample_width = audio_helpers.DEFAULT_AUDIO_SAMPLE_WIDTH
		self.audio_iter_size = audio_helpers.DEFAULT_AUDIO_ITER_SIZE
		self.audio_block_size = audio_helpers.DEFAULT_AUDIO_DEVICE_BLOCK_SIZE
		self.audio_flush_size = audio_helpers.DEFAULT_AUDIO_DEVICE_FLUSH_SIZE
		self.grpc_deadline = DEFAULT_GRPC_DEADLINE
