import sys
import click
import json
import io
import pafy

import googleapiclient.discovery

"""
This serves as the music player for the roomba
"""
class YoutubePlayer:
	def __init__(self):
		# Getting our api key
		apiKeyFile = click.get_app_dir("youtube-api-key") + "/key.json"
		self.__API_KEY = self.__getAPIKey(apiKeyFile)

		# Setup pafy
		pafy.set_api_key(self.__API_KEY)

		# Setup youtube api
		self.__youtubeApi = self.__youtubeApiFactory(self.__API_KEY)

	"""
	Gets the api key from pointed location
	@param path - The path to the json file containing server API key
	"""
	def __getAPIKey(self, path):
		try:
			with io.open(path, 'r') as f:
				keyJson = json.load(f)
				output = keyJson['api_key']
		except Exception as e:
			print("Having issue reading ", path, e)
			sys.exit(-1)

		return output

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

	"""
	Search for the music on youtube with the provided music name
	@param musicName - The music name given by the user
	@return a video id for the first search result, return None when on result us returned
	"""
	def searchSong(self, musicName):
		print("Not implemented")
		request = self.__youtubeApi.search().list(
				part="snippet",
				maxResults=1,
				q=musicName
		)

		response = request.execute() # response is already a json object

		if response['pageInfo']['totalResults'] <= 0:
			return None

		return response['items'][0]['id']['videoId']
