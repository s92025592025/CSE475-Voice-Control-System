import click
import sys
import io
import json
import google.oauth2.credentials
import google.auth.transport.requests
import google.auth.transport.grpc

"""
This class should serve as the a object that runs the setup and 
communication process with Google Assistant SDK(Service)
"""
class GoogleAssistant:
	ASSISTANT_API_ENDPOINT = 'embeddedassistant.googleapis.com'

	def __init__(self):
		self.__CREDENTIAL_FILE = click.get_app_dir('google-oauthlib-tool') + "/credentials.json"

	
	"""
	Authenticate this device by searching default json location
	"""
	def authentication(self):
		try:
			with io.open(self.__CREDENTIAL_FILE, 'r') as f:
				# Validate credential
				credential = google.oauth2.credentials.Credentials(token=None, 
																	**json.load(f))

				# Get an HTTP request function to refresh credentials.
				http_request = google.auth.transport.requests.Request()

				# Refresh the credential, don't know why but won't hurt
				credential.refresh(http_request)
				print("Credential Verified")
		except Exception as e:
			print("Something is wrong with the credential. ", e)
			sys.exit(-1)

		channel = google.auth.transport.grpc.secure_authorized_channel(credential,
													 http_request,
													 GoogleAssistant.ASSISTANT_API_ENDPOINT)

		return channel
