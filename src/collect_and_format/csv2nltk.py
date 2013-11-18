import csv
import json
import argparse
import re
from ProgressBar import ProgressBar
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

# Initialize the args parser
parser = argparse.ArgumentParser(description='Filter the tweets stored in a file given a list of keywords.')

parser.add_argument('-i', type=str, help='CSV file containing the training data', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the training data in nltk format', metavar="output-file")
parser.add_argument('-k', type=str, help='file containing the words to remove (eg. list of stopwords)', metavar='keywords-file')
parser.add_argument('-bigrams', choices=['yes','no'], help='flag which value is yes if you want to user bigrams in your features', default='no')

def line2feat(line, keywords, bigrams = False):
	"""Transform a entry from the cvs file into a vector of features"""
	text = line[5]
	label = line[0]
	text = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?]))''', '', text)
	words = re.findall(r'\w+', text.lower())
	important_words = filter(lambda w : w not in keywords and len(str(w)) > 2, words)

	if bigrams:
		score_fn=BigramAssocMeasures.chi_sq
		n=200
		bigram_finder = BigramCollocationFinder.from_words(important_words)
		bigrams = bigram_finder.nbest(score_fn, n)
		important_words += bigrams

	feature = (important_words, label)
	return feature

def csv2nltk(input_file, output_file = None, keywords_file = None, bigrams = False):
	"""Function parsing a csv file from Sentiment140 dataset and transform them in the format to be used with a nltk classifier."""

	in_std_output = output_file == None # True if we need to print in stdout, False otherwise

	keywords = []	
	if keywords_file != None:
		keywords = json.load(open(keywords_file))
	
	# Setting up progress bar
	nb_lines = 0
	with open(input_file) as f:
		for line in f:
			nb_lines += 1
			pass
	lineno = 0
	bar = ProgressBar(30)
	with open(input_file, 'rb') as csvfile:
	    reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	    features = []

	    for line in reader:
	    	lineno += 1
	    	bar.update(float(lineno)/float(nb_lines))
	    	features.append(line2feat(line, keywords, bigrams))

	if in_std_output:
		print json.dumps(features)
	else:
		with open(output_file, "w") as f:
			f.write(json.dumps(features))
	return features

if __name__ == "__main__":
    # parse arguments
    args = parser.parse_args()
    csv2nltk(args.i, args.o, args.k, args.bigrams == 'yes')

