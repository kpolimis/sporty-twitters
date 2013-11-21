import nltk
import argparse
import features
import pickle
import json
import sys
from nltk.classify.util import accuracy
from nltk import metrics
import collections

# Initialize the args parser
parser = argparse.ArgumentParser(description='Test a classifier over a set of data.')

parser.add_argument('-c', type=str, help='file containing the classifier', metavar="classifier-file", required=True)
parser.add_argument('-t', type=str, help='file containing the testing data in nltk format', metavar="testing-data")
parser.add_argument('-o', type=str, help='file to output the obtained metrics', metavar='output-file', default=None)
parser.add_argument('-cutoff', type=int, help='value that indicates the quantity of features to keep (default: 3000)', metavar='cutoff-value', default=3000)
parser.add_argument('-bigrams', choices=['yes', 'no'], help='flag put to yes if you want to use bigrams in your classifier, no otherwise', metavar='bigram-boolean', default='no')
parser.add_argument('-split', type=float, help='float between 0 and 1 indicating the split of data between unigrams and bigrams. For example, if split is equal to 0.75, then you will get 75 percent of unigrams and 25 percent of bigrams', metavar='split-value', default=0.9)

def precision_recall_fmeasures(classifier, testfeats):
	refsets = collections.defaultdict(set)
	testsets = collections.defaultdict(set)
	for i, (feats, label) in enumerate(testfeats):
		refsets[label].add(i)
		observed = classifier.classify(feats)
		testsets[observed].add(i)
	precisions = {}
	recalls = {}
	f_measures = {}
	for label in classifier.labels():
		precisions[label] = metrics.precision(refsets[label],
			testsets[label])
		recalls[label] = metrics.recall(refsets[label], testsets[label])
		f_measures[label] = metrics.f_measure(refsets[label], testsets[label])
	return precisions, recalls, f_measures

def analyze_classifier(input_file, testing_data, output_file=None, cutoff=3000, bigrams='no', split=0.9):
	tweets = json.load(open(testing_data))
	use_bigrams = bigrams == 'yes'

	use_stdout = output_file == None

	def extract_features(document):
		if use_bigrams:
			document = document + nltk.bigrams(document)
		return {w : True for w in filter(lambda x : x in document, word_features)}

	word_features = features.tweets2features(tweets, use_bigrams, cutoff, split)
	testing_set = nltk.classify.apply_features(extract_features, tweets)

	with open(input_file) as f:
		classifier = pickle.load(f)

	acc = accuracy(classifier,testing_set)
	precisions, recalls, f_measures = precision_recall_fmeasures(classifier, testing_set)

	analyze = {'accuracy':acc}
	for label in classifier.labels():
		analyze[label] = {'precision': precisions[label], 'recall': recalls[label], 'f_measure': f_measures[label]}

	if use_stdout:
		sys.stdout.write(json.dumps(analyze))
	else:
		with open(output_file, "w") as f:
			f.write(json.dumps(analyze))

	print "\n",classifier.show_most_informative_features(30)

if __name__ == "__main__":
	args = parser.parse_args()
	analyze_classifier(args.c, args.t, args.o, args.cutoff, args.bigrams, args.split)