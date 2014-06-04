# Sporty Twitters

## Abstract

This project has been realized on a 6 month period (2014/1 - 2014/7) at the Illinois Institute of Technology. It has been supervised by [Dr. Aron Culotta](http://cs.iit.edu/~culotta/).

The goal of this project is to find a correlation between the well-being of a person and the fact that this person regularly exercises.

This project relies on machine learning techniques, it uses the Twitter API to collect data on users, and it depends of sport tracking apps (RunKeeper, Nike+, ...) to detect sportive users.

## Installation

This project is written in Python and uses the following packages:

- [sklearn](http://scikit-learn.org/stable/)
- [nltk](http://www.nltk.org/)
- [TwitterAPI](https://github.com/geduldig/TwitterAPI)
- [docopt](http://docopt.org/)

<!-- TODO: setup.py -->

## Usage

This project has been developed with the idea that it could be tweaked by developers that want to adapt this project to their need. To facilitate this, the sporty API has been developed. Moreover, it was also convenient to have an easy-to-use method to run the several experiments of this project without having to code it every time using the API. That is why the Command-Line Interface (CLI) has been developed.

### Sporty API

The sporty API centralizes all of the projects APIs which are mood, user, and tweets.

#### Mood API

This API as a variable expandVocabularyClass that defines the method to use to expand the vocabulary. The choices for this variable has stored in expand_vocabulary.py: it can be ContextSimilar (default value), WordNet, or Cooccurences.

- `expandVocabulary(vocabulary, corpus, n=20)`
    - `vocabulary`: vocabulary to expand
    - `corpus`: corpus used to expand the vocabulary
    - `n`: number of words to generate for each word in the vocabulary
- `buildFeatures(corpus, keep_rt=True, labels=False)`
    - `corpus`: corpus used to build the features
    - `keep_rt`: flag set to True if the user wants to keep the retweets to build the features
    - `labels`: as this function can also get the labels of each tweet in the corpus, this field describes the name(s) of the label(s). It is false (default value), no label is retrieved.
- `buildVectorizer(vec_type='tfidf', options={})`
- `train()`
- `predict(X_pred)`
- `benchmark(cv=5, scorings=['accuracy', 'f1', 'precision', 'recall', 'roc_auc'])`

#### Tweets API

- `load(input_file)`
- `authenticate()`
- `collect(tracked_words, output_file=None, mode='a+', count=0, lang=["en-EN", "en", "en-CA","en- -GB"], locations=None)`
- `filter(n, words, each_word=True, output_file=None, mode='a+', rt=True)`
- `label(labels, output_file=None, begin_line=0)`

#### User API 

- `getFriends()`
- `collectTweets(count=3200, output_file=None, mode='a+')`

### CLI

The CLI has been built using the [docopt](http://docopt.org/) package and relies on the sporty API. The current usage for the CLI is the following:

    Usage: cli -h | --help
       cli mood benchmark <labeled_tweets> [-s SW] [-e E] [-b] [--no-AH --no-DD --no-TA] [--min-df=M] 
       cli mood label <input_tweets> <labeled_tweets> [-l L] [--no-AH --no-DD --no-TA]
       cli tweets collect <settings_file> <output_tweets> <track_file> [<track_file>...] [-c C]
       cli tweets filter <input_tweets> <output_tweets> <track_file> [<track_file>...] [-c C] [--each] [--no-rt]
       cli users collect_tweets <settings_file> <user_ids_file> <output_dir> [-c C]
       cli users list_friends <settings_file> <user_ids_file> <output_dir>

    Options:
        -h, --help              Show this screen.
        --each                  Filter C tweets for each of the tracked words
        --min-df=M              See min_df from sklearn vectorizers [default: 1]
        --no-AH                 Do not label tweets on Anger/Hostility dimension
        --no-DD                 Do not label tweets on Depression/Dejection dimension
        --no-TA                 Do not label tweets on Tension/Anxiety dimension
        --no-rt                 Remove retweets when filtering
        -b, --binary            No count of features, only using binary features.
        -c C, --count=C         Number of tweets to collect/filter [default: 3200]
        -e E, --emoticons=E     Path to file containing the list of emoticons to keep
        -l, --begin-line=L      Line to start labeling the tweets [default: 0]
        -s SW, --stopwords=SW   Path to file containing the stopwords to remove from the corpus 