import nltk
	
def get_words_in_tweets(tweets):
	all_words = []
	for (words, sentiment) in tweets:
		all_words.extend(words)
	return all_words

def get_bigrams_in_tweets(tweets):
	all_bigrams = []
	for (words, sentiment) in tweets:
		all_bigrams.extend(nltk.bigrams(words))
	return all_bigrams

def tweets2features(tweets, bigrams=False, cutoff=3000, split=0.9):
	features = {'unigrams':[], 'bigrams':[]}
	cutoff_unigrams = cutoff*split
	cutoff_bigrams = cutoff-cutoff_unigrams

	# Getting unigrams
	worldist = get_words_in_tweets(tweets)
	wordlist = nltk.FreqDist(wordlist)
	features['unigrams'] = wordlist.keys()[:cutoff_unigrams]

	# Getting bigrams
	bigramslist = get_bigrams_in_tweets(tweets)
	bigramslist = nltk.FreqDist(bigramslist)
	features['bigrams'] = bigramslist.keys()[:cutoff_bigrams]

	return features

