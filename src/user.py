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
parser.add_argument('-lb', type=int, help='lower bound for the processed user ids',default=-1)
parser.add_argument('-ub', type=int, help='upper bound for the processed user ids',default=-1)

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
	users = sorted(users, key=int)

	restricted_users = []
	for u in users:
		u = int(u)
		if (args.lb == -1 or u > args.lb) and (args.ub == -1 or u < args.ub):
			restricted_users.append(u)
	users = restricted_users

	bar = ProgressBar(30)
	max_users = len(users)
	actual = 0

	for u in users:
		u = int(u)
		actual += 1
		bar.update(float(actual)/float(max_users))
		user_directory = "./" + args.d + "/" + str(u)
		ensure_dir(user_directory)
		try:
			if args.act == 'tweets' or args.act == 'both':
				tweets_file = open(user_directory + "/tweets.json", "w")
				for tweet in tweepy.Cursor(api.user_timeline, id=u).items(args.N):
					tweets_file.write(tweet.text + "\n")
				tweets_file.close()
			if args.act == 'friends' or args.act == 'both':
				friends_file = open(user_directory + "/friends.json", "w")
				user = api.get_user(id=u)
				friends = api.friends_ids(id=user.id)
				followers = api.followers_ids(id=user.id)
				for userid in friends:
					if userid in followers:
						friends_file.write(str(userid) + "\n")
				friends_file.close()
		except UnicodeEncodeError:
			continue
		except tweepy.error.TweepError, e:
			# Handle TweepError correctly
			print e.code
			if e[0] == 88:
				print e[0][0] + "\n" + "Waiting 1 minute to continue."
				time.sleep(60)
			# user tweets are not public, delete his folder
			continue