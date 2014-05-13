import argparse
import sys
import re
from collections import defaultdict
import json

def get_tweets_containing(n, words_file, each_word_n=True, in_stream=sys.stdin, out_stream=sys.stdout, raw_json=False):
	found_tweets = []
	words_set = set()
	words_count = defaultdict(int)

	# Load the words to find in the corpus, one word per line
	with open(words_file, "r") as f:
		for line in f:
			w = line.strip()
			words_set.add(w)
			words_count[w] = 0

	# initialize count variables
	count = 0

	# Process each line of the input stream
	for line in in_stream:
		# if working with raw json, extract the text from the tweet
		if raw_json:
			tw = json.loads(line)
			line = tw['text']

		# get the tweet and check that words we look for are present in this tweet
		line_words = set(x.lower() for x in re.split("\s+", line.strip()))
		inter = line_words.intersection(words_set)

		# once we have found n tweets containing the word w, we remove the
		# word w from our search list
		to_remove = set(w for w in inter if words_count[w] >= n)
		words_set -= to_remove

		# case where we output the found tweet: words which count is < n were found in the tweet
		if inter and not to_remove:
			if raw_json:
				out_stream.write(json.dumps(tw) + "\n")
				found_tweets.append(tw)
			else:
				out_stream.write(line)
				found_tweets.append(line)
			count += 1
			for w in inter:
				words_count[w] += 1
		break_cond = not each_word_n or not words_set
		if count >= n and break_cond:
			break
	return found_tweets

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("n", type=int)
	parser.add_argument("words_file", type=str)
	parser.add_argument("--raw-json", "--json", dest='raw_json', action='store_true')
	parser.set_defaults(raw_json=False)
	args = parser.parse_args()

	get_tweets_containing(args.n, args.words_file, raw_json=args.raw_json)