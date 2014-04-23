import argparse
import sys
import re
from collections import defaultdict
import json

def get_tweets_containing(n, words_file, each_word_n=True, in_stream=sys.stdin, out_stream=sys.stdout):
	words_set = set()
	words_count = defaultdict(int)

	with open(words_file, "r") as f:
		for line in f:
			w = line[:-1]
			words_set.add(w)
			words_count[w] = 0
	count = 0
	total = 0

	for line in in_stream:
		total += 1

		# get the tweet and check that words we look for are present in this tweet
		line_words = set(x.lower() for x in re.split("\s+", line[:-1]))
		inter = line_words.intersection(words_set)

		to_remove = set(w for w in inter if words_count[w] >= n)
		words_set -= to_remove

		if inter and not to_remove:
			out_stream.write(line)
			count += 1
			for w in inter:
				words_count[w] += 1
		break_cond = not each_word_n or not words_set
		if count >= n and break_cond:
			break
	sys.stderr.write(str(total) + "\n")
	sys.stderr.write(str(json.dumps(words_count, sort_keys=True, indent=4, separators=(',', ': '))))

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("n", type=int)
	parser.add_argument("words_file", type=str)
	args = parser.parse_args()

	get_tweets_containing(args.n, args.words_file)