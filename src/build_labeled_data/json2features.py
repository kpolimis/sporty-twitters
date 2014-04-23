import json
import argparse
import sys
import StringIO
import ..clean_corpus.clean_corpus as cc

def json2features(tw):
	features = {}
	
	# load the raw json
	tw = json.loads(tw)

	# create variables to use strings as files
	inpstr = StringIO.StringIO()
	outstr = StringIO.StringIO()

	return features

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("stopwords", type=str)
	args = parser.parse_args()
