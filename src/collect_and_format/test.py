import tweepy
import json

# Load settings and connect to Twitter API
settings = json.load(open("mysettings.json"))

consumer_key = settings['consumer_key']
consumer_secret = settings['consumer_secret']
access_token = settings['access_token']
access_token_secret = settings['access_token_secret']

# Authenticate to the twitter API
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

#user = api.get_user(7986822)
timeline = api.user_timeline(id=7986822)

# friends = api.friends_ids(id=user.id)
# followers = api.followers_ids(id=user.id)
# actual_friends = [id for id in friends if id in followers]

# print actual_friends
# for friend in actual_friends:
# 	fuser = api.get_user(id=friend)
# 	print fuser.screen_name
#for friend in user.friends():

verge_file = open("verge","w")
for tweet in timeline:#tweepy.Cursor(api.user_timeline, id=7986822).items(200):
	try:
		print tweet.text
 		verge_file.write(tweet.text + "\n")
	except UnicodeEncodeError, e:
		print "unicode"
		pass
verge_file.close()

