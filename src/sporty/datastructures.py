import json
import os
from collections import defaultdict
import re

class Tweets():
    """
    Manage a list of tweets loaded either from a file (in lazy mode) or from a list.
    """
    def __init__(self, tw_in=None, mode='a+'):
        self.index = 0
        self._load(tw_in, mode)

    def _load(self, tw_in=None, mode='a+'):
        if tw_in == None:
            self.tweets = []
            self.lazy = False
        elif type(tw_in) == list:
            self.tweets = tw_in
            self.lazy = False
        elif type(tw_in) == file:
            self.tweets = tw_in
            self.lazy = True
        elif type(tw_in) == str:
            self.tweets = open(tw_in, mode)
            self.lazy = True

    def __iter__(self):
        return self

    def next(self):
        if self.lazy:
            line = self.tweets.readline()
            if line:
                data = json.loads(line.strip())
            else:
                raise StopIteration
        else:
            try:
                data = self.tweets[self.index]
            except IndexError:
                raise StopIteration
            self.index += 1
        return data

    def tolist(self):
        if type(self.tweets) == list:
            return self.tweets
        else:
            tweets_list = []
            if sys.stdout != self.tweets:
                self.tweets.seek(0)
                for line in self.tweets:
                    tweets_list.append(json.loads(line.strip))
                return tweets_list

    def append(self, tw):
        if self.lazy:
            if self.tweets != sys.stdout:
                self.tweets.seek(0,os.SEEK_END)
            if type(tw) == dict:
                self.tweets.write(json.dumps(tw) + "\n")
            elif type(tw) == str:
                self.tweets.write(tw + "\n")
            self.tweets.flush()
        else:
            self.tweets.append(tw)

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
        if type(self.poms_file) == str:
            poms_file = open(self.poms_file)
        elif type(self.poms_file) == file:
            poms_file = self.poms_file
        else:
            raise Exception("Unsupported type for poms file.")
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
        if not self.input_file:
            return
        if type(self.input_file) == str:
            input_file = open(self.input_file)
        elif type(self.input_file) == file:
            input_file = self.input_file
        else:
            raise Exception("Unsupported type for input file.")
        for line in input_file:
            self.words.append(line.strip())

    def tolist(self):
        return self.words
