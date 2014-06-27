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

    def buildFeatures(self, corpus, cleaner_options={}, fb_options={}):
        """
        Builds and returns a list of features and a list of labels that can then be passed to a
        sklearn vectorizer.
        """
        self.corpus = corpus
        cl = utils.Cleaner(**cleaner_options)
        fb = utils.FeaturesBuilder(corpus, cleaner=cl, **fb_options)
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
        corpus = self.corpus.tolist()

        print "#### Mood Benchmark ####"
        print "Classifier: " + str(self.clf)
        print "Labels: " + str(label_names)

        # print "Pos/Neg:   number of positive labels/number of negative labels"
        # print "Accuracy:  average accuracy over " + str(n_folds) + " folds"
        # print "F1:        F1 score for the positive label"
        # print "Precision: Precision for the positive label"
        # print "Recall:    Recall for the positive label"
        # print "ROC AUC:   Area Under the ROC-Curve"
        # print

        for label in label_names:
            print "==== Label: " + label + " [" + str(n_folds) + " folds] ===="
            X = self.X
            y = np.array([d[label] for d in self.labels])

            skf = StratifiedKFold(y, n_folds=n_folds)
            i = 0
            scores = defaultdict(list)
            wrong_class = set()
            for train_index, test_index in skf:
                i += 1
                X_train, X_test = X[train_index], X[test_index]
                y_train, y_test = y[train_index], y[test_index]

                self.clf.fit(X_train, y_train)
                y_pred = self.clf.predict(X_test)

                scores['nb_pos'].append(sum([1 for x in y_test if x == 1]))
                scores['nb_neg'].append(sum([1 for x in y_test if x == 0]))
                scores['acc'].append(metrics.accuracy_score(y_test, y_pred))
                scores['f1'].append(metrics.f1_score(y_test, y_pred, average='macro'))
                scores['prec'].append(metrics.precision_score(y_test, y_pred, average='macro'))
                scores['rec'].append(metrics.recall_score(y_test, y_pred, average='macro'))
                scores['rocauc'].append(metrics.roc_auc_score(y_test, y_pred))

                if n_examples > 0:
                    for j in range(0, len(y_test)):
                        if y_test[j] != y_pred[j]:
                            wrong_class.add(test_index[j])

            self.scores = scores
            left = 12
            right = 15

            posneg = str(sum(scores['nb_pos'])) + "/" + str(sum(scores['nb_neg']))
            print "Pos/Neg:".ljust(left) + posneg.ljust(right)
            print "Accuracy:".ljust(left) + str(np.mean(scores['acc'])).ljust(right)
            print "F1:".ljust(left) + str(np.mean(scores['f1'])).ljust(right)
            print "Precision:".ljust(left) + str(np.mean(scores['prec'])).ljust(right)
            print "Recall:".ljust(left) + str(np.mean(scores['rec'])).ljust(right)
            print "ROC AUC:".ljust(left) + str(np.mean(scores['rocauc'])).ljust(right)

            hascoef = False
            if hasattr(self.clf, 'coef_'):
                hascoef = True

            if n_examples:
                print
                print "--- " + str(n_examples) + " Misclassified Tweets ---"

            for j in range(min(n_examples, len(wrong_class))):
                idx = wrong_class.pop()
                true_class = self.labels[idx][label]  # y_pred[idx]
                pred_class = np.abs(true_class-1)  # y_test[idx]
                print "True: " + str(true_class) + " / Pred: " + str(pred_class)
                print corpus[idx]['text'].encode('ascii', 'ignore')
                for ft in self.features[idx].split():
                    if ft.lower() in self.vectorizer.get_feature_names():
                        ft_idx = self.vectorizer.get_feature_names().index(ft.lower())
                        if hascoef:
                            ft_w = self.clf.coef_[0][ft_idx]
                        else:
                            ft_w = 0
                    else:
                        ft_w = 0
                    left = 30
                    right = 20
                    ft = ft.encode('ascii', 'ignore')
                    print ("\t" + ft + ": ").ljust(left) + str(ft_w).ljust(right)
            if n_examples:
                print

            if top_features:
                print
                if hascoef:
                    print("--- Top 50 features [over " + str(len(self.clf.coef_[0])) + "]: ---")
                    feature_names = np.asarray(self.vectorizer.get_feature_names())
                    top50 = np.argsort(self.clf.coef_[0])[-50:]
                    for idx in top50:
                        print "\t" + feature_names[idx].ljust(15) \
                              + str(self.clf.coef_[0][idx]).ljust(10)
                else:
                    print("Error while printing the top features: the classifier does not have a "
                          + "coef_ attribute.")
                print
