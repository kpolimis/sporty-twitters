import sys 
import argparse
import json
import re
import os
from ..utils.ProgressBar import ProgressBar
from ..utils.line_count import line_count

# Initialize the args parser
parser = argparse.ArgumentParser(description='Clean a corpus from a list of words.')

parser.add_argument('-k', type=str, help='json file containing the keywords to remove', metavar="keyword-file", required=True)
parser.add_argument('-i', type=str, help='file containing the tweets that need to be filtered', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the filtered tweets', metavar="output-file")
parser.add_argument('-rmurl', type=str, choices=['yes','no'], help='flag that indicates if the URLs need to be removed from the corpus', default='no')

def clean_corpus(input_file, keywords_file, output=None, rmurl=None):
    tweets = json.load(open(input_file))
    return clean_tweets(tweets, keywords_file, output, rmurl)

def clean_tweets(tweets, keywords_file, output=None, rmurl=None):
    keywords = json.load(open(keywords_file))
    result = []

    in_std_output = output == None # True if we need to print in stdout, False otherwise
    devnull = output == os.devnull

    # initialize progress bar    
    nb_lines = len(tweets)
    lineno = 0
    if devnull:
        bar = ProgressBar(30, output=os.devnull)
    else:
        bar = ProgressBar(30)

    for tweet in tweets:
        lineno += 1 # update progress bar variable

        # remove URLs if asked by user
        if rmurl == 'yes':
            tweet = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?]))''', '', tweet)

        # remove undesired words
        words = re.findall(r'\w+', tweet.lower(),flags = re.UNICODE) 
        important_words = filter(lambda w : w not in keywords, words)

        # store the obtained words in result variable
        if important_words:
            result.append(important_words)

        # update the progress bar view
        bar.update(float(lineno)/float(nb_lines))

    if not in_std_output:
        with open(output, "w") as f:
            f.write(json.dumps(result))
    else:
        sys.stdout.write(json.dumps(result))

    return result

if  __name__ == "__main__":
    # parse arguments
    args = parser.parse_args()
    clean_corpus(args.i, args.k, args.o, args.rmurl)
