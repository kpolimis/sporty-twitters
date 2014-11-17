from collections import defaultdict
import json
import os
import re
import sys
import logging

class Tweets(object):
	"""
	Manages a list of tweets loaded from a file or a list.
	Makes it possible to iterate over tweets using a unique structure when
	tweets are in a Python list or stored on disk in a file.
	"""

	def __init__(self, tw_in=None, mode='a+'):
		"""
		Initializes an instance by loading file/list.

		Parameters:
		tw_in - Object from which the input tweets are read.
		mode - Opening mode if tw_in is a file path, useless otherwise.

		Return value:
		True if the tweets have been correctly loaded, False otherwise.
		"""
		super(Tweets, self).__init__()
		self.index = 0	# cursor pointing to the next tweet to return
		return self._load(tw_in, mode)

	def _load(self, tw_in=None, mode='a+'):
		"""
		Switches on the possible types of tweets input to correctly load the
		tweets.

		Parameters:
		tw_in - Object from which the input tweets are read.
		mode - Opening mode if tw_in is a file path, useless otherwise.

		Return value:
		True if the tweets have been correctly loaded, False otherwise.
		"""
		cases = { 
				  None: (lambda: [], False),
				  list: (lambda: tw_in, False),
				  file: (lambda: tw_in, True),
				  str: 	(lambda: open(tw_in, mode), True)
				}
		input_type = None if tw_in == None else type(tw_in)
		if input_type in cases.keys():
			self.tweets = cases[input_type][0]()
			self.lazy = cases[input_type][1]
			return True
		else:
			logging.error("Tweets input mode not supported. Is %s and should be one of %s." % (type(tw_in), repr(cases.keys())))
			return False

	def __iter__(self):
		return self

	def next(self):
		"""
		Return value:
		A dictionary object containing the informations of the next tweet to be
		returned.
		"""
		# case when tweets are stored on disk
		if self.lazy:
			line = self.tweets.readline()
			if line:
				data = json.loads(line.strip())
			else:
				raise StopIteration
		# case when tweets are stored in a Python list
		else:
			try:
				data = self.tweets[self.index]
			except IndexError:
				index = 0
				raise StopIteration
			self.index += 1
		return data

	def tolist(self):
		"""
		Transform the tweets in a list.If the tweets are stored on disk, it loads
		all the tweets sequentially making the lazy loading mode useless.

		Return value:
		A list containing all the input tweets.
		"""
		if type(self.tweets) == list:
			return self.tweets
		else:
			self.tweets.seek(0)
			tweets_list = [json.loads(line.strip()) for line in self.tweets]
			return tweets_list

	def filter(self, f=None):
		"""
		Filter the list of tweets using a given function.

		Parameters:
		f - the filtering function

		Return value:
		A list containing the tweets for which the filtering function f returns
		True.
		"""
		tweets = self.tolist()
		if f is None:
			return tweets
		else:
			filtered = filter(f, tweets)
		return filtered

	def append(self, tw):
		"""
		Appends a given tweet to the list of tweets. If the tweets are stored
		in a file on disk, then the appended tweet is written at the end of the
		file.

		Parameters:
		tw - the tweet to append, either in a dictionary or as directly as a
			 string when the lazy opening mode is on, any object when the lazy
			 mode is off.

		Return value:
		True if the tweet has been properly appended, False otherwise.
		"""
		if self.lazy:
			self.tweets.seek(0, os.SEEK_END)
			cases : {
					  dict: lambda: self.tweets.write(json.dumps(tw) + "\n"),
					  str: lambda: self.tweets.write(tw + "\n")
					}
			tw_type = type(tw)
			if tw_type in cases.keys():
				cases[tw_type]()
				self.tweets.flush()
			else:
				logging.error("Tweet type not supported. ")
				return False
		else:
			self.tweets.append(tw)
		return True

class TSV(object):
	"""
	Tool to load a TSV file into several dictionaries. It is used in this
	project to load the POMS vocabulary and the emoticons. Each word of these
	vocabularies belong to a category. This data structure give access to a
	dictionary 'keys' that maps a category to a list of words belonging to
	this category, and a dictionary 'values' that maps each word in the
	vocabulary to the category it belongs to.
	"""
	def __init__(self, tsv_file):
		"""
		Initializes an TSV instance by loading a TSV file.
		"""
		super(TSV, self).__init__()
		self.tsv_file = tsv_file
		self.keys = defaultdict(list)
		self.values = {}
		self.load()

	def load(self):
		"""
		Loads the TSV file in the dictionaries.
		"""
		if not self.tsv_file:
				return
		if type(self.tsv_file) == str:
			tsv_file = open(self.tsv_file)
		elif type(self.tsv_file) == file:
			tsv_file = self.tsv_file
		else:
			raise Exception("Unsupported type for TSV file.")
		for line in tsv_file:
			fields = re.split("\s+", line.strip())
			if len(fields) > 1:
				self.keys[fields[0]].append(fields[1])
				self.values[fields[1]] = fields[0]


class LSF(object):
	"""
	Tool to load a Line-Separated File. This kind of file contains a list of
	words, one word on each line.
	"""
	def __init__(self, input_file):
		"""
		Initializes the LSF instance by loading the input file.
		"""
		super(LSF, self).__init__()
		self.input_file = input_file
		self.words = []
		self.load()

	def load(self):
		if not self.input_file:
			return
		if type(self.input_file) == str:
			input_file = open(self.input_file)
		elif type(self.input_file) == file:
			input_file = self.input_file
		else:
			raise Exception("Unsupported type for input file.")
		for line in input_file:
			self.words.append(line.strip())

	def tolist(self):
		return self.words
