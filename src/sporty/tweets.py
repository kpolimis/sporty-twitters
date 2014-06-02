import json
import codecs
import sys
import re
import os
from collections import defaultdict
from utils import TwitterAPIUser
from datastructures import Tweets

class api(TwitterAPIUser):
    def __init__(self, settings_file=None):
        super(api, self).__init__(settings_file)
        self.tweets = Tweets()
        self.filtered_tweets = Tweets()
        self.labeled_tweets = Tweets()
        self.words_count = defaultdict(int)
        self.words_filtered = set()

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

    def collect(self, tracked_words, output_file=None, mode='a+', count=0, lang=["en-EN", "en", "en-CA", "en-GB"], locations=None):
        self.tweets = Tweets(output_file, mode)
        i = 0
        while True:
            try:
                r = self.getStatusStream(tracked_words, lang, locations)
                for item in r.get_iterator():
                    if 'limit' not in item.keys():
                        self.tweets.append(item)
                        i += 1
                        if count and i >= count:
                            break
                break
            except Exception, e:
                # sys.stderr.write("ChunkedEncodingError\n")
                continue

    def filter(self, n, words, each_word=True, output_file=None, mode='a+', rt=True):
        self.filtered_tweets = Tweets(output_file, mode)
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
