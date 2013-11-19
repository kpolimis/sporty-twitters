import sys 
import argparse
import json
from ProgressBar import ProgressBar
import re

# Initialize the args parser
parser = argparse.ArgumentParser(description='Clean a corpus from a list of words.')

parser.add_argument('-k', type=str, help='json file containing the keywords to remove', metavar="keyword-file", required=True)
parser.add_argument('-i', type=str, help='file containing the tweets that need to be filtered', metavar="input-file", required=True)
parser.add_argument('-o', type=str, help='file to output the filtered tweets', metavar="output-file")
parser.add_argument('-rmurl', type=str, choices=['yes','no'], help='flag that indicates if the URLs need to be removed from the corpus', default='no')

def clean_corpus(input_file, keywords_file, output=None, rmurl=None):

    in_std_output = output == None # True if we need to print in stdout, False otherwise

    if not in_std_output:
        out = open(output, 'w')

    result=""
    keywords = json.load(open(keywords_file))

    # initialize progress bar    
    nb_lines = 0
    with open(input_file) as f:
        for line in f:
            nb_lines += 1
            pass
    lineno = 0
    bar = ProgressBar(30)

    with open(input_file) as f:
        for line in f:
            lineno += 1 # update progress bar variable

            # remove URLs if asked by user
            if rmurl == 'yes':
                line = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?]))''', '', line)

            # remove undesired words
            words = re.findall(r'\w+', line.lower(),flags = re.UNICODE) 
            important_words = filter(lambda w : w not in keywords, words)

            # output the obtained words in JSON format
            if important_words:
                if in_std_output:
                    sys.stdout.write(json.dumps(important_words) + "\n")
                    sys.stdout.flush()
                else:
                    out.write(json.dumps(important_words) + "\n")

            # update the progress bar view
            bar.update(float(lineno)/float(nb_lines))

    if not in_std_output:
        out.close()

    return result

if  __name__ == "__main__":
    # parse arguments
    args = parser.parse_args()
    clean_corpus(args.i, args.k, args.o, args.rmurl)
