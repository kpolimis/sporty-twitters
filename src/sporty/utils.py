import re
import os.path
from collections import defaultdict
from datastructures import *
import sys
import string
import codecs
import json
from TwitterAPI import TwitterAPI

class Cleaner():
    """Cleaner of corpus"""
    def __init__(self, stopwords=None, emoticons=None, rm_urls=True, rm_mentions=True, rm_punctuation=True, rm_unicode=True):
        self.stopwords = LSF(stopwords).tolist()
        self.emoticons = TSV(emoticons).keys
        self.url_regex = re.compile(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`()\[\]{};:'"<>?]))''')
        self.mentions_regex = re.compile(r'''(?<=^|(?<=[^a-zA-Z0-9-_\.]))@([A-Za-z]+[A-Za-z0-9]+)''')
        self.unicode_regex = re.compile(r'''[^\x00-\x7F]''')
        self.stem_regex = re.compile(r'''([a-zA-Z])\1{2,}''', re.DOTALL)
        self.exclude = set(string.punctuation)
        self.rm_urls = rm_urls
        self.rm_mentions = rm_mentions
        self.rm_punctuation = rm_punctuation
        self.rm_unicode = rm_unicode
        self.cleaned_corpus = []

    def preprocess(self,text):
        """
        Processes a string in order to remove urls, mentions, unicode characters,
        and punctuation. It also replaces characters that are repeated more than
        three times by two of the same character and replaces emoticons with tags.
        """
        text = text.lower()

        if self.rm_mentions:
            text = re.sub(self.mentions_regex, '', text) 

        if self.rm_urls:
            text = re.sub(self.url_regex, '', text) 
        
        if self.rm_unicode:
            text = re.sub(self.unicode_regex, '', text)

        # replace emoticons
        if self.emoticons:
            for emo in self.emoticons:
                for entry in self.emoticons[emo]:
                    text = string.replace(text, entry, emo)

        if self.rm_punctuation:
            text = ''.join(c for c in text if c not in self.exclude)

        text = re.sub(self.stem_regex, r'\1\1', text)

        return text

    def tokenize(self, text):
        """Tokenize a string and remove given stopwords from the final list of words"""
        words = re.split("[\s]+", text)
        words = [x for x in words if x] # remove starting space
        if self.stopwords:
            # remove stopwords
            words = [x for x in words if x not in self.stopwords]
        return words

    def _clean(self, tw):
        text = tw['text']
        text = self.preprocess(text)
        words = self.tokenize(text)
        text = " ".join(words)

        if text:
            tw['text'] = text
        return tw

    def clean(self, corpus):
        """Clean a corpus given as an iterable by removing stopwords, URLs, mentions, and punctuation."""
        self.cleaned_corpus = (self._clean(tw) for tw in corpus)
        return self.cleaned_corpus

class TwitterAPIUser(object):
    """TwitterAPIUser allows access to the Twitter API."""
    def __init__(self, settings_file=None):
        super(TwitterAPIUser, self).__init__()
        self.settings_file = settings_file
        self.twitterapi = None
        self.settings = None
        self.authenticate()

    def authenticate(self):
        if self.settings_file:
            if type(self.settings_file) == str:
                settings_f = open(self.settings_file)
            elif type(self.settings_file) == file:
                settings_f = self.settings_file
            else:
                raise Exception("Unsupported type for settings file.")
            self.settings = json.load(settings_f)
            consumer_key = self.settings['consumer_key']
            consumer_secret = self.settings['consumer_secret']
            access_token = self.settings['access_token']
            access_token_secret = self.settings['access_token_secret']
            self.twitterapi = TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)

    def getStatusStream(self, tracked_words, lang, locations):
        if not self.settings_file:
            raise Exception("TwitterAPI not authenticated. Please call the constructor using a settings file if you want to collect tweets.")

        req_options = dict()
        req_options['track'] = ",".join(tracked_words)
        req_options['language'] = ",".join(lang)
        if locations:
            req_options['locations'] = locations

        r = self.twitterapi.request('statuses/filter', req_options)
        return r

    def getUserStream(self, user_id, since_id=None, max_id=None):
        print "call getUserStream"
        if not self.settings_file:
            raise Exception("TwitterAPI not authenticated. Please call the constructor using a settings file if you want to collect tweets.")

        req_options = dict()
        req_options['user_id'] = user_id
        req_options['count'] = 200
        if since_id:
            req_options['since_id'] = since_id
        if max_id:
            req_options['max_id'] = max_id

        r = self.twitterapi.request('statuses/user_timeline', req_options)
        return r
