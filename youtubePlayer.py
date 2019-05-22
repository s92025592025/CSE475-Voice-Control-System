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

		# Setup callback events
		self.__musicPlayerEvents = self.__musicPlayer.event_manager()
		self.__musicPlayerEvents.event_attach(vlc.EventType.MediaListPlayerPlayed,
											  self.showCurrentPlaying)

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
	Callback trigger after a song is played. Removed the last played song
	"""
	@vlc.callbackmethod
	def showCurrentPlaying(self, data):
		self.__music2play.remove_index(0)

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
		#print(response)

		if response['pageInfo']['totalResults'] <= 0:
			return None

		# If the first result is a playlist, get the first song of the playlist
		if response['items'][0]['id']['kind'] == "youtube#playlist":
			# Get the first video in the playlist
			playListId = response['items'][0]['id']['playlistId']
			request = self.__youtubeApi.playlistItems().list(
				part="snippet",
				maxResults=1,
				playlistId=playListId
			)

			response = request.execute()

			if response['pageInfo']['totalResults'] <= 0:
				return None

			return response['items'][0]['snippet']['resourceId']['videoId']

		# If the first result is a video get the video id
		return response['items'][0]['id']['videoId']

	"""
	Add one song to the front of the queue to play
	@param videoId - The youtube videoId to play
	"""
	def add2Front(self, videoId):
		media = self.__getBestAudioMedia(videoId)
		self.__music2play.insert_media(media, 0)

	"""
	Add one song to the queue of music to play
	@param videoId - The youtube videoId to play
	"""
	def add2Queue(self, videoId):
		media = self.__getBestAudioMedia(videoId)
		self.__music2play.add_media(media)

	"""
	@param videoId - The youtube videoId to play
	@return A Media object that contains the audio of the videoId
	"""
	def __getBestAudioMedia(self, videoId):
		url = YoutubePlayer.BASE_URL + videoId
		video = pafy.new(url)
		bestAudio = video.getbestaudio()

		return self.__instance.media_new(bestAudio.url)


	"""
	@returns The number of songs songs left in the queue
	"""
	def songsInQueue(self):
		return self.__music2play.count()

	"""
	Clears out the entire medialist
	"""
	def cleanQueue(self):
		while self.songsInQueue() > 0:
			self.__music2play.remove_index(0)

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

	"""
	Stop the music player
	"""
	def stop(self):
		self.__musicPlayer.stop()

	"""
	@return True if the music player is playing, otherwise False
	"""
	def isPlaying(self):
		return self.__musicPlayer.is_playing()
