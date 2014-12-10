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
		"""
		super(Tweets, self).__init__()
		self.index = 0	# cursor pointing to the next tweet to return
		self._load(tw_in, mode)

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
		return Tweets(filtered)

	def filter_on_hashtags(self, hashtags):
		f = lambda tw: not(hashtags & set([h['text'].lower()
						   for h in tw['entities']['hashtags']]))
		return self.filter(f)

	def filter_on_contains(self, words):
		f = lambda tw: words & set(w.lower() for w in tw['text'].split())
		return self.filter(f)

	def size(self):
		return len(self.tolist())

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
			cases = {
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
	Tool to load a tabulation-separated values (TSV) file into several
	dictionaries. It can be used to:
		- load the POMS vocabulary
		- load the emoticons
		- etc
	Each element of these vocabularies is associated to a category and a category
	can have many elements. This data structure gives access to two dictionaries:
		- keys: store the belonging elements for every category
		- values: store the associated category for every elements
	"""
	def __init__(self, tsv_file):
		"""
		Parameters:
		tsv_file - the TSV file to load
		"""
		super(TSV, self).__init__()
		self.tsv_file = tsv_file
		self.keys = defaultdict(list)
		self.values = {}
		self.load()

	def load(self):
		"""
		Loads the TSV file in the dictionaries.

		Return value:
		True if the file has been properly loaded, False otherwise.
		"""
		if not self.tsv_file:
			return
		tsv_type = type(self.tsv_file) if self.tsv_file else None
		cases = {
				  str: lambda: open(self.tsv_file),
				  file: lambda: self.tsv_file
				}
		if tsv_type in cases.keys():
			tsv_file = cases[tsv_type]()
		else:
			logging.error("Input type not suported for TSV. Is %s but should be one of %s." % (tsv_type, repr(cases.keys())))
			return False

		linecount = 0
		for line in tsv_file:
			linecount += 1
			fields = re.split("\s+", line.strip())
			if len(fields) > 1:
				self.keys[fields[0]].append(fields[1])
				self.values[fields[1]] = fields[0]
			else:
				logging.warning("Only %d field(s) on line %d of the TSV file." % (len(fields), linecount))
		return True

class LSF(object):
	"""
	Tool to load a Line-Separated File. This kind of file contains a list of
	words, one word on each line.
	"""
	def __init__(self, input_file):
		"""
		Initializes the LSF instance by loading the input file.

		Parameters:
		input_file - file to read to store its content in memory
		"""
		super(LSF, self).__init__()
		self.input_file = input_file
		self.words = []
		self.load()

	def load(self):
		"""
		Load the input file in memory

		Return value:
		True if the file has been properly loaded, False otherwise.
		"""
		if not self.input_file:
			return
		type_lsf = type(self.input_file) if self.input_file else None
		cases = {
				  str: lambda: open(self.input_file),
				  file: lambda: self.input_file
				}
		if type_lsf in cases.keys():
			input_file = cases[type_lsf]()
		else:
			logging.error("Input type not suported for LSF. Is %s but should be one of %s." % (type_lsf, repr(cases.keys())))
			return False

		for line in input_file:
			self.words.append(line.strip())
		return True

	def tolist(self):
		return self.words
