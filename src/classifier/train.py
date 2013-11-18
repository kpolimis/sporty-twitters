import argparse
import nltk
import time
import pickle
import json
import features
from nltk.classify import DecisionTreeClassifier
from nltk.classify import MaxentClassifier

# Initialize the args parser
parser = argparse.ArgumentParser(description='Train a classifier over tweets from sentiment140 using nltk.')

parser.add_argument('-i', type=str, help='tweets file containing the training data', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the classifier', metavar="output-file", required=True)
parser.add_argument('-type', choices=['bayes', 'dtree', 'maxent'], help='define the type of classifier that you want to train amongst three possibilities : a Naive Bayes classifier (bayes), a decision tree classifier (dtree), or a MaxEntropy classifier (maxent)', required=True)

def extract_features(document):
	return {w : True for w in filter(lambda x : x in document, word_features)}

if __name__ == "__main__":
	args = parser.parse_args()
	
	tweets = json.load(open(args.i))
	word_features = features.tweets2features(tweets)
	training_set = nltk.classify.apply_features(extract_features, tweets)

	start_time = time.time()
	print "Start training classifier (" + args.type + ") on training set of size " + str(len(training_set))

	if args.type == 'bayes':
		classifier = nltk.NaiveBayesClassifier.train(training_set)
	elif args.type == 'dtree':
		classifier = DecisionTreeClassifier.train(training_set,binary=True, entropy_cutoff=0.8, depth_cutoff=5, support_cutoff=30)
	elif args.type == 'maxent':
		classifier = MaxentClassifier.train(training_set, algorithm='iis', trace=0, max_iter=1, min_lldelta=0.5)

	print "Training time: ", time.time() - start_time, "seconds"

	with open(args.o, "w") as f:
		pickle.dump(classifier,f)
	#print classifier.show_most_informative_features(50)