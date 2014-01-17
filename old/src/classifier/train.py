import argparse
import nltk
import time
import pickle
import json
import features
from nltk.classify import MaxentClassifier

# Initialize the args parser
parser = argparse.ArgumentParser(description='Train a classifier over tweets from sentiment140 using nltk.')

parser.add_argument('-i', type=str, help='tweets file containing the training data', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the classifier', metavar="output-file", required=True)
parser.add_argument('-cutoff', type=int, help='value that indicates the quantity of features to keep (default: 3000)', default=3000)
parser.add_argument('-bigrams', choices=['yes', 'no'], help='flag put to yes if you want to use bigrams in your classifier, no otherwise', default='no')
parser.add_argument('-split', type=float, help='float between 0 and 1 indicating the split of data between unigrams and bigrams. For example, if split is equal to 0.75, then you will get 75 percent of unigrams and 25 percent of bigrams', default=0.9)
parser.add_argument('-type', choices=['nb', 'me'], help='type of the classifier: Naive Bayes (nb) or MaxEnt (me)', default='nb')

if __name__ == "__main__":
	args = parser.parse_args()
	
	tweets = json.load(open(args.i))
	use_bigrams = args.bigrams == 'yes'

	def extract_features(document):
		if use_bigrams:
			document = document + nltk.bigrams(document)
		return {w : True for w in filter(lambda x : x in document, word_features)}

	word_features = features.tweets2features(tweets, bigrams=use_bigrams, cutoff=args.cutoff, split=args.split)
	training_set = nltk.classify.apply_features(extract_features, tweets)

	start_time = time.time()
	print "Start training classifier"

	if args.type == 'nb':
		classifier = nltk.NaiveBayesClassifier.train(training_set)
	elif args.type == 'me':
		#classifier = MaxentClassifier.train(training_set, algorithm='iis', trace=0, max_iter=10, min_lldelta=0.1)
		classifier = MaxentClassifier.train(training_set, algorithm='iis', trace=0, max_iter=1, min_lldelta=0.5)
	elif args.type == 'dt':
		classifier = DecisionTreeClassifier.train(training_set, entropy_cutoff=0.5, depth_cutoff=12, support_cutoff=20)
		#classifier = DecisionTreeClassifier.train(training_set,binary=True, entropy_cutoff=0.9, depth_cutoff=6, support_cutoff=12)

	print "Training time: ", time.time() - start_time, "seconds"

	with open(args.o, "w") as f:
		pickle.dump(classifier,f)
	#print classifier.show_most_informative_features(50)