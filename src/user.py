import json
import argparse
import tweepy
import time
import os

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

# Initialize the args parser
parser = argparse.ArgumentParser(description='From a list of users, create one directory by user, store the N last tweets of the user in a file and/or store the user\'s friends in a file')

parser.add_argument('-i', type=str, help='file containing the list of users', metavar='input-file', required=True)
parser.add_argument('-d', type=str, help='directory where the user files will be stored', metavar='output-directory', required=True)
parser.add_argument('-N', type=int, help='number of tweets to collect for each user', metavar='number-tweets', default=200)
parser.add_argument('-s', type=str, help='json file containing the Twitter API key and token', metavar='settings-file', default='settings.json')

args = parser.parse_args()
settings = json.load(open(args.s))

consumer_key = settings['consumer_key']
consumer_secret = settings['consumer_secret']
access_token = settings['access_token']
access_token_secret = settings['access_token_secret']

# Authenticate to the twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

for status in tweepy.Cursor(api.user_timeline, id=888451525).items(20):
	print status.text

# ids = []
# for page in tweepy.Cursor(api.followers_ids, screen_name="McDonalds").pages():
#     ids.extend(page)
#     print page
#     time.sleep(60)
