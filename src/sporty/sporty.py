import mood
import tweets
import users
import utils
import sys


class api():
    """
    Main API that centralizes/wraps all the other APIs so that the user does not have to worry
    about which API instanciate.
    """
    def __init__(self, settings_file=None):
        self.tweets = tweets.api(settings_file)
        self.mood = mood.api()
        self.users = users.api(settings_file=settings_file)

    # Mood API #

    def expandVocabulary(self, vocabulary, corpus, n=20):
        return self.mood.expandVocabulary(vocabulary, corpus, n)

    def buildX(self, corpus, k=100, cleaner_options={}, fb_options={}, tfidf_options={}):
        return self.mood.buildX(corpus, k, cleaner_options, fb_options, tfidf_options)

    def train(self):
        return self.mood.train()

    def predict(self, X_pred):
        return self.mood.predict(X_pred)

    def benchmark(self, n_folds=3, n_examples=0, top_features=False):
        return self.mood.benchmark(n_folds, n_examples, top_features)

    # Tweets API #

    def load(self, input_file):
        return self.tweets.load(input_file)

    def authenticate(self):
        return self.tweets.authenticate()

    def collect(self, tracked_words, output_file=None, mode='a+', count=0,
                lang=["en-EN", "en", "en-CA", "en-GB"], locations=None):
        return self.tweets.collect(tracked_words, output_file, mode, count, lang)

    def filter(self, n, words, each_word=True, output_file=None, mode='a+', rt=True):
        return self.tweets.filter(n, words, each_word, output_file, mode, rt)

    def label(self, labels, output_file=None, begin_line=0):
        return self.tweets.label(labels, output_file, begin_line)

    # Users API

    def outputFriendsIds(self, output_dir="./"):
        return self.users.outputFriendsIds(output_dir)

    def collectTweets(self, output_dir="./", count=3200):
        return self.users.collectTweets(output_dir, count)

    def show(self):
        return self.users.show()
