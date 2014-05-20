import re
import os.path
from collections import defaultdict
import sys
import string
import codecs
import json

class Cleaner():
    """docstring for Cleaner"""
    def __init__(self, stopwords=None, rm_urls=True, rm_mentions=True, rm_punctuation=True, rm_unicode=True, raw_json=False, json_out=False):
        self.stopwords = stopwords
        self.url_regex = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`()\[\]{};:'"<>?]))''')
        self.mentions_regex = re.compile(r'''(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)''')
        self.unicode_regex = re.compile(r'''[^\x00-\x7F]''')
        self.stem_regex = re.compile(r'''([a-zA-Z])\1{2,}''', re.DOTALL)
        self.exclude = set(string.punctuation)
        self.rm_urls = rm_urls
        self.rm_mentions = rm_mentions
        self.rm_punctuation = rm_punctuation
        self.rm_unicode = rm_unicode
        self.raw_json = raw_json
        self.json_out = json_out
        self.cleanCorpus = []

    def preprocess(self,line):
        """
        Processes a string in order to remove urls, mentions, unicode characters,
        and punctuation. It also replaces characters that are repeated more than
        three times by two of the same character.
        """
        line = line.lower()

        if self.rm_mentions:
            line = re.sub(self.mentions_regex, '', line) 

        if self.rm_urls:
            line = re.sub(self.url_regex, '', line) 
        
        if self.rm_unicode:
            line = re.sub(self.unicode_regex, '', line)

        if self.rm_punctuation:
            line = ''.join(c for c in line if c not in self.exclude)

        line = re.sub(self.stem_regex, r'\1\1', line)

        return line

    def tokenize(self, line):
        """Tokenize a string and remove given stopwords from the final list of words"""
        words = re.split("[\s]+", line)
        words = [x for x in words if x] # remove starting space
        if self.stopwords:
            # remove stopwords
            words = [x for x in words if x not in self.stopwords]
        return words

    def clean(self, corpus):
        """Clean a corpus given as an iterable by removing stopwords, URLs, mentions, and punctuation."""
        for line in corpus:
            if type(line) == str:
                if self.raw_json:
                    tw = json.loads(line.strip())
                    line = tw['text']
            elif type(line) == dict:
                tw = line
                line = tw['text']
            line = self.preprocess(line)
            words = self.tokenize(line)
            line = " ".join(words)

            if line:
                if self.json_out:
                    tw['text'] = line
                    line = json.dumps(tw)
                self.cleanCorpus.append(line)
        return self.cleanCorpus

class POMS():
    """
    Tool to load the POMS vocabulary into several dictionaries.
    """
    def __init__(self, poms_file):
        self.poms_file = poms_file
        self.categories = defaultdict(list)
        self.words = {}
        self.load()
        
    def load(self):
        with open(os.path.abspath(self.poms_file), "r") as poms_file:
            for line in poms_file:
                fields = re.split("\s+", line.strip())
                self.categories[fields[0]].append(fields[1])
                self.words[fields[1]] = fields[0]

class LSF():
    """
    Tool to load a Line-Separated File. This kind of file contains a list of words, one word on 
    each line.
    """
    def __init__(self, input_file):
        self.input_file = input_file
        self.words = []
        self.load()
    
    def load(self):
        with open(os.path.abspath(self.input_file), "r") as input_file:
            for line in input_file:
                self.words.append(line.strip())

    def tolist():
        return words