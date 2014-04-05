import json
import twitter
import sys
import argparse

def authenticate(settings_file):
	settings = json.load(settings_file)

	consumer_key = settings['consumer_key']
	consumer_secret = settings['consumer_secret']
	access_token = settings['access_token']
	access_token_secret = settings['access_token_secret']

	api = twitter.Api(consumer_key, consumer_secret, access_token, access_token_secret)
	return api

def collect(api, output=sys.stdout, limit=-1, track=[]):
	statuses = api.GetStreamFilter(track=track)
	track = set(h.lower() for h in track)
	
	count = 0
	# check all the statuses using the streaming API
	for s in statuses:
		# stop collecting if we have enough tweets
		if limit > 0 and count >= limit:
			break
		try:
			# checking that the user's language is english
			if s['lang'] == 'en':
				select_tweet = True
				if track:
					hashtags = set([h['text'].lower() for h in s['entities']['hashtags']])
					if not hashtags.intersection(track):
						select_tweet = False
				if select_tweet:
					output.write(json.dumps(s) + "\n")
					count += 1
		except KeyError:
			continue

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--settings", type=str, default=sys.stdin)
	parser.add_argument("--limit", type=int, default=-1)
	parser.add_argument("track", type=str, nargs='+')
	args = parser.parse_args()

	api = authenticate(args.settings)
	collect(api, limit=args.limit, track=args.track)