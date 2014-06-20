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
from sklearn.cross_validation import StratifiedKFold
from sklearn import preprocessing
from sklearn import svm
from collections import defaultdict
import utils as utils


class api(object):
    """
    Programming Interface dedicated to the study of the users' mood.
    """

    def __init__(self, expandVocabularyClass=expand_vocabulary.ContextSimilar, clf=None):
        """
        Initializes the api class using ContextSimilar to expand vocabulary by default.
        """
        super(api, self).__init__()
        self.expandVocabularyClass = expandVocabularyClass
        self.features = []
        self.labels = []
        self.vectorizer = None
        self.X = None
        self.tfidf = None
        self.corpus = []
        if not clf:
            self.clf = svm.SVC(kernel='linear', C=1, class_weight='auto')

    def expandVocabulary(self, vocabulary, corpus, n=20):
        """
        Calls the strategy loaded at the initialization to expand the vocabulary.
        """
        return self.expandVocabularyClass(vocabulary, corpus, n).expandVocabulary()

    def buildFeatures(self, corpus, cleaner_options={}, labels=False, keep_rt=True):
        """
        Builds and returns a list of features and a list of labels that can then be passed to a
        sklearn vectorizer.
        """
        self.corpus = corpus
        cl = utils.Cleaner(**cleaner_options)
        fb = utils.FeaturesBuilder(corpus, cleaner=cl, labels=labels, keep_rt=keep_rt)
        self.features, self.labels = fb.run()

        return self.features, self.labels

    def buildVectorizer(self, vec_type='tfidf', options={}):
        """
        Builds the wanted vectorizer once the features have been built using buildFeatures.
        """
        if not self.features:
            raise Exception("No features defined yet. Call buildFeatures method first.")

        if vec_type == 'tfidf':
            self.vectorizer = TfidfVectorizer(**options)
            self.tfidf = self.vectorizer.fit_transform(self.features)
            self.X = preprocessing.scale(self.tfidf.toarray())
            return self.X
        else:
            raise Exception("Vectorizer type (" + str(vec_type) + ")not supported yet.")

    def train(self):
        """
        Trains the classifier.
        """
        array_labels = DictVectorizer().fit_transform(self.labels).toarray()
        if array_labels.shape[1] == 1:
            array_labels = [x[0] for x in array_labels]
        self.clf.fit(self.X, array_labels)

    def predict(self, X_pred):
        """
        Predicts the label of entries.
        """
        return self.clf.predict(X_pred)

    def benchmark(self, n_folds=3, n_examples=0, top_features=False):
        """
        Computes and displays several scores to evaluate the classifier.
        """
        label_names = self.labels[0].keys()

        for label in label_names:
            print "==== Label: " + label + " [" + str(n_folds) + " folds] ===="
            X = self.X
            y = np.array([d[label] for d in self.labels])

            skf = StratifiedKFold(y, n_folds=n_folds)
            i = 0
            for train_index, test_index in skf:
                i += 1
                print
                print "= Fold " + str(i) + " ="
                X_train, X_test = X[train_index], X[test_index]
                y_train, y_test = y[train_index], y[test_index]
                self.clf.fit(X_train, y_train)
                y_pred = self.clf.predict(X_test)
                nb_pos = str(sum([1 for x in y_test if x == 1]))
                nb_neg = str(sum([1 for x in y_test if x == 0]))
                posneg = nb_pos + "/" + nb_neg
                acc = metrics.accuracy_score(y_test, y_pred)
                f1 = metrics.f1_score(y_test, y_pred, average=None)
                prec = metrics.precision_score(y_test, y_pred, average=None)
                rec = metrics.recall_score(y_test, y_pred, average=None)
                rocauc = metrics.roc_auc_score(y_test, y_pred)
                left = 12
                right = 15
                print "Pos/Neg:".ljust(left) + str(posneg).ljust(right)
                print "Accuracy:".ljust(left) + str(acc).ljust(right)
                print "F1:".ljust(left) + str(f1).ljust(right)
                print "Precision:".ljust(left) + str(prec).ljust(right)
                print "Recall:".ljust(left) + str(rec).ljust(right)
                print "ROC_AUC:".ljust(left) + str(rocauc).ljust(right)

                if n_examples > 0:
                    print "--- Diff: ---"
                    count = n_examples
                    for j in range(0, len(y_test)):
                        if count < 1:
                            break
                        if y_test[j] != y_pred[j]:
                            idx = test_index[j]
                            print "True: " + str(y_test[j]) + " / Pred: " + str(y_pred[j])
                            print self.features[idx]
                            count -= 1

            if top_features:
                print
                if hasattr(self.clf, 'coef_'):
                    print("Top 50 keywords:")
                    feature_names = np.asarray(self.vectorizer.get_feature_names())
                    top50 = np.argsort(self.clf.coef_[0])[-50:]
                    for idx in top50:
                        print "\t" + feature_names[idx].ljust(15) \
                              + str(self.clf.coef_[0][idx]).ljust(10)
            print