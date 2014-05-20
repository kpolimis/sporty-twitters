from TwitterAPI import TwitterAPI
import json
import codecs
import sys
import re
from collections import defaultdict

class api():

    def __init__(self, settings_file=None, lazy=False):
        self.settings_file = settings_file
        self.lazy = lazy
        self.tweets_file = None
        self.twitterapi = False
        self.authenticate()
        self.tweets = []
        self.filtered_tweets = []
        self.words_count = defaultdict(int)
        self.words_filtered = set()

    def load(self, input_file):
        self.tweets = []
        self.tweets_file = open(input_file, 'r')
        if not self.lazy:
            for line in self.tweets_file:
                tw = json.loads(line.strip())
                self.tweets.append(tw)
        return self.tweets

    def authenticate(self):
        if self.settings_file:
            with open(self.settings_file, 'r') as settings_f:
                self.settings = json.load(settings_f)
                consumer_key = self.settings['consumer_key']
                consumer_secret = self.settings['consumer_secret']
                access_token = self.settings['access_token']
                access_token_secret = self.settings['access_token_secret']
                self.twitterapi = TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)

    def collect(self, tracked_words, output=sys.stdout, count=0, lang=["en-EN", "en", "en-CA", "en-GB"], locations=None):
        if not self.settings_file:
            print "Error: TwitterAPI not authenticated. Please call the constructor using a settings file if you want to collect tweets."
            return False
        i = 0
        out = codecs.getwriter('utf8')(output)

        req_options = dict()
        req_options['track'] = ",".join(tracked_words)
        req_options['language'] = ",".join(lang)
        if locations:
            req_options['locations'] = locations

        while True:
            try:
                r = self.twitterapi.request('statuses/filter', req_options)
                for item in r.get_iterator():
                    if 'limit' not in item.keys():
                        if not self.lazy:
                            self.tweets.append(item)
                        out.write(json.dumps(item))
                        out.write("\n")
                        out.flush()
                        i += 1
                        if count and i >= count:
                            break
                break
            except:
                # sys.stderr.write("ChunkedEncodingError\n")
                continue

    def _iter(self):
        if self.lazy:
            data = json.loads(self.tweets_file.readline().strip())
        else:
            if "tweet_iter" not in _iter.__dict__:
                _iter.tweet_iter = iter(self.tweets)
            data = _iter.tweet_iter.next()
        yield data

    def filter(self, n, words, each_word=True, out_stream=sys.stdout, from_file=True):
        self.filtered_tweets = []
        self.words_filtered = set(words)

        # initialize count variables
        count = 0

        # Process each tweet
        for tw in self._iter():
            text = tw['text']

            # check that words we look for are present in this tweet
            terms = set(x.lower() for x in re.split("\s+", text))
            inter = terms.intersection(self.words_filtered)

            # once we have found n tweets containing the word w, we remove the
            # word w from our search list
            to_remove = set(w for w in inter if self.words_count[w] >= n)
            self.words_filtered -= to_remove

            # case where we output the found tweet: words which count is < n were found in the tweet            
            if inter and not to_remove:
                out_stream.write(json.dumps(tw) + "\n")
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

    def label(self, labels, output_file, begin=0):
        # define the opening mode of the output file given the begin line
        o_mode = "w"
        if begin != 0:
            o_mode = "a+"
        with open(output_file, o_mode) as o:
            count = 0
            for tw in self._iter():
                print "-"*20
                # read lines that are before the given beginning line
                if count < begin:
                    count += 1
                    continue
                text = tw['text']
                # show the line and ask the user to choose a label
                sys.stdout.write(text + "\n")
                if type(labels) == list:
                    labels = {"label": labels}

                for ln in labels:
                    l = self.__ask_label(ln, labels[ln])
                    if l == 'q':
                        return()
                    tw[ln] = l

                outstr = json.dumps(tw) + "\n"
                # output the line and the label separated by a tab
                o.write(outstr)
                o.flush()
