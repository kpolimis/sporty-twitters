from TwitterAPI import TwitterAPI
import argparse
import json
from collections import defaultdict
import codecs
import sys

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def authenticate(settings_file):
	settings = json.load(open(settings_file, 'r'))

	consumer_key = settings['consumer_key']
	consumer_secret = settings['consumer_secret']
	access_token = settings['access_token']
	access_token_secret = settings['access_token_secret']
	api = TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)

	return api

def files_to_track(files):
	tracked_words = []
	for f in files:
		with open(f, "r") as fd:
			for line in fd:
				tracked_words.append(line.strip())
	return tracked_words

def collect(tracked_words, limit=10, lang=["en-EN", "en", "en-CA", "en-GB"], locations=None):
	req_options = dict()
	req_options['track'] = ",".join(tracked_words)
	req_options['language'] = ",".join(lang)
	if locations:
		req_options['locations'] = locations

	count_tracked_words = {tr:0 for tr in tracked_words}

	r = api.request('statuses/filter', req_options)
	for item in r.get_iterator():
		print json.dumps(item)
		sys.stdout.flush()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--settings", "-s", dest='settings', type=str)
	parser.add_argument("--limit", "-l", type=int, default=0)
	parser.add_argument("-f", "--file", dest='fileflag', action='store_true')
	parser.add_argument("track", type=str, nargs='+')
	args = parser.parse_args()

	tracked_words = (args.fileflag and files_to_track(args.track)) or args.track
	
	api = authenticate(args.settings)
	collect(tracked_words, args.limit)
