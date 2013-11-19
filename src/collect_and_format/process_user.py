import json
import argparse
import tweepy
import time
import os
import sys
from ProgressBar import ProgressBar
import shutil

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

	# Load the list of known users and sort them by id
	users = json.load(open(args.i))
	users = sorted(users, key=int)

	# list of users between lb and ub
	in_bounds_users = filter(lambda u : (args.lb == -1 or int(u) > args.lb) and (args.ub == -1 or int(u) < args.ub), users)

	users = in_bounds_users

	bar = ProgressBar(30)
	max_users = len(users)
	actual = 0
	sleeptime = 1

	# While there is at least one unprocessed user
	while users:
		bar.update(float(actual)/float(max_users))
		u = int(users[0]) # get the next user to be processed

		# create user_directory to store the list of tweets and/or the list of friends
		user_directory = "./" + args.d + "/" + str(u)
		ensure_dir(user_directory)

		try:
			# Getting the last tweets
			if args.act == 'tweets' or args.act == 'both':
				with open(user_directory + "/tweets", "w") as tweets_file:
					# use the twitter API to get the N last tweets from an user timeline
					for tweet in tweepy.Cursor(api.user_timeline, id=u).items(args.N):
						try:
							tweets_file.write(tweet.text + "\n")
						except UnicodeEncodeError:
							pass

			# Getting the list of friends
			if args.act == 'friends' or args.act == 'both':
				friends = api.friends_ids(id=u)		# get the list of friends
				followers = api.followers_ids(id=u)	# get the list of followers

				# we remove the user from the dataset if he/she has more than 1000 friends or more than 1000 followers
				if len(friends) > 1000 or len(followers) > 1000:
					shutil.rmtree(user_directory)
					del users[0]
					continue

				# we assume that the actual set of friends is the intersection between twitter "friends" and followers
				intersect = filter(lambda x : x in followers, friends)

				# saving the friends in a file
				with open(user_directory + "/friends", "w") as friends_file:
					for userid in intersect:
						friends_file.write(str(userid) + "\n")

			del users[0]
		except tweepy.error.TweepError, e:
			# Getting the code of the exception
			exc = json.loads(e.__str__().replace("'", '"').replace('u"', '"'))
			code = exc[0]['code']
			if code == 88:
				sys.stdout.write("\nError while processing user " + str(u) + "\n")
				sys.stdout.write(exc[0]['message'] + ". Waiting " + str(max(4,sleeptime)*15) + " seconds to continue.\n")
				sys.stdout.flush()
				time.sleep(15*max(4,sleeptime))
				sleeptime += 1
				continue
		actual += 1
		sleeptime = 1
