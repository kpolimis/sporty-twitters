import mood
import tweets
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

    # Mood API #
    def expandVocabulary(self, vocabulary, corpus, n=20):
        return self.mood.expandVocabulary(vocabulary, corpus, n)

    def buildFeatures(self, corpus, keep_rt=True, labels=False, binary=False):
        return self.mood.buildFeatures(corpus, keep_rt, labels, binary)

    def buildVectorizer(self, vec_type='tfidf', options={}):
        return self.mood.buildVectorizer(vec_type, options)

    def train(self):
        return self.mood.train()

    def predict(self, X_pred):
        return self.mood.predict(X_pred)

    def benchmark(self, cv=5, scorings=['accuracy', 'f1', 'precision', 'recall', 'roc_auc']):
        return self.mood.benchmark(cv, scorings)

    # Tweets API #
    def load(self, input_file, lazy=True):
        return self.tweets.load(input_file, lazy)

    def authenticate(self):
        return self.tweets.authenticate()

    def collect(self, tracked_words, output=None, mode='a+', count=0, lang=["en-EN", "en", "en-CA", "en-GB"], locations=None):
        return self.tweets.collect(tracked_words, output, mode, count, lang)

    def filter(self, n, words, each_word=True, out_stream=None, mode='a+'):
        return self.tweets.filter(n, words, each_word, out_stream, mode)

    def label(self, labels, output_file=None, begin_line=0):
        return self.tweets.label(labels, output_file, begin_line)