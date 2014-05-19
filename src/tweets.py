from TwitterAPI import TwitterAPI
import json
import codecs
import sys
import re
from collections import defaultdict

class api():

    def __init__(self, settings_file=None):
        self.settings_file = settings_file
        self.settings = settings
        self.twitterapi = False
        self.authenticate()
        self.tweets = []
        self.filtered_tweets = []
        self.words_count = defaultdict(int)
        self.words_filtered = set()

    def load(self, input_file):
        self.tweets = []
        with open(input_file, "r") as f:
            for line in f:
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
                r = twitterapi.request('statuses/filter', req_options)
                for item in r.get_iterator():
                    if 'limit' not in item.keys():
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

    def filter(n, words, each_word=True, out_stream=sys.stdout):
        self.filtered_tweets = []
        self.words_filtered = set(words)

        # initialize count variables
        count = 0

        # Process each tweet
        for tw in self.tweets:
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
