#! /usr/bin/env python
import argparse
import sys
import re
import string
import codecs
import json

urlregex = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`()\[\]{};:'"<>?]))''')
mentionsregex = re.compile(r'''(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)''')
exclude = set(string.punctuation)

def preprocess(line, rm_urls=True, rm_mentions=True, rm_punctuation=True, raw_json=False):
    """Process a string in order to remove urls, mentions, and punctuation."""

    if raw_json:
        tw = json.loads(line)
        line = tw['text'].lower()
    else:
        line = line.lower()

    if rm_mentions:
        line = re.sub(mentionsregex, '', line) 

    if rm_urls:
        line = re.sub(urlregex, '', line) 
    
    if rm_punctuation:
        line = ''.join(c for c in line if c not in exclude)

    return line

def tokenize(line, stopwords):
    """Tokenize a string and the remove given stopwords from the final list of words"""
    word = re.split("[\s]+", line)
    word = [x for x in word if x] # remove starting space
    if stopwords:
        # remove stopwords
        word = [x for x in word if x not in stopwords]
    line = " ".join(word)
    return line

def clean(in_stream=sys.stdin, out_stream=sys.stdout, stopwords=[], rm_urls=True, rm_mentions=True, rm_punctuation=True, raw_json=False):
    """Clean a corpus given as an input stream by removing stopwords, URLs, mentions, and punctuation."""
    out_stream = codecs.getwriter('utf8')(out_stream)

    if stopwords:
        # load the stopwords from a given file
        with open(stopwords, "r") as sw_file:
            sw = set(x.strip() for x in sw_file)

    for line in in_stream:
        line = preprocess(line, rm_urls, rm_mentions, rm_punctuation, raw_json)
        line = tokenize(line, sw)

        # write result in the output stream
        if line:
            if raw_json:
                tw['text'] = line
                line = json.dumps(tw)
            out_stream.write(line + "\n")

"""Remove given stopwords, URLs, and punctuation from a corpus of raw tweets."""
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stopwords", type=str, default="None", nargs='?')
    parser.add_argument("--keep-mentions", dest='rm_mentions', action='store_false')
    parser.add_argument("--keep-urls", dest='rm_urls', action='store_false')
    parser.add_argument("--keep-punctuation", dest='rm_punctuation', action='store_false')
    parser.add_argument("--raw-json", "--json", dest='raw_json', action='store_true')
    parser.set_defaults(rm_mentions=True, rm_stopwords=True, rm_urls=True, rm_punctuation=True, raw_json=False)
    args = parser.parse_args()

    clean(sys.stdin, sys.stdout, args.stopwords, args.rm_mentions, args.rm_urls, args.rm_punctuation, args.raw_json)
