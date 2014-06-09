import json
import os
from collections import defaultdict
import re
import sys


class Tweets(object):
    """
    Manages a list of tweets loaded from a file (possibly empty) or a list.
    Makes it possible to iterate over tweets using a unique structure when
    tweets are in a Python list or stored on disk in a file.
    """
    def __init__(self, tw_in=None, mode='a+'):
        "Initializes an instance by loading file/list."
        super(Tweets, self).__init__()
        self.index = 0
        self._load(tw_in, mode)

    def _load(self, tw_in=None, mode='a+'):
        "Switches on the possible types of tw_in to correctly load the tweets."
        if not tw_in:  # if no tw_in, creates an empty list
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
        else:
            raise Exception("Unsupported type for tweets source: " + str(type(tw_in)))

    def __iter__(self):
        return self

    def next(self):
        """
        Returns the next tweet.
        """
        # case when tweets are stored on disk
        if self.lazy:
            line = self.tweets.readline()
            if line:
                data = json.loads(line.strip())
            else:
                raise StopIteration
        # case when tweets are stored in a Python list
        else:
            try:
                data = self.tweets[self.index]
            except IndexError:
                raise StopIteration
            self.index += 1
        return data

    def tolist(self):
        """
        Returns a list of tweets. If the tweets are stored on disk, it loads all the tweets thus
        making the lazy loading mode useless.
        """
        if type(self.tweets) == list:
            return self.tweets
        else:
            tweets_list = []
            if sys.stdout != self.tweets:
                self.tweets.seek(0)
                for line in self.tweets:
                    tweets_list.append(json.loads(line.strip()))
                return tweets_list

    def append(self, tw):
        """
        Appends a given tweet to the list of tweets. If the tweets are stored in a file on disk,
        then the appended tweet is written at the end of the file.
        """
        if self.lazy:
            self.tweets.seek(0, os.SEEK_END)
            if type(tw) == dict:
                self.tweets.write(json.dumps(tw) + "\n")
            elif type(tw) == str:
                self.tweets.write(tw + "\n")
            self.tweets.flush()
        else:
            self.tweets.append(tw)


class TSV(object):
    """
    Tool to load a TSV file into several dictionaries. It is used in this project to load the POMS
    vocabulary and the emoticons. Each word of these vocabularies belong to a category. This data
    structure give access to a dictionary 'keys' that maps a category to a list of words belonging
    to this category, and a dictionary 'values' that maps each word in the vocabulary to the
    category it belongs to.
    """
    def __init__(self, tsv_file):
        """
        Initializes an TSV instance by loading a TSV file.
        """
        super(TSV, self).__init__()
        self.tsv_file = tsv_file
        self.keys = defaultdict(list)
        self.values = {}
        self.load()

    def load(self):
        """
        Loads the TSV file in the dictionaries.
        """
        if type(self.tsv_file) == str:
            tsv_file = open(self.tsv_file)
        elif type(self.tsv_file) == file:
            tsv_file = self.tsv_file
        else:
            raise Exception("Unsupported type for TSV file.")
        for line in tsv_file:
            fields = re.split("\s+", line.strip())
            if len(fields) > 1:
                self.keys[fields[0]].append(fields[1])
                self.values[fields[1]] = fields[0]


class LSF(object):
    """
    Tool to load a Line-Separated File. This kind of file contains a list of words, one word on
    each line.
    """
    def __init__(self, input_file):
        """
        Initializes the LSF instance by loading the input file.
        """
        super(LSF, self).__init__()
        self.input_file = input_file
        self.words = []
        self.load()

    def load(self):
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
