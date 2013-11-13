import json
import argparse
import tweepy
import time
import os
import sys
from ProgressBar import ProgressBar

def ensure_dir(directory):
	if not os.path.exists(directory):
		os.makedirs(directory)

# Initialize the args parser
parser = argparse.ArgumentParser(description='From a list of users, create one directory by user, store the N last tweets of the user in a file and/or store the user\'s friends in a file')

parser.add_argument('-i', type=str, help='file containing the list of users', metavar='input-file', required=True)
parser.add_argument('-d', type=str, help='directory where the user files will be stored', metavar='output-directory', required=True)
parser.add_argument('-N', type=int, help='number of tweets to collect for each user', metavar='number-tweets', default=200)
parser.add_argument('-s', type=str, help='json file containing the Twitter API key and token', metavar='settings-file', default='settings.json')
parser.add_argument('-act', choices=['tweets', 'friends', 'both'], help='define which action will be executed by the program', default='tweets')

if __name__ == "__main__":
	args = parser.parse_args()

	# Load settings and connect to Twitter API
	settings = json.load(open(args.s))

	consumer_key = settings['consumer_key']
	consumer_secret = settings['consumer_secret']
	access_token = settings['access_token']
	access_token_secret = settings['access_token_secret']

	# Authenticate to the twitter API
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth)

	# Ensure that the directory where we want to store the user tweets and friends exists.
	ensure_dir("./"+args.d)

	# Load the list of known users
	users = json.load(open(args.i))
	bar = ProgressBar(30)
	max_users = len(users)
	actual = 0

	for u in users:
		actual += 1
		user_directory = "./" + args.d + "/" + u
		ensure_dir(user_directory)
		#print "-----" + str(u) + "-----"
		try:
			if args.act == 'tweets' or args.act == 'both':
				tweets_file = open(user_directory + "/tweets.json", "w")
				for tweet in tweepy.Cursor(api.user_timeline, id=u).items(args.N):
					tweets_file.write(tweet.text + "\n")
				tweets_file.close()
		except UnicodeEncodeError:
			continue
		except tweepy.error.TweepError:
			# user tweets are not public, delete his foldeer
			continue
		bar.update(float(actual)/float(max_users))
    #if args.act == 'friends' or args.act == 'both':
	# ids = []
	# for page in tweepy.Cursor(api.followers_ids, screen_name="McDonalds").pages():
	#     ids.extend(page)
	#     print page
	#     time.sleep(60)
