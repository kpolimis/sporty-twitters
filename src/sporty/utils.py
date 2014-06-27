import re
import os.path
from collections import defaultdict
from datastructures import *
import sys
import string
import codecs
import json
from TwitterAPI import TwitterAPI
from sklearn.feature_extraction.text import CountVectorizer
from lexicon import Lexicon


class FeaturesBuilder(object):
    def __init__(self, corpus,
                 cleaner=None,
                 func_list=None,
                 labels=False,
                 labels_reduce_f=None,
                 keep_rt=True,
                 mini=50,
                 maxi=100,
                 liwc_path=None):
        super(FeaturesBuilder, self).__init__()
        self.corpus = corpus
        if cleaner:
            self.cleaner = cleaner
        else:
            self.cleaner = Cleaner()
        self.extract_labels = labels
        self.keep_rt = keep_rt
        self.extractors = []
        self.mini = mini
        self.maxi = maxi
        self.features = []
        self.labels = []
        self.labels_reduce_f = labels_reduce_f
        self.tw_features = set()
        self.tweet = {}
        self.lexicon = None
        if liwc_path:
            self.lexicon = Lexicon(liwc_path)
        if not func_list:
            self.func_list = ['caseFeature',
                              'lengthFeature',
                              'liwcFeature',
                              'clean',
                              'wordTokenize',
                              #'charTokenize',
                              'ngrams',
                              'mentionsFeature',
                              'urlsFeature'
                              'hashtagsFeature']
        else:
            self.func_list = func_list

    def clean(self):
        self.tweet = self.cleaner.clean_tw(self.tweet)

    def tokenize(self, analyzer='word', ngram_range=(1, 1)):
        text = self.tweet['text']
        vec = CountVectorizer(analyzer=analyzer, ngram_range=ngram_range, lowercase=False)
        vec.fit_transform([text])
        self.tw_features = self.tw_features.union(set(vec.get_feature_names()))

    def wordTokenize(self):
        self.tokenize()

    def charTokenize(self):
        self.tokenize(analyzer='char_wb', ngram_range=(3, 3))

    def ngrams(self, ngram_range=(2, 2)):
        tw_save = self.tweet
        if not self.cleaner.rm_punctuation:
            self.cleaner.rm_punctuation = True
            self.tweet = self.cleaner.clean_tw(self.tweet)
        text = self.tweet['text']
        if -1 != text.find(' '):
                ngrams = CountVectorizer(ngram_range=ngram_range, min_df=1, lowercase=False)
                ngrams.fit_transform([text])
                ngrams_undersc = map(lambda x: x.replace(" ", "_"), ngrams.get_feature_names())
                self.tw_features = self.tw_features.union(set(ngrams_undersc))
        self.tweet = tw_save

    def mentionsFeature(self):
        entities = self.tweet['entities']
        if len(entities["user_mentions"]) != 0:
            self.tw_features.add("_USER_MENTIONS_")

    def hashtagsFeature(self):
        entities = self.tweet['entities']
        if len(entities["hashtags"]) != 0:
                self.tw_features.add("_HASHTAGS_")

    def urlsFeature(self):
        entities = self.tweet['entities']
        if len(entities["urls"]) != 0:
                self.tw_features.add("_URLS_")

    def lengthFeature(self):
        text = self.tweet['text']
        if len(text) < self.mini:
            self.tw_features.add("_TW_SMALL_")
        elif len(text) < self.maxi:
            self.tw_features.add("_TW_MEDIUM_")
        else:
            self.tw_features.add("_TW_LARGE_")

    def caseFeature(self):
        text = self.tweet['text']
        caps = float(sum(1 for c in text if c.isupper()))
        length = float(len(text))
        if caps/length > 0.8:
            self.tw_features.add("_ALL_CAPS_")

    def liwcFeature(self):
        if self.lexicon:
            words = self.tweet['text'].split()
            categories = self.lexicon.categories_for_tokens(words)
            features = reduce(lambda x, y: set(x).union(set(y)), categories)
            self.tw_features = self.tw_features.union(features)

    def extractFeatures(self, tw):
        check_func = (f for f in self.func_list if f in dir(self) and callable(getattr(self, f)))
        # filter on retweets
        self.tweet = tw
        tw_rt = self.tweet['text'].find("RT") != -1
        if not self.keep_rt and tw_rt:
            return False

        # apply features extractors
        for f in check_func:
            getattr(self, f)()
            #print self.tw_features
        self.features.append(" ".join(self.tw_features))
        return True

    def extractLabels(self, tw):
        if self.extract_labels:
            d = {}
            for l in self.extract_labels:
                d[l] = int(tw[l])
            if self.labels_reduce_f:
                labels = d.values()
                d = {}
                d['reduced'] = reduce(self.labels_reduce_f, labels)
            self.labels.append(d)

    def run(self):
        for tw in self.corpus:
            self.tw_features = set()
            if self.extractFeatures(tw):
                self.extractLabels(tw)
        return self.features, self.labels


class Cleaner():
    """
    Cleaner of corpus
    """
    def __init__(self, stopwords=None, emoticons=None, rm_urls=True, rm_mentions=True,
                 rm_punctuation=True, rm_unicode=True):
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
        self.original_corpus = []
        self.cleaned_corpus = []

    def preprocess(self, text):
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
                    text = string.replace(text, entry, " " + emo + " ")

        if self.rm_punctuation:
            text = ''.join(c for c in text if c not in self.exclude)

        text = re.sub(self.stem_regex, r'\1\1', text)
        return text

    def tokenize(self, text):
        """
        Tokenize a string and remove given stopwords from the final list of words.
        """
        words = re.split("\s+", text)
        words = [x for x in words if x]  # remove empty words
        if self.stopwords:
            # remove stopwords
            words = [x for x in words if x not in self.stopwords]
        return words

    def clean_tw(self, tw):
        """
        Clean one tweet by removing stopwords, URLs, mentions, and punctuation.
        """
        text = tw['text']
        text = self.preprocess(text)
        words = self.tokenize(text)
        text = " ".join(words)

        if text:
            tw['text'] = text
        return tw

    def clean(self, corpus):
        """
        Clean a corpus given as an iterable by removing stopwords, URLs, mentions, and punctuation.
        """
        self.original_corpus = corpus
        self.cleaned_corpus = (self.clean_tw(tw) for tw in corpus)
        return self.cleaned_corpus


class TwitterAPIUser(object):
    """
    TwitterAPIUser allows access to the Twitter API.
    """
    def __init__(self, settings_file=None):
        super(TwitterAPIUser, self).__init__()
        self.settings_file = settings_file
        self.twitterapi = None
        self.settings = None
        self.authenticate()

    def authenticate(self):
        """
        Authenticate to the Twitter API using the settings file given on initialization.
        """
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
            self.twitterapi = TwitterAPI(consumer_key, consumer_secret,
                                         access_token, access_token_secret)

    def getStatusStream(self, tracked_words, lang, locations):
        """
        Returns the response sent by the Twitter API when requested the last statuses in the
        Twitter timeline.
        """
        if not self.settings_file:
            raise Exception("TwitterAPI not authenticated. Please call the constructor using a "
                            + " settings file if you want to collect tweets.")

        req_options = dict()
        req_options['track'] = ",".join(tracked_words)
        req_options['language'] = ",".join(lang)
        if locations:
            req_options['locations'] = locations

        r = self.twitterapi.request('statuses/filter', req_options)
        return r

    def getFolloweesStream(self, user_id, cursor=-1, count=5000):
        """
        Returns the response sent by the Twitter API when requested the followees of a user.
        """
        req_options = dict()
        req_options['user_id'] = user_id
        req_options['cursor'] = cursor
        req_options['count'] = count
        r = self.twitterapi.request('friends/ids', req_options)
        return r

    def getFollowersStream(self, user_id, cursor=-1, count=5000):
        """
        Returns the response sent by the Twitter API when requested the followers of a user.
        """
        req_options = dict()
        req_options['user_id'] = user_id
        req_options['cursor'] = cursor
        req_options['count'] = count
        r = self.twitterapi.request('followers/ids', req_options)
        return r

    def getUserStream(self, user_id, since_id=None, max_id=None):
        """
        Returns the response sent by the Twitter API when requested the timeline of a user.
        """
        if not self.settings_file:
            raise Exception("TwitterAPI not authenticated. Please call the constructor using a"
                            + " settings file if you want to collect tweets.")

        req_options = dict()
        req_options['user_id'] = user_id
        req_options['count'] = 200
        if since_id:
            req_options['since_id'] = since_id
        if max_id:
            req_options['max_id'] = max_id

        r = self.twitterapi.request('statuses/user_timeline', req_options)
        return r
