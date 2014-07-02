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
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from collections import defaultdict
import utils as utils


class api(object):
    """
    Programming interface dedicated to the study of the users' mood.
    """

    def __init__(self, expandVocabularyClass=expand_vocabulary.ContextSimilar, clf=None):
        """
        Initializes the api class using ContextSimilar to expand vocabulary by default.
        """
        super(api, self).__init__()
        self.expandVocabularyClass = expandVocabularyClass
        self.features = []
        self.labels = []
        self.X = None
        self.corpus = []
        if not clf:
            self.clf = svm.SVC(kernel='linear', C=1, class_weight='auto')

    def expandVocabulary(self, vocabulary, corpus, n=20):
        """
        Calls the strategy loaded at the initialization to expand the vocabulary.
        """
        return self.expandVocabularyClass(vocabulary, corpus, n).expandVocabulary()

    def buildX(self, corpus, k=100, cleaner_options={}, fb_options={}, tfidf_options={}):
        """
        """
        self.corpus = corpus

        # clean the corpus
        cl = utils.Cleaner(**cleaner_options)
        # build the features
        fb = utils.FeaturesBuilder(corpus, cleaner=cl, **fb_options)
        self.features, self.labels = fb.run()

        # process labels so they are in the right format
        array_labels = DictVectorizer().fit_transform(self.labels).toarray()
        if array_labels.shape[1] == 1:
            array_labels = [x[0] for x in array_labels]
        self.vect_labels = array_labels

        self.vectorizer = TfidfVectorizer(**tfidf_options)
        self.features_selection = SelectKBest(chi2, k)
        self.pipeline = Pipeline([('tfidf', self.vectorizer),
                                  ('chi2', self.features_selection)])
        self.X = self.pipeline.fit_transform(self.features, self.vect_labels)
        self.X = preprocessing.scale(self.X.toarray())
        return self.X

    def train(self):
        """
        Trains the classifier.
        """
        self.clf.fit(self.X, self.labels)

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

        hascoef = False
        if hasattr(self.clf, 'coef_'):
            hascoef = True

        print "#### Mood Benchmark ####"
        print "Classifier: " + str(self.clf)
        print "Labels: " + str(label_names)

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
                scores['confusion'].append(metrics.confusion_matrix(y_test, y_pred))
                if hascoef:
                    scores['weight'].append(self.clf.coef_[0])
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
            print "Confusion Matrix:".ljust(left)
            reduced_cm = reduce(np.add, scores['confusion'])
            print str(reduced_cm)



            if n_examples:
                print
                print "--- " + str(n_examples) + " Misclassified Tweets ---"

            def get_ft_attr(ft):
                vect_idx = self.vectorizer.get_feature_names().index(ft)
                coef_array = self.features_selection.get_support(True)
                coef_indexes = np.where(coef_array == vect_idx)
                if coef_indexes[0].size:
                    coef_idx = coef_indexes[0][0]
                else:
                    coef_idx = -1
                if hascoef and coef_idx != -1:
                    w = self.clf.coef_[0][coef_idx]
                else:
                    w = 0
                return vect_idx, w

            for j in range(min(n_examples, len(wrong_class))):
                idx = wrong_class.pop()
                true_class = self.labels[idx][label]  # y_pred[idx]
                pred_class = np.abs(true_class-1)  # y_test[idx]
                print "True: " + str(true_class) + " / Pred: " + str(pred_class)
                print corpus[idx]['text'].encode('ascii', 'ignore')
                if hascoef:
                    ft_idx = []
                    ft_w = []
                    for ft in self.features[idx].split():
                        if ft in self.vectorizer.get_feature_names():
                            vect_idx, w = get_ft_attr(ft)
                            if w != 0:
                                ft_idx.append(vect_idx)
                                ft_w.append(w)
                    sorted_w_idx = np.argsort(ft_w)
                    for k in sorted_w_idx:
                        left = 30
                        right = 20
                        ft = self.vectorizer.get_feature_names()[ft_idx[k]].encode('ascii', 'ignore')
                        w = ft_w[k]
                        print ("\t" + ft + ": ").ljust(left) + str(w).ljust(right)
            if n_examples:
                print

            if top_features:
                print
                if hascoef:
                    top_features_mean = reduce(np.add, scores['weight'])/n_folds
                    print("--- Top 50 features [over " + str(len(top_features_mean)) + "]: ---")
                    feature_names = [self.vectorizer.get_feature_names()[x]
                                     for x in self.features_selection.get_support(True)]
                    top50 = np.argsort(top_features_mean)[-50:]
                    for idx in top50:
                        print "\t" + feature_names[idx].ljust(15) \
                              + str(top_features_mean[idx]).ljust(10)
                else:
                    print("Error while printing the top features: the classifier does not have a "
                          + "coef_ attribute.")
                print

            return np.mean(scores['rocauc'])
