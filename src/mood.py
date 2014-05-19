import expand_vocabulary
import json
import argparse
import sys
from time import time
import StringIO
import numpy as np
import re
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import metrics
from sklearn import cross_validation
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
        self.tfidf = None
        self.clf = clf

    def expandVocabulary(self, vocabulary, corpus, n=20):
        self.vocabulary = vocabulary
        self.corpus = corpus
        self.expandVocabulary = self.expandVocabulary(self.vocabulary, self.corpus, n)
        return self.expandVocabulary.expandVocabulary()

    def buildFeatures(self, corpus, keep_rt=True, labels=False, binary=False):
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

            # extract the other features (mentions, hashtags, etc)
            entities = tw['entities']
            if len(entities["user_mentions"]) != 0:
                terms.append("USER_MENTIONS")
            if len(entities["hashtags"]) != 0:
                terms.append("HASHTAGS")
            if len(text) < 50:
                terms.append("TW_SMALL")
            elif len(text) < 100:
                terms.append("TW_MEDIUM")
            else:
                terms.append("TW_LARGE")

            self.features.append(" ".join(terms))

            if labels:
                d = {}
                for l in labels:
                    d[l] = int(tw[l])
                self.labels.append(d)

        return self.features, self.labels

    def buildTfidf(self, options):
        if not self.features:
            print "Error: no features defined yet. Call getFeatures method first."
            return False
        self.vectorizer = TfidfVectorizer(**options)
        self.tfidf = self.vectorizer.fit_transform(self.features)
        self.X = preprocessing.scale(self.tfidf.toarray())
        return self.X

    def train(self, label="label"):
        # TODO: deal with multiple labels
        labels = [d[label] for d in self.labels]
        self.clf.fit(self.X, labels)

    def predict(self, X_pred):
        self.clf.predict(X_pred)

    def benchmark(self, cv=5, scorings=['accuracy', 'f1', 'precision', 'recall', 'roc_auc']):
        # TODO: change this method to deal with multiple labels
        for label in self.labels[0]:
            print "-"*80
            labels = np.array([d[label] for d in self.labels])

            for method in scorings:
                score = cross_validation.cross_val_score(self.clf, self.X, labels, cv=cv, scoring=method)
                method_name = 'Average ' + method + ': '
                score_str = str(score.mean()) + " (+/- " + str(score.std()) + ")"
                print method_name.ljust(25) + score_str.ljust(20)

        print "-"*80
        if hasattr(self.clf, 'coef_'):
            print("Top 10 keywords:")
            feature_names = np.asarray(self.vectorizer.get_feature_names())

            top10 = np.argsort(self.clf.coef_[0])[-10:]
            for idx  in top10:
                print "\t" + feature_names[idx].ljust(15) + str(self.clf.coef_[0][idx]).ljust(10)
