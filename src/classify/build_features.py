import json
import argparse
import sys
import StringIO
import utils.clean_corpus as cc
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import preprocessing
from collections import defaultdict

def build_features(tweets=sys.stdin, stopwords=[], keep_rt=True, label=False):
	"""Returns a scaled Vectorizer built from tweets. If the label flag is true, then it also returns the list of labels."""
	corpus = []
	labels = []

	for line in tweets:
		# load the raw json and extract the text
		tw = json.loads(line)
		# filter on retweets
		if tw['retweeted'] and not keep_rt:
			continue

		# extract the text features
		text = tw['text']
		terms = cc.tokenize(cc.preprocess(text), stopwords)
		d = defaultdict(int)
		for t in terms:
			d[t] += 1	

		# extract the other features (retweet, mentions, hashtags, etc)
		entities = tw['entities']
		if len(entities["user_mentions"]) != 0:
			d["USER_MENTIONS_NB"] = 1
		if len(entities["hashtags"]) != 0:
			d["HASHTAGS_NB"] = 1
		if len(text) < 50:
			d["TW_SMALL"] = 1
		elif len(text) < 100:
			d["TW_MEDIUM"] = 1
		else:
			d["TW_LARGE"] = 1

		# append to the corpus
		corpus.append(d)
		if label:
			labels.append(int(tw['label']))

	return corpus, labels

def get_X(corpus, labels=[]):
	# use the DictVectorizer method to fit the data, avoid sparse vectorizer in
	# order to be able to scale it.
	vectorizer = DictVectorizer(sparse=False)
	X = vectorizer.fit_transform(corpus)
	X = preprocessing.scale(X)
	return X, labels

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--no-rt", "--no-retweet", dest="nort", action="store_false")
	parser.add_argument("--labeled", action="store_true")
	parser.add_argument("--stopwords", "-sw", type=str, default='')
	args = parser.parse_args()

	if args.stopwords:
		with open(args.stopwords, "r") as sw_file:
			sw = set(x.strip() for x in sw_file)

	corpus, labels = build_features(stopwords=sw, keep_rt=args.nort, label=args.labeled)
	get_X(corpus, labels)