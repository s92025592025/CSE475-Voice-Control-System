import sys
import click
import json
import io
import pafy

import vlc
import googleapiclient.discovery

"""
This serves as the music player for the roomba
"""
class YoutubePlayer:
	BASE_URL = "https://www.youtube.com/watch?v="

	def __init__(self):
		# Getting our api key
		apiKeyFile = click.get_app_dir("youtube-api-key") + "/key.json"
		self.__API_KEY = self.__getAPIKey(apiKeyFile)

		# Setup pafy
		#pafy.set_api_key(self.__API_KEY)

		# Setup youtube api
		self.__youtubeApi = self.__youtubeApiFactory(self.__API_KEY)

		# Setup vlc instance and player
		self.__instance = vlc.Instance()
		self.__musicPlayer = self.__instance.media_list_player_new()

		# Setup music queue
		self.__music2play = self.__instance.media_list_new()
		self.__musicPlayer.set_media_list(self.__music2play)

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
		request = self.__youtubeApi.search().list(
				part="snippet",
				maxResults=1,
				q=musicName
		)

		response = request.execute() # response is already a json object

		if response['pageInfo']['totalResults'] <= 0:
			return None

		return response['items'][0]['id']['videoId']

	"""
	Add one song to the queue of music to play
	@param videoId - The youtube videoId to play
	"""
	def add2Queue(self, videoId):
		url = YoutubePlayer.BASE_URL + videoId
		video = pafy.new(url)
		bestAudio = video.getbestaudio()

		media = self.__instance.media_new(bestAudio.url)
		self.__music2play.add_media(media)

	"""
	@returns The number of songs songs left in the queue
	"""
	def songsInQueue(self):
		return self.__music2play.count()

	"""
	Plays music in the queue
	@return True when there is music to play and playing, otherwise False
	"""
	def play(self):
		self.__musicPlayer.play()

		return True

	"""
	Pause currently playing music
	"""
	def pause(self):
		self.__musicPlayer.pause()

