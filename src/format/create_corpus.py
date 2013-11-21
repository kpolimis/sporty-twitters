import argparse
import json
from ..utils.ProgressBar import ProgressBar
from ..utils.line_count import line_count
from filter import filter_contains
from clean_corpus import clean_tweets
import os
import os.path
import sys

# Initialize the args parser
parser = argparse.ArgumentParser(description='Create a corpus from a directory containing one folder per twitter user. Output one json file containing for each user : his uid, the number of tweets he posted and the features of the tweets.')

parser.add_argument('-id', type=str, help='input directory', metavar="input-directory", required=True)
parser.add_argument('-o', type=str, help='output file', metavar="output-directory", default='sys.stdout')
parser.add_argument('-kw', type=str, help='file containing the keywords used to filter tweets. tweets that contain those keywords will be removed from the corpus', metavar='keywords-file', required=True)
parser.add_argument('-sw', type=str, help='file containing the stopwords to delete from tweets', metavar='stopwords-file', required=True)

def create_corpus(input_dir, kw, sw, output_file=sys.stdout):
	uids = [o for o in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir,o))]
	output = {}

	bar = ProgressBar(30)
	i = 0.
	size = float(len(uids))

	for u in uids:
		i += 1.
		user = {'nbtweets': None, 'tweets': None}
		tweets_path = input_dir + "/" + u + "/tweets"

		tweets = filter_contains(tweets_path, kw, output=os.devnull, rm=True)
		tweets = clean_tweets(tweets, sw, rmurl='yes', output=os.devnull)

		user['tweets'] = tweets
		user['nbtweets'] = len(tweets)
		if len(tweets) > 0:
			output[u] = user

		bar.update(i/size)

	with open(output_file, "w") as f:
		f.write(json.dumps(output))


if "__main__" == __name__:
	args = parser.parse_args()
	create_corpus(args.id, args.kw, args.sw, args.o)
	#os.path.join(args.id,o)
	

