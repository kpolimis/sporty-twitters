import argparse
import copy
import expand_vocabulary
import json
import logging
import matplotlib as mpl
import matplotlib.pyplot as plt
import multiprocessing
import numpy as np
import os.path
import re
import StringIO
import sys
import utils as utils
from collections import defaultdict
from multiprocessing import Process, Lock, Queue
from sklearn import cross_validation
from sklearn import metrics
from sklearn import preprocessing
from sklearn import svm
from sklearn.cross_validation import StratifiedKFold
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from time import time
from tweets import Tweets
logger = logging.getLogger(__name__)


class api(object):
	"""
	Programming interface dedicated to the study of the users' mood.
	"""

	def __init__(self, expandVocabularyClass=expand_vocabulary.ContextSimilar,
				 clf=None):
		"""
		Initializes the api class using ContextSimilar to expand vocabulary by
		default.

		Parameters:
		expandVocabularyClass - class to use to expand the vocabulary
		clf - classifier to use (default to SVM with linear kernel)
		"""
		super(api, self).__init__()
		self.cleaner_options = {}
		self.corpus = []
		self.expandVocabularyClass = expandVocabularyClass
		self.fb_options = {}
		self.features = []
		self.labels = []
		self.tfidf_options = {}
		self.X = None
		if not clf:
			self.clf = svm.SVC(kernel='linear', C=1, class_weight='auto')

	def expandVocabulary(self, vocabulary, corpus, n=20):
		"""
		Wrapper that calls the strategy loaded at the initialization in order to
		expand the vocabulary.

		Parameters:
		vocabulary - list containing vocabulary to expand
		corpus - corpus used to expand the vocabulary

		Return value:
		The extended version of the vocabulary.
		"""
		c = self.expandVocabularyClass(vocabulary, corpus, n)
		return c.expandVocabulary()

	def buildX(self, corpus, k=160,
			   cleaner_options={},
			   fb_options={},
			   tfidf_options={},
			   predict=False):
		"""
		Build the features vectors for each entry in the corpus given the options
		for the cleaner, the feature builder, and the vectorizer. If the flag
		predict is True, then we assume that we want to predict the labels of the
		given corpus and that the classifier has already been trained. Therefore,
		the options dictionaries already exist and we do not do features
		selection.

		Parameters:
		corpus - the data for which we want to build the features matrix
		k - number of features to keep during the features selection, irrelevant
			when predict is True.
		cleaner_options - options stored in a dictionary to be passed to a
						  Cleaner instance.
		fb_options - options stored in a dictionary to be passed to a
					 FeaturesBuilder instance.
		tfidf_options - options stored in a dictionary to be passed to a
						TfidfVectorizer instance.
		predict - boolean set to False when we are training the classifier and
				  set to True when we want to do a classification task.

		Return value:
		The features matrix for the given corpus.
		"""
		self.corpus = corpus

		# Different behavior given the predict flag
		if predict:
			cleaner_options = self.cleaner_options
			fb_options = self.fb_options
			fb_options['keep_rt'] = False
			fb_options['labels'] = False
			tfidf_options = self.tfidf_options
		else:
			self.cleaner_options = cleaner_options
			self.fb_options = fb_options
			self.tfidf_options = tfidf_options

		# build the cleaner and the features
		cl = utils.Cleaner(**cleaner_options)
		fb = utils.FeaturesBuilder(corpus, cleaner=cl, **fb_options)
		self.features, self.labels, self.twids = fb.run()

		# process labels so they are in the right format
		self.vect_labels = []
		if self.labels:
			array_labels = DictVectorizer().fit_transform(self.labels).toarray()
			if array_labels.shape[1] == 1:
				array_labels = [x[0] for x in array_labels]
			self.vect_labels = array_labels

		if not predict:
			# build the pipeline with the vectorizer and features selection
			self.vectorizer = TfidfVectorizer(**tfidf_options)
			self.features_selection = SelectKBest(chi2, k)
			self.pipeline = Pipeline([('tfidf', self.vectorizer),
									  ('chi2', self.features_selection)])
			self.X = self.pipeline.fit_transform(self.features,
												 self.vect_labels)
		else:
			# the pipeline has already been built in a previous call
			self.X = self.pipeline.transform(self.features)
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

	# def prec_rec_curve(self):
	# 	label_names = self.labels[0].keys()
	# 	for label in label_names:
	# 		X = self.X
	# 		y = np.array([d[label] for d in self.labels])

	def ROC_curve(self, c=0.1):
		"""
		Plot the ROC curve for each dimension.
		"""
		label_names = self.labels[0].keys()
		labels = ["Hostility", "Dejection", "Anxiety"]
		fpr_tpr = []
		for label in label_names:
			X = self.X
			y = np.array([d[label] for d in self.labels])

			# build cross validation set
			sets = cross_validation.train_test_split(X, y, test_size=c, random_state=1191)
			X_train, X_test, y_train, y_test = sets

			self.clf.fit(X_train, y_train)
			y_pred_proba = self.clf.predict_proba(X_test)[:, 1]
			fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred_proba,
								 pos_label=1)
			fpr_tpr.append((fpr, tpr))
			
		plt.figure(figsize=(6,5))
		styles = ['x-', '^-', 'o-']
		for i, (fpr, tpr) in enumerate(fpr_tpr):
			plt.plot(fpr, tpr, styles[i], label=labels[i], ms=4)
		plt.title("ROC Curve", size=16)
		# Add some axis labels
		plt.xlabel("False Positive Rate")
		plt.ylabel("True Positive Rate")
		plt.legend(loc="lower right")
		plt.savefig("ROC.pdf", bbox_inches='tight')

	def benchmark(self, n_folds=10, n_examples=0, top_features=False,
				  probability=0.5):
		"""
		Computes and displays several scores to evaluate the classifier.

		Parameters:
		n_folds - number of folds for the cross validation
		n_examples - number of misclassified tweets to print for each dimension.
		top_features - set to True to print the top features for each dimension.
		probability - if this value is set, a tweet will be classified as 
					  positive only if the probability for it to be positive is
					  greater or equal to the given value.

		Return value:
		A dictionary containing the benchmark statistics.
		"""
		label_names = self.labels[0].keys()
		corpus = self.corpus.tolist()

		print "#### Mood Benchmark ####"
		print "Classifier: %s" % self.clf
		print "Labels: %s" % label_names

		total_stats = defaultdict(list)
		for label in label_names:
			print "==== Label: %s [%d folds] ====" % (label, n_folds)
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

				y_pred_proba = self.clf.predict_proba(X_test)[:, 1]
				y_pred = map(lambda x: 0 if x < probability else 1,
							 y_pred_proba)

				hascoef = False
				if hasattr(self.clf, 'coef_'):
					hascoef = True

				scores['nb_pos'].append(sum([1 for x in y_test if x == 1]))
				scores['nb_neg'].append(sum([1 for x in y_test if x == 0]))
				scores['acc'].append(metrics.accuracy_score(y_test, y_pred))
				scores['f1'].append(metrics.f1_score(y_test, y_pred,
													 average='macro'))
				scores['prec'].append(metrics.precision_score(y_test, y_pred,
															  average='macro'))
				scores['rec'].append(metrics.recall_score(y_test, y_pred,
														  average='macro'))
				scores['rocauc'].append(metrics.roc_auc_score(y_test, y_pred))
				scores['confusion'].append(metrics.confusion_matrix(y_test,
																	y_pred))
				if hascoef:
					scores['weight'].append(self.clf.coef_[0])
				if n_examples > 0:
					for j in range(0, len(y_test)):
						if y_test[j] != y_pred[j]:
							wrong_class.add(test_index[j])

			self.scores = scores
			left = 12
			right = 15

			posneg = str(sum(scores['nb_pos'])) + "/"
			posneg += str(sum(scores['nb_neg']))

			print("Pos/Neg:".ljust(left) + posneg.ljust(right))

			print("Accuracy:".ljust(left)
				  + str(np.mean(scores['acc'])).ljust(right))

			print("F1:".ljust(left) + str(np.mean(scores['f1'])).ljust(right))

			print("Precision:".ljust(left)
				  + str(np.mean(scores['prec'])).ljust(right))

			print("Recall:".ljust(left)
				  + str(np.mean(scores['rec'])).ljust(right))

			print("ROC AUC:".ljust(left)
				  + str(np.mean(scores['rocauc'])).ljust(right))

			print("Confusion Matrix:".ljust(left))
			reduced_cm = reduce(np.add, scores['confusion'])
			print(str(reduced_cm))

			if n_examples:
				print
				print "--- %d Misclassified Tweets ---" % n_examples

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
				print "True: %s / Pred: %s" % (true_class, pred_class)
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
						ft = self.vectorizer.get_feature_names()[ft_idx[k]]
						ft = ft.encode('ascii', 'ignore')
						w = ft_w[k]
						print ("\t" + ft + ": ").ljust(left) \
						+ str(w).ljust(right)
			if n_examples:
				print

			if top_features:
				print
				if hascoef:
					top_features_mean = reduce(np.add, scores['weight'])/n_folds
					print "--- Top 50 features [over %d]: ---" % len(top_features_mean)
					feature_names = [self.vectorizer.get_feature_names()[x]
									 for x in
									 self.features_selection.get_support(True)]
					top50 = np.argsort(top_features_mean)[-50:]
					for idx in top50:
						print("\t" + feature_names[idx].ljust(15)
							  + str(top_features_mean[idx]).ljust(10))
				else:
					print("Error while printing the top features: the classifier does not have a coef_ attribute.")
				print

			total_stats['acc'].append(np.mean(scores['acc']))
			total_stats['f1'].append(np.mean(scores['f1']))
			total_stats['prec'].append(np.mean(scores['prec']))
			total_stats['rec'].append(np.mean(scores['rec']))
			total_stats['rocauc'].append(np.mean(scores['rocauc']))

		returned_stats = {}
		for s in total_stats:
			returned_stats[s] = np.mean(total_stats[s])
		return returned_stats

	def _classifyUser_onethread(self, forbid, auto_hash, requested, sporty,
				    classifiers, users_dir, uids, label_names,
				    probability, i, stdout_lock, raw=False):
		def print_results(t):
			stdout_lock.acquire()
			uid = t[0]
			scores = t[1]
			if raw:
				print json.dumps(scores)
			else:
				print "%s,%s" % (uid, ",".join(map(str,scores)))
			sys.stdout.flush()
			stdout_lock.release()

		while True:
			uid = uids.get()
			if uid is None:
				logger.debug("%d - Exiting" % i)
				return
			logger.debug("%d - Processing %s" % (i, uid))
			utweets = Tweets(os.path.join(users_dir, str(uid)))

			# removing sport tracker tweets
			no_sport_utweets = utweets.filter_on_hashtags(forbid)
			if no_sport_utweets.size() < utweets.size(): 
				# some sporty tweets have been removed
				if not sporty:  # user is not supposed to be exercising
					logger.info("no_sport user %s is exercising" % uid)
					continue

			# removing tweets generated by well-known apps
			filtered_utweets = no_sport_utweets.filter_on_hashtags(auto_hash)
			score_denom = filtered_utweets.size()

			poms_tweets = filtered_utweets.tolist()
			if requested:
				poms_tweets = filtered_utweets.filter_on_contains(requested).tolist()

			if not poms_tweets:
				logger.info("no tweets for %s" % uid)
				continue
			else:
				user = poms_tweets[0]['user']
				if user['lang'] != 'en':
					logger.info("user %s lang is not en" % uid)
					continue
			X = self.buildX(poms_tweets, predict=True)
			
			preds = []
			for label in label_names:
				# raw predicted probability scores
				if raw:
					preds.append(classifiers[label].predict_proba(X).tolist())
				# classification
				else:
					y_pred_proba = classifiers[label].predict_proba(X)[:, 1]
					pred = map(lambda x: 0 if x < probability else 1,
							   y_pred_proba)
					ones = float(np.count_nonzero(pred))
					score = ones/score_denom
					preds.append(score)
			print_results((uid,preds))

	def classifyUser(self, users_dir, uids, forbid=set(), probability=0.5,
					 sporty=False, poms=False, raw=False):
		"""
		Classify a list of users by individually classifying their tweets.

		Parameters:
		users_dir - path to the directory where the tweets are stored for every 
					user
		uids - list of user IDs to process
		forbid - set of forbidden hashtags, tweets that have a hashtag in this 
				 set will not be classified
		probability - if this value is set, a tweet will be classified as 
					  positive only if the probability for it to be positive is
					  greater or equal to the given value.
		sporty - True if the users are sporty users, False otherwise.

		Return value:
		A list containing the scores on every POMS dimension for every given
		user.
		"""
		if type(uids) != list:
			return self.classifyUser(users_dir, [uids])

		# Build classifiers for each dimension
		label_names = self.labels[0].keys()
		classifiers = {}
		for label in label_names:
			X_train = self.X
			y_train = np.array([d[label] for d in self.labels])
			self.clf.fit(X_train, y_train)
			classifiers[label] = copy.deepcopy(self.clf)

		auto_hash = set(['foursquare', 'yelp'])
		requested = None
		if poms:
			poms_AH = set(poms.keys['AH'])
			poms_DD = set(poms.keys['DD'])
			poms_TA = set(poms.keys['TA'])
			requested = poms_AH | poms_DD | poms_TA
		proc_count = 1 #multiprocessing.cpu_count()
		uids_q = Queue()
		stdout_lock = Lock()
		processes = []
		# Copy uids to process into task queue
		for uid in uids:
			uids_q.put(uid)
		# Add kill pill tasks to the task queue so that the workers exit
		for i in range(proc_count):
			uids_q.put(None)
		# Run the jobs
		for i in range(proc_count):
			p = Process(target=self._classifyUser_onethread,
				    args=(forbid, auto_hash, requested, sporty, classifiers,
					  users_dir, uids_q, label_names, probability, i,
					  stdout_lock, raw))
			processes.append(p)
			p.start()
		for p in processes:
			p.join()

	def match_users(self, sport_file, no_sport_file, match_file, random_file=None):
		"""
		Concatenate the scores of the exercising user and its match.

		Parameters:
		sport_file - file containing the results of the classification for the exercising users
		no_sport_file - file containing the results of the classification for the non exercising users
		match_file - file containing the pair of users exercising/match
		random_file - optional file containing the results of the classification for the random users
		"""
		sfd = open(sport_file)
		nsfd = open(no_sport_file)
		mfd = open(match_file)
		s_scores = {}
		ns_scores = {}
		matches = {}
		r_scores = {}
		for line in sfd:
			row = line.strip().split(",")
			if len(row) != 4:
				continue
			uid = row[0]
			s_scores[uid] = map(float, row[1:])
		for line in nsfd:
			row = line.strip().split(",")
			if len(row) != 4:
				continue
			uid = row[0]
			ns_scores[uid] = map(float, row[1:])
		for line in mfd:
			row = line.strip().split(",")
			if len(row) != 3:
				continue
			uid = row[0]
			matches[uid] = row[1]
		sfd.close()
		nsfd.close()
		mfd.close()

		if random_file:
			with open(random_file) as rfd:
				for line in rfd:
					row = line.strip().split(",")
					uid = row[0]
					r_scores[uid] = map(float, row[1:])

		def any_zero(l):
			for item in l:
				if item == 0.:
					return True
			return False

		def all_zeros(l):
			for item in l:
				if item != 0:
					return False
			return True

		random_header = ",r,r_AH,r_DD,r_TA,r_avg" if random_file else ""
		random_idx = 0
		rids = r_scores.keys()
		print "u,u_AH,u_DD,u_TA,u_avg,m,m_AH,m_DD,m_TA,m_avg%s" % random_header
		for u in matches:
			if u in s_scores:
				uscores = s_scores[u]
				# if all_zeros(uscores):
				# 	continue
				# find match in ns_scores
				m = matches[u]
				if m in ns_scores:
					mscores = ns_scores[m]
					# if all_zeros(mscores):
					# 	continue
					toprint = [u]
					toprint += uscores
					toprint.append(np.average(uscores))
					toprint.append(m)
					toprint += mscores
					toprint.append(np.average(mscores))
					if random_file:
						rid = 0
						rscores = [0.,0.,0.]
						if random_idx < len(rids):
							rid = rids[random_idx]
							rscores = r_scores[rid]
							random_idx += 1
						toprint.append(rid)
						toprint += rscores
					print ",".join(map(str, toprint))
