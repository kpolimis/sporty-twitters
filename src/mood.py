import expand_vocabulary
import json
import argparse
import sys
import StringIO
import numpy as np
import re
from sklearn.feature_extraction import DictVectorizer
from sklearn import preprocessing
from sklearn import svm
from collections import defaultdict

class api():
    """
    Programming Interface dedicated to the study of the users' mood in the sporty twitters project.
    """

    def __init__(self, expandVocabulary=expand_vocabulary.ContextSimilar, clf=svm.SVC(kernel='linear', C=1)):
        self.expandVocabulary = expandVocabulary
        self.corpus = []
        self.vocabulary = []
        self.features = []
        self.labels = []
        self.vectorizer = None
        self.X = None
        self.clf = clf

    def expandVocabulary(self, vocabulary, corpus, n=20):
        self.vocabulary = vocabulary
        self.corpus = corpus
        self.expandVocabulary = self.expandVocabulary(self.vocabulary, self.corpus, n)
        return self.expandVocabulary.expandVocabulary()

    def getFeatures(self, corpus, keep_rt=True, label=False, binary=False):
        self.corpus = corpus
        self.features = []
        self.labels = []

        for line in self.corpus:
            # load the raw json and extract the text
            tw = json.loads(line)
            # filter on retweets
            if tw['retweeted'] and not keep_rt:
                continue

            # extract the text features
            text = tw['text']
            terms = re.split("\s+", text.strip())
            d = defaultdict(int)
            for t in terms:
                if binary:
                    d[t] = 1    
                else:
                    d[t] += 1

            # extract the other features (mentions, hashtags, etc)
            entities = tw['entities']
            if len(entities["user_mentions"]) != 0:
                d["USER_MENTIONS"] = 1
            if len(entities["hashtags"]) != 0:
                d["HASHTAGS"] = 1
            if len(text) < 50:
                d["TW_SMALL"] = 1
            elif len(text) < 100:
                d["TW_MEDIUM"] = 1
            else:
                d["TW_LARGE"] = 1

            # append to the corpus
            self.features.append(d)
            if label:
                self.labels.append(int(tw['label']))

        return self.features, np.array(self.labels)

    def getX(self):
        if not self.features:
            print "Error: no features defined yet. Call getFeatures method first."
            return False
        # use the DictVectorizer method to fit the data, avoid sparse matrix in
        # order to scale it after.
        self.vectorizer = DictVectorizer(sparse=False)
        self.X = self.vectorizer.fit_transform(self.features)
        self.X = preprocessing.scale(self.X)
        return self.X

    def train(self):
        clf.fit(self.X, self.labels)

    def predict(self, X_pred):
        clf.predict(X_pred)

    def benchmark(self):
        # TODO: test with k fold cross validation
        return True
        