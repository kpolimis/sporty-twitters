import json
import twitter

settings = json.load(open("settings.json"))

consumer_key = settings['consumer_key']
consumer_secret = settings['consumer_secret']
access_token = settings['access_token']
access_token_secret = settings['access_token_secret']

api = twitter.Api(consumer_key, consumer_secret, access_token, access_token_secret)

statuses = api.GetStreamSample(stall_warnings=True)

#print "rate limit :"
#print api.GetRateLimitStatus()

i = 0
for s in statuses:
    try:
        if s['user']['lang'] == 'en':
            print s
    except KeyError:
        continue
    

