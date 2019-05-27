import click
import io
import json
import sys

import twitter

class TwitterAPI:
	ELON_THE_MASTER_ID = 44196397
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

	"""
	Get the user twitter timeline by user id.
	@param userId - The user id. Must be int
	@return a Json obj of the timeline
	"""
	def getUserTimeLineById(self, userId):
		return self.__API.GetUserTimeline(userId)

	"""
	Get the user twitter timeline by user name.
	@param userName - The on screen user name you can easily 
					  find on the twitter page
	@return a Json obj of the timeline
	"""
	def getUserTimeLineByScreenName(self, userName):
		return self.__API.GetUserTimeline(screen_name=userName)

	"""
	Gets the content of the latest tweet of the one and only 
	meme master Elon Musk.
	@return a string of the content of the latest tweet
	"""
	def getElonLatestTweet(self):
		status = self.getUserTimeLineById(TwitterAPI.ELON_THE_MASTER_ID)

		return status[0].text
