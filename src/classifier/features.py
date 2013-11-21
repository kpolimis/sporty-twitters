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

def tweets2features(tweets, bigrams=False, cutoff=3000, split=0.75):
	if bigrams:
		cutoff_unigrams = int(cutoff*split)
		cutoff_bigrams = int(cutoff-cutoff_unigrams)
	else:
		cutoff_unigrams = cutoff

	# Getting unigrams
	wordlist = get_words_in_tweets(tweets)
	wordlist = nltk.FreqDist(wordlist)
	unigram_feats = wordlist.keys()[:cutoff_unigrams]

	bigram_feats = []
	if bigrams:
		# Getting bigrams
		bigramslist = get_bigrams_in_tweets(tweets)
		bigramslist = nltk.FreqDist(bigramslist)
		bigram_feats = bigramslist.keys()[:cutoff_bigrams]

	return unigram_feats + bigram_feats
