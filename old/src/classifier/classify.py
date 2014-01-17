import json
import pickle
import nltk
import features
import argparse
import sys
from ..utils.ProgressBar import ProgressBar

# Initialize the args parser
parser = argparse.ArgumentParser(description='Classify a tweet when given a classifier.')

parser.add_argument('-i', type=str, help='file in which the corpus is stored', metavar="corpus-file", required=True)
parser.add_argument('-o', type=str, help='file in which the results will be stored', metavar="results-file", default='sys.stdout')
parser.add_argument('-d', type=str, help='directory containing the classifiers', metavar='classifiers-directory', required=True)

def extract_features(document):
	document = document + nltk.bigrams(document)
	return {w : True for w in document}

def classify_features(features):
	probs = {0:0,4:0}
	for name in classifiers:
		dist = classifiers[name].prob_classify(features)
		probs_tmp = {int(s) : dist.prob(s) for s in dist.samples()}
		probs = {int(s) : probs[int(s)]+dist.prob(s) for s in dist.samples()}
	#print  name, "\t=>\t", probs_tmp

	probs = {int(s) : probs[int(s)]/len(classifiers) for s in probs.keys()}
	return probs

def classify_tweet(tweet):
	features = extract_features(tweet.lower().split())
	print features
	return classify_features(features)

def classify_corpus(input_file, output_file):
	corpus = json.load(open(input_file))
	results = {}

	bar = ProgressBar(30)
	nbusers = float(len(corpus))
	i = 0.

	sys.stdout.write("Begin classification on corpus with " + str(len(corpus)) + " users.\n")
	sys.stdout.flush()
	for u in corpus:
		corpus_user = corpus[u]

		i += 1.
		nbtweets = corpus_user['nbtweets']
		probs = list()
		for tweet in corpus_user['tweets']:
			features = extract_features(tweet)
			probs.append(classify_features(features))
		sum_probs = reduce(lambda x, y: {0:x[0]+y[0], 4:x[4]+y[4]}, probs)
		avgprob = {p : sum_probs[p]/nbtweets for p in sum_probs}

		user = {'nbtweets':None,'avgprob':None,'probs':None}
		user['nbtweets'] = nbtweets
		user['avgprob'] = avgprob
		user['probs'] = probs
		results[u] = user
		bar.update(i/nbusers)

	with open(output_file, "w") as f:
		f.write(json.dumps(results))

	return results

if __name__ == "__main__":
	args = parser.parse_args()

	classifiers_name = ['3000-nb-unibi-r20.classifier', '3000-nb-uni-r20.classifier', '5000-nb-uni-r40.classifier']

	sys.stdout.write("Loading classifiers\n")
	sys.stdout.flush()

	classifiers = {}
	for classifier_name in classifiers_name:
		with open(args.d + classifier_name) as f:
			classifiers[classifier_name] = pickle.load(f)
	sys.stdout.write("Classifiers loaded\n")
	sys.stdout.flush()
	classify_corpus(args.i, args.o)