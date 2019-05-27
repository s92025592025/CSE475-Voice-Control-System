import click
import io
import json
import sys

import twitter

class TwitterAPI:
	def __init__(self):
		apiKeyFilePath = click.get_app_dir("twitter-api") + "/credential.json"
		keys = self.__getAPIKeys(apiKeyFilePath)
		self.__API = twitter.Api(consumer_key = keys["consumer-api-key"],
								 consumer_secret = keys["consumer-secret-key"],
								 access_token_key = keys["access-token"],
								 access_token_secret = keys["access-secret"]
		)

	"""
	Get the twitter api information from the given path
	@param path - The path to the credential.json file that contains the
				  Twitter api information
	@return A json object representing the content of the path
	"""
	def __getAPIKeys(self, path):
		output = None
		try:
			with io.open(path, 'r') as f:
				output = json.load(f)
		except Exception as e:
			print("Having issue reading ", path, e)
			sys.exit(-1)

		return output
