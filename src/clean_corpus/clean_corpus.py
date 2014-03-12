#! /usr/bin/env python
import argparse
import sys
import re
import string

parser = argparse.ArgumentParser()

parser.add_argument("stopwords", type=str, default="None", nargs='?')
parser.add_argument("--keep-mentions", dest='rm_mentions', action='store_false')
parser.add_argument("--keep-urls", dest='rm_urls', action='store_false')
parser.add_argument("--keep-punctuation", dest='rm_punctuation', action='store_false')

parser.set_defaults(rm_mentions=True, rm_stopwords=True, rm_urls=True, rm_punctuation=True)

"""Remove given stopwords, URLs, and punctuation from a corpus of raw tweets."""
if __name__ == "__main__":
    args = parser.parse_args()

    if args.stopwords != 'None':
        # load stopwords file
        sw_file = open(args.stopwords, "r");
        sw = set(x[:-1] for x in sw_file)
        
    if args.rm_urls:
        urlregex = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`()\[\]{};:'"<>?]))''')

    if args.rm_mentions:
        mentionsregex = re.compile(r'''(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)''')

    for line in sys.stdin:
        # put the line in lower case
        line = line.lower()

        if args.rm_mentions:
            # remove mentions
            line = re.sub(mentionsregex, '', line) 

        if args.rm_urls:
            # remove URLs
            line = re.sub(urlregex, '', line) 
        
        if args.rm_punctuation:
            # remove punctuation
            line = line.translate(string.maketrans("",""), string.punctuation)

        word = re.split("[\s]+", line)
        word = [x for x in word if x] # remove starting space
        if args.stopwords != 'None':
            # remove stopwords
            word = [x for x in word if x not in sw]
        line = " ".join(word) + "\n"

        # write result in stdout
        if line:
            sys.stdout.write(line)
            sys.stdout.flush()
