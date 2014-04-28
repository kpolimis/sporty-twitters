import json
import argparse
import sys
import StringIO
import utils.clean_corpus as cc
#from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import preprocessing

def getVectorizer(tweets=sys.stdin, keep_rt=True):
	"""Return a scaled Vectorizer built from labeled tweets."""
	corpus = []
	labels = []
	for line in tweets:
		# load the raw json and extract the text
		tw = json.loads(line)
		# filter on retweets
		if tw['retweeted'] and not keep_rt:
			continue
		text = tw['text']
		corpus.append(text)
		labels.append(int(tw['label']))

	vectorizer = CountVectorizer(min_df=1, analyzer='word', preprocessor=cc.preprocess, stop_words='english')
	X = vectorizer.fit_transform(corpus)

	scaler = preprocessing.StandardScaler(with_mean=False).fit(X)
	scaled_X = scaler.transform(X)

	return scaled_X

def tweet2features(tw, vocabulary):
	features = []
	
	# load the raw json
	tw = json.loads(tw)

	# create variables to use strings as files
	inpstr = StringIO.StringIO()
	outstr = StringIO.StringIO()

	return features

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--no-rt", "--no-retweet", dest="nort", action="store_false")
	args = parser.parse_args()
	X = getVectorizer(keep_rt=args.nort)
	print X
