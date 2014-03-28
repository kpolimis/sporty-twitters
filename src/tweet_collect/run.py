import json
import twitter
import sys

settings = json.load(sys.stdin)

consumer_key = settings['consumer_key']
consumer_secret = settings['consumer_secret']
access_token = settings['access_token']
access_token_secret = settings['access_token_secret']

api = twitter.Api(consumer_key, consumer_secret, access_token, access_token_secret)

statuses = api.GetStreamSample(stall_warnings=True)

i = 0
for s in statuses:
    try:
        if s['user']['lang'] == 'en':
            sys.stdout.write(json.dumps(s))
    except KeyError:
        continue