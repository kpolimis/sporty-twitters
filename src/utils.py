import re
import os.path
from collections import defaultdict
import sys
import string
import codecs
import json

class Cleaner():
    """docstring for Cleaner"""
    def __init__(self, stopwords=None, rm_urls=True, rm_mentions=True, rm_punctuation=True, rm_unicode=True):
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
        self.cleaned_corpus = []

    def preprocess(self,text):
        """
        Processes a string in order to remove urls, mentions, unicode characters,
        and punctuation. It also replaces characters that are repeated more than
        three times by two of the same character.
        """
        text = text.lower()

        if self.rm_mentions:
            text = re.sub(self.mentions_regex, '', text) 

        if self.rm_urls:
            text = re.sub(self.url_regex, '', text) 
        
        if self.rm_unicode:
            text = re.sub(self.unicode_regex, '', text)

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
