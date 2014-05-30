from TwitterAPI import TwitterAPI
import json
import codecs
import sys
import re
import os
from collections import defaultdict

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
                self.tweets.seek(0, os.SEEK_END)
            if type(tw) == dict:
                self.tweets.write(json.dumps(tw) + "\n")
            elif type(tw) == str:
                self.tweets.write(tw + "\n")
            self.tweets.flush()
        else:
            self.tweets.append(tw)

class api():

    def __init__(self, settings_file=None):
        self.settings_file = settings_file
        self.tweets = Tweets()
        self.filtered_tweets = Tweets()
        self.labeled_tweets = Tweets()
        self.twitterapi = None
        self.words_count = defaultdict(int)
        self.words_filtered = set()
        self.authenticate()

    def load(self, input_file, lazy=True):
        self.lazy = lazy
        if self.lazy:
            self.tweets = Tweets(input_file)
        else:
            self.tweets = Tweets()
            with open(input_file, 'r') as i:
                for line in i:
                    tw = json.loads(line.strip())
                    self.tweets.append(tw)
        return self.tweets

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

    def collect(self, tracked_words, output=None, mode='a+', count=0, lang=["en-EN", "en", "en-CA", "en-GB"], locations=None):
        if not self.settings_file:
            print "Error: TwitterAPI not authenticated. Please call the constructor using a settings file if you want to collect tweets."
            return False

        self.tweets = Tweets(output, mode)

        req_options = dict()
        req_options['track'] = ",".join(tracked_words)
        req_options['language'] = ",".join(lang)
        if locations:
            req_options['locations'] = locations

        i = 0
        while True:
            try:
                r = self.twitterapi.request('statuses/filter', req_options)
                for item in r.get_iterator():
                    if 'limit' not in item.keys():
                        self.tweets.append(item)
                        i += 1
                        if count and i >= count:
                            break
                break
            except:
                # sys.stderr.write("ChunkedEncodingError\n")
                continue


    def filter(self, n, words, each_word=True, out_stream=None, mode='a+', rt=True):
        self.filtered_tweets = Tweets(out_stream, mode)
        self.words_filtered = set(words)

        # initialize count variables
        count = 0

        # Process each tweet
        for tw in self.tweets:
            text = tw['text']
            tw_rt = text.find("RT") != -1
            if not rt and tw_rt:
                continue
            # check that the words we look for are present in this tweet
            terms = set(x.lower() for x in re.split("\s+", text))
            inter = terms.intersection(self.words_filtered)

            # once we have found n tweets containing the word w, we remove the
            # word w from our search list
            to_remove = set(w for w in inter if self.words_count[w] >= n)
            self.words_filtered -= to_remove

            # case where we output the found tweet: words which count is < n were found in the tweet            
            if inter and not to_remove:
                self.filtered_tweets.append(tw)
                count += 1
                for w in inter:
                    self.words_count[w] += 1
            break_cond = not each_word or not self.words_filtered
            if count >= n and break_cond:
                break
        return self.filtered_tweets

    def __ask_label(self, label_name, choices):
        # Set instructions for user
        first_input = "Choose " + label_name + " amongst " + str(choices) + " or (q)uit: "
        choices = set(choices)
        incorrect_input = "Incorrect input. " + first_input
        ask = first_input
        while True:
            try:
                l = raw_input(ask)
                if str(l) == 'q':
                    l = str(l)
                    break
                elif int(l) in choices:
                    l = int(l)
                    break
                else:
                    ask = incorrect_input   
            except ValueError:
                ask = incorrect_input
                continue
        return l

    def label(self, labels, output_file=None, begin=0):
        # define the opening mode of the output file given the begin line
        o_mode = "w"
        if begin != 0:
            o_mode = "a+"
        self.labeled_tweets = Tweets(output_file, o_mode)
        count = 0
        for tw in self.tweets:
            tw_labeled = dict(tw)
            # read lines that are before the given beginning line
            count += 1
            if count < begin:
                continue
            print "-"*20 + " " + str(count)
            text = tw_labeled['text']
            # show the line and ask the user to choose a label
            sys.stdout.write(text + "\n")
            if type(labels) == list:
                labels = {"label": labels}

            for ln in labels:
                l = self.__ask_label(ln, labels[ln])
                if l == 'q':
                    return()
                tw_labeled[ln] = l
            self.labeled_tweets.append(tw_labeled)
