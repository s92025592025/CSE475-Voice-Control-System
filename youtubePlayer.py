import sys
import click
import json
import pafy

import googleapiclient.discovery

"""
This serves as the music player for the roomba
"""
class YoutubePlayer:
	def __init__(self):
		# Getting our api key
		apiKeyFile = click.get_app_dir("youtube-api-key") + "/key.json"
		apiKeyJson = json.load(apiKeyFile)
		self.__API_KEY = apiKeyJson['api_key']

		# Setup pafy
		pafy.set_api_key(self.__API_KEY)

		# Setup youtube api
		self.__youtubeApi = self.__youtubeApiFactory(self.__API_KEY)

	"""
	Generates a youtube api object
	@param apiKey - The server side api key to use youtube api
	@return an youtube api object
	"""
	def __youtubeApiFactory(self, apiKey):
		apiServiceName = "youtube"
		apiVersion = "v3"

		output = googleapiclient.discovery.build(apiServiceName,
												 apiVersion,
												 developerKey=apiKey)

		return output
