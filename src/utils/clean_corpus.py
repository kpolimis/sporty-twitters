#! /usr/bin/env python
import argparse
import sys
import re
import string
import codecs
import json

url_regex = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`()\[\]{};:'"<>?]))''')
mentions_regex = re.compile(r'''(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)''')
unicode_regex = re.compile(r'''[^\x00-\x7F]''')
stem_regex = re.compile(r'''([a-zA-Z])\1{2,}''', re.DOTALL)
exclude = set(string.punctuation)

def preprocess(line, rm_urls=True, rm_mentions=True, rm_punctuation=True, rm_unicode=True, raw_json=False):
    """
    Processes a string in order to remove urls, mentions, unicode characters,
    and punctuation. It also replaces characters that are repeated more than
    three times by two of the same character.
    """
    if raw_json:
        tw = json.loads(line)
        line = tw['text'].lower()
    else:
        line = line.lower()

    if rm_mentions:
        line = re.sub(mentions_regex, '', line) 

    if rm_urls:
        line = re.sub(url_regex, '', line) 
    
    if rm_unicode:
        line = re.sub(unicode_regex, '', line)

    if rm_punctuation:
        line = ''.join(c for c in line if c not in exclude)

    line = re.sub(stem_regex, r'\1\1', line)

    return line

def tokenize(line, stopwords):
    """Tokenize a string and the remove given stopwords from the final list of words"""
    words = re.split("[\s]+", line)
    words = [x for x in words if x] # remove starting space
    if stopwords:
        # remove stopwords
        words = [x for x in words if x not in stopwords]
    return words

def clean(in_stream=sys.stdin, out_stream=sys.stdout, stopwords=False, rm_urls=True, rm_mentions=True, rm_punctuation=True, rm_unicode=True, raw_json=False):
    """Clean a corpus given as an input stream by removing stopwords, URLs, mentions, and punctuation."""
    out_stream = codecs.getwriter('utf8')(out_stream)

    if stopwords:
        # load the stopwords from a given file
        with open(stopwords, "r") as sw_file:
            sw = set(x.strip() for x in sw_file)

    for line in in_stream:
        line = preprocess(line, rm_urls, rm_mentions, rm_punctuation, rm_unicode, raw_json)
        words = tokenize(line, sw)
        line = " ".join(words)

        # write result in the output stream
        if line:
            if raw_json:
                tw['text'] = line
                line = json.dumps(tw)
            out_stream.write(line + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stopwords", type=str, default="None", nargs='?')
    parser.add_argument("--keep-mentions", "-m", dest='rm_mentions', action='store_false')
    parser.add_argument("--keep-urls", "l", dest='rm_urls', action='store_false')
    parser.add_argument("--keep-punctuation", "-p", dest='rm_punctuation', action='store_false')    
    parser.add_argument("--keep-unicode", "-u", dest='rm_unicode', action='store_false')
    parser.add_argument("--raw-json", "--json", dest='raw_json', action='store_true')
    parser.set_defaults(rm_mentions=True, rm_stopwords=True, rm_urls=True, rm_punctuation=True, rm_unicode=True, raw_json=False)
    args = parser.parse_args()

    clean(sys.stdin, sys.stdout, args.stopwords, args.rm_mentions, args.rm_urls, args.rm_punctuation, args.rm_unicode, args.raw_json)
