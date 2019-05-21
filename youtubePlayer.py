import sys
import click
import json
import pafy

"""
This serves as the music player for the roomba
"""
class YoutubePlayer:
	def __init__(self):
		apiKeyFile = click.get_app_dir("youtube-api-key") + "/key.json"
		apiKeyJson = json.load(apiKeyFile)
		self.__API_KEY = apiKeyJson['api_key']
		pafy.set_api_key(self.__API_KEY)
