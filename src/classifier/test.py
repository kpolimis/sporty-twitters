import nltk
import argparse
import features
import pickle
import json
from nltk.classify.util import accuracy

# Initialize the args parser
parser = argparse.ArgumentParser(description='Test a classifier over a set of data.')

parser.add_argument('-c', type=str, help='file containing the classifier', metavar="classifier-file", required=True)
parser.add_argument('-t', type=str, help='file containing the testing data in nltk format', metavar="testing-data")

def extract_features(document):
	return {w : True for w in filter(lambda x : x in document, word_features)}

if __name__ == "__main__":
	args = parser.parse_args()

	tweets = json.load(open(args.t))
	word_features = features.tweets2features(tweets)
	testing_set = nltk.classify.apply_features(extract_features, tweets)

	with open(args.c) as f:
		classifier = pickle.load(f)

	acc = accuracy(classifier,testing_set)
	print "Accuracy: ", acc