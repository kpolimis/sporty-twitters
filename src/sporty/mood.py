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

    def __init__(self, expandVocabulary=expand_vocabulary.ContextSimilar, clf=None):
        self.expandVocabulary = expandVocabulary
        self.corpus = []
        self.vocabulary = []
        self.features = []
        self.labels = []
        self.vectorizer = None
        self.X = None
        self.tfidf = None
        if clf == None:
            self.clf = svm.SVC(kernel='linear', C=1)

    def expandVocabulary(self, vocabulary, corpus, n=20):
        self.vocabulary = vocabulary
        self.corpus = corpus
        self.expandVocabulary = self.expandVocabulary(self.vocabulary, self.corpus, n)
        return self.expandVocabulary.expandVocabulary()

    def buildFeatures(self, corpus, keep_rt=True, labels=False, binary=False):
        self.corpus = corpus
        self.features = []
        self.labels = []

        for tw in self.corpus:
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

    def buildVectorizer(self, vec_type='tfidf', options={}):
        if not self.features:
            print "Error: no features defined yet. Call buildFeatures method first."
            return False
        if vec_type == 'tfidf':
            self.vectorizer = TfidfVectorizer(**options)
            self.tfidf = self.vectorizer.fit_transform(self.features)
            self.X = preprocessing.scale(self.tfidf.toarray())
            return self.X
        else:
            print "Error: vectorizer type (" + str(vec_type) + ")not supported yet."
            return False

    def train(self):
        array_labels = DictVectorizer().fit_transform(self.labels).toarray()
        self.clf.fit(self.X, array_labels)

    def predict(self, X_pred):
        self.clf.predict(X_pred)

    def benchmark(self, cv=5, scorings=['accuracy', 'f1', 'precision', 'recall', 'roc_auc']):
        for i, label in enumerate(self.labels[0]):
            print "-"*80
            print "- label: " + label
            print "-"*80
            labels = np.array([d[label] for d in self.labels])
            for method in scorings:
                score = cross_validation.cross_val_score(self.clf, self.X, labels, cv=cv, scoring=method)
                method_name = 'Average ' + method + ': '
                score_str = str(score.mean()) + " (+/- " + str(score.std()) + ")"
                print method_name.ljust(25) + score_str.ljust(20)

            if hasattr(self.clf, 'coef_'):
                print("Top 10 keywords:")
                feature_names = np.asarray(self.vectorizer.get_feature_names())
                top10 = np.argsort(self.clf.coef_[i])[-10:]
                for idx  in top10:
                    print "\t" + feature_names[idx].ljust(15) + str(self.clf.coef_[i][idx]).ljust(10)
