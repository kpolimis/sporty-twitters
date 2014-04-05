#! /usr/bin/env python
import argparse
import sys
import re
import string

def clean(in_stream=sys.stdin, out_stream=sys.stdout, stopwords=[], rm_urls=True, rm_mentions=True, rm_punctuation=True):
    """Clean a corpus given as an input stream by removing stopwords, URLs, mentions, and punctuation."""
    if stopwords:
        # load stopwords file
        sw_file = open(stopwords, "r");
        sw = set(x[:-1] for x in sw_file)
        
    if rm_urls:
        urlregex = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`()\[\]{};:'"<>?]))''')

    if rm_mentions:
        mentionsregex = re.compile(r'''(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)''')

    for line in in_stream:
        # put the line in lower case
        line = line.lower()

        if rm_mentions:
            # remove mentions
            line = re.sub(mentionsregex, '', line) 

        if rm_urls:
            # remove URLs
            line = re.sub(urlregex, '', line) 
        
        if rm_punctuation:
            # remove punctuation
            line = line.translate(string.maketrans("",""), string.punctuation)

        word = re.split("[\s]+", line)
        word = [x for x in word if x] # remove starting space
        if stopwords:
            # remove stopwords
            word = [x for x in word if x not in sw]
        line = " ".join(word) + "\n"

        # write result in the output stream
        if line:
            out_stream.write(line)

"""Remove given stopwords, URLs, and punctuation from a corpus of raw tweets."""
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stopwords", type=str, default="None", nargs='?')
    parser.add_argument("--keep-mentions", dest='rm_mentions', action='store_false')
    parser.add_argument("--keep-urls", dest='rm_urls', action='store_false')
    parser.add_argument("--keep-punctuation", dest='rm_punctuation', action='store_false')
    parser.set_defaults(rm_mentions=True, rm_stopwords=True, rm_urls=True, rm_punctuation=True)
    args = parser.parse_args()

    clean(sys.stdin, sys.stdout, args.stopwords, args.rm_mentions, args.rm_urls, args.rm_punctuation)