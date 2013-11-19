import argparse
import nltk
import time
import pickle
import json
import features

# Initialize the args parser
parser = argparse.ArgumentParser(description='Train a classifier over tweets from sentiment140 using nltk.')

parser.add_argument('-i', type=str, help='tweets file containing the training data', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the classifier', metavar="output-file", required=True)
parser.add_argument('-cutoff', type=int, help='value that indicates the quantity of features to keep (default: 3000)', default=3000)

def extract_features(document):
	return {w : True for w in filter(lambda x : x in document, word_features)}

if __name__ == "__main__":
	args = parser.parse_args()
	
	tweets = json.load(open(args.i))
	word_features = features.tweets2features(tweets, args.cutoff)
	training_set = nltk.classify.apply_features(extract_features, tweets)

	start_time = time.time()
	print "Start training classifier"

	classifier = nltk.NaiveBayesClassifier.train(training_set)

	print "Training time: ", time.time() - start_time, "seconds"

	with open(args.o, "w") as f:
		pickle.dump(classifier,f)
	#print classifier.show_most_informative_features(50)