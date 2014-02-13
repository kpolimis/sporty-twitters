#! /usr/bin/env python
import argparse
import sys
import re
import string

parser = argparse.ArgumentParser()
parser.add_argument("stopwords", type=str)

"""Remove stopwords (from a given list), URLs, and punctuation."""
if __name__ == "__main__":
    args = parser.parse_args()
    # load stopwords file
    sw_file = open(args.stopwords, "r");
    sw = set(x[:-1] for x in sw_file)

    urlregex = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?]))''')
    # read in stdin
    for line in sys.stdin:
        # put the line in lower case
        line = line.lower()

        # remove URLs
        line = re.sub(urlregex, '', line)
        
        # remove punctuation
        line = line.translate(string.maketrans("",""), string.punctuation)

        # remove stopwords
        word = set(re.split("[\s]+", line))
        word = [x for x in word if x not in sw and x != '']
        # write result in stdout
        sys.stdout.write(" ".join(word) + "\n")
        sys.stdout.flush()
