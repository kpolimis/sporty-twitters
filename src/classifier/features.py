import nltk

def get_words_in_tweets(tweets):
        all_words = []
        for (words, sentiment) in tweets:
                all_words.extend(words)
        return all_words

def get_word_features(wordlist, cutoff):
        wordlist = nltk.FreqDist(wordlist)
        word_features = wordlist.keys()
        return word_features[:cutoff]

def tweets2features(tweets, cutoff):
	return get_word_features(get_words_in_tweets(tweets), cutoff)