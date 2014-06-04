import mood
import tweets
import user
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
        self.user = user.api(settings_file=settings_file)

    # Mood API #
    def expandVocabulary(self, vocabulary, corpus, n=20):
        return self.mood.expandVocabulary(vocabulary, corpus, n)

    def buildFeatures(self, corpus, keep_rt=True, labels=False):
        return self.mood.buildFeatures(corpus, keep_rt, labels)

    def buildVectorizer(self, vec_type='tfidf', options={}):
        return self.mood.buildVectorizer(vec_type, options)

    def train(self):
        return self.mood.train()

    def predict(self, X_pred):
        return self.mood.predict(X_pred)

    def benchmark(self, cv=5, scorings=['accuracy', 'f1', 'precision', 'recall', 'roc_auc']):
        return self.mood.benchmark(cv, scorings)

    # Tweets API #
    def load(self, input_file):
        return self.tweets.load(input_file)

    def authenticate(self):
        return self.tweets.authenticate()

    def collect(self, tracked_words, output_file=None, mode='a+', count=0, lang=["en-EN", "en", "en-CA", "en-GB"], locations=None):
        return self.tweets.collect(tracked_words, output_file, mode, count, lang)

    def filter(self, n, words, each_word=True, output_file=None, mode='a+', rt=True):
        return self.tweets.filter(n, words, each_word, output_file, mode, rt)

    def label(self, labels, output_file=None, begin_line=0):
        return self.tweets.label(labels, output_file, begin_line)

    # User API 
    def getFriends(self):
        return self.user.getFriends()

    def collectTweets(self, count=3200, output_file=None, mode='a+'):
        return self.user.collectTweets(count, output_file, mode)