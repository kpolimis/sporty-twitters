# Sporty Twitters

## Abstract

This project has been realized on a 6 month period (2014/1 - 2014/7) at the Illinois Institute of Technology. It has been supervised by [Dr. Aron Culotta](http://cs.iit.edu/~culotta/).

The goal of this project is to find a correlation between the well-being of a person and the fact that this person regularly exercises.

This project relies on machine learning techniques, it uses:

- the Twitter API to collect data on users,
- sport tracking apps (RunKeeper, Nike+, ...) to detect sportive users

## Installation

This project is written in Python and uses the following packages:

- [sklearn](http://scikit-learn.org/stable/) for the machine learning algorithms,
- [matplotlib](http://matplotlib.org/) to draw graphs in Python,
- [TwitterAPI](https://github.com/geduldig/TwitterAPI) to make requests to the Twitter API in Python,
- [docopt](http://docopt.org/) to easily implement a command-line interface.

The installation process requires three steps:

1. [Install scikit-learn](http://scikit-learn.org/stable/install.html). 
2. [Install matplotlib](http://matplotlib.org/faq/installing_faq.html#how-to-install)
3. Clone this github repository and install as usual:

	> git clone https://github.com/vlandeiro/sporty-twitters.git
	> cd sporty-twitters
	> python setup.py install

## Usage

This project has been developed with the idea that it could be tweaked by developers that want to adapt it to their need. To facilitate this, the sporty API has been developed so the different parts of this project can be integrated to existing code.

It is also convenient to have an easy way to run experiments from a terminal instead of having to code it every time using the API: that is the purpose of the Command-Line Interface (CLI).

### API

The project is divided in three sub-APIs: `users`, `tweets`, and `mood`. They are centralized in the `sporty` API in order to simplify the instanciation for a developer.

#### Users API

The `users` API centralizes all the actions related to the Twitter users. From a list of user identifiers (UID) `L`, it is possible to:

- Collect the tweets of every user in `L` with a maximum of 3200;
- Collect the UIDs of the friends of every user in `L` and save them on disk;
- Load the user object of every user in `L`;
- Load the friends (as user objects) of every user in `L`;
- Get the user object of every user in `L` using the Twitter API;
- Get the most similar friends of every user in `L`;
- Label each user of `L` on gender.

#### Tweets API

The `tweets` API focuses on the manipulation of tweet objects. The possible operations are the following:

- Load a corpus of tweets;
- Collect tweets using the Streaming API and store them on disk or on memory;
- Filter a corpus of tweets as follow: for each word in a list, it is going to keep `n` tweets that contain this word;
- Label a corpus of tweets.

#### Mood API

The `mood` API is centered on the study of the users' mood. It contains all of the machine learning part of the project. Thanks to this API, one can:

- Expand a vocabulary using different methods: WordNet or Context Similarity;
- Build a features vector to pass to a classifier;
- Train a classifier;
- Classify tweets once the classifier is trained;
- Draw and save on disk the ROC curve for a classifier;
- Run a benchmark of a classifier using n-folds cross validation.

### CLI

The CLI has been built using the [docopt](http://docopt.org/) package and relies on the sporty API.
It provides a lot of access to the API:

```
Usage: sporty-cli -h | --help
       sporty-cli mood benchmark <labeled_tweets> [-bmptu] [-s SW] [-e E] [-k K]
                          [--min-df=M] [--n-folds=K] [--n-examples=N]
                          [--clf=C [--clf-options=O]] [--proba=P] [--roc=R]
                          [--reduce-func=R] [--features-func=F] [--liwc=L]
       sporty-cli mood label <input_tweets> <labeled_tweets> [-l L]
       sporty-cli mood predict_user <labeled_tweets> <users_dir> <user_ids_file>
                            [-bmptu] [-s SW] [-e E] [--liwc=L]
                            [--forbid=F] [--clf=C [--clf-options=O]]
                            [--proba=P] [--min-df=M] [--reduce-func=R]
                            [--features-func=F] [--sporty] [--poms=P]
       sporty-cli mood match_users <sport_scores> <no_sport_scores> <user_match> [--rand=R]
       sporty-cli tweets collect <settings_file> <output_tweets> <track_file>
                          [<track_file>...] [-c C]
       sporty-cli tweets filter <input_tweets> <output_tweets> <track_file>
                         [<track_file>...] [-c C] [--each] [--no-rt]
       sporty-cli users collect_tweets <settings_file> <user_ids_file> <output_dir>
                                [-c C]
       sporty-cli users list_friends <settings_file> <user_ids_file> <output_dir>
       sporty-cli users most_similar <user_ids_file> <users_dir> <friends_dir>
                              [--no-tweets]
       sporty-cli users show <settings_file> <input_dir>
       sporty-cli stream collect <settings_file> [--lang=L] [-c C]

Options:
    -h, --help              Show this screen.
    --clf=C                 Classifier type to use for the task. Valid options
                            are 'logistic-reg', 'svm', 'decision-tree',
                            'naive-bayes', 'kneighbors'
    --clf-options=O         Options for the classifier as a string
                            representing a Python dictionary
    --each                  Filter C tweets for each of the tracked words
    --forbid=F              Path to a file containing a list of forbidden
                            words. If a tweet contains any of these words,
                            it will not be used for the classification
                            task.
    --lang=L                Language of the tweets to collect [default: en]
    --liwc=L                Path to the LIWC dictionary [default: /data/1/sporty/lexicons/liwc/liwc.dic]
    --min-df=M              See min_df from sklearn vectorizers [default: 3]
    --n-examples=N          Number of wrongly classified examples to display
                            [default: 0]
    --n-folds=K             Number of folds for the cross validation
                            [default: 10]
    --no-rt                 Remove retweets when filtering
    --no-tweets             Do not use the tweets of the users to infer their
                            location
    --poms=P                Path to the poms lexicon
    --proba=P               Classify a tweet as positive only if the
                            probability to be positive is greater than P [default: 0.91]
    --sporty                Flag to put when the users are expected to be exercising.
    --rand=R                Path to file containing the scores of the random users.
    --roc=R                 Plot the ROC curve with R the test set size given
                            as a ratio (e.g. 0.2 for 20 percent of the data)
                            and return. Note: the benchmark is not run
    -b, --binary            No count of features, only using binary features
    -c C, --count=C         Number of tweets to collect/filter [default: 3200]
    -e E, --emoticons=E     Path to file containing the dictionary of emoticons
                            [default: /data/1/sporty/lexicons/stopwords/emoticons]
    -f F, --features-func=F List of functions to execute amongst the functions
                            of the FeatureBuilder class. The functions of this
                            list will be executed in order
    -k K, --k-features=K    Number of features to keep during the features
                            selection [default: 160]
    -l, --begin-line=L      Line to start labeling the tweets [default: 0]
    -m                      Keep mentions when cleaning corpus
    -p                      Keep punctuation when cleaning corpus
    -r R, --reduce-func=R   Function that will be used to reduced the labels
                            into one general label (e.g. 'lambda x, y: x or y')
    -s SW, --stopwords=SW   Path to file containing the stopwords to remove
                            from the corpus
    -t, --top-features      Display the top features during the benchmark
    -u                      Keep URLs when cleaning corpus
```

Note that the CLI is divided in four parts:

1. `mood` to call functions from the Mood API,
2. `users` to call functions from the Users API,
3. `tweets` to call functions from the Tweets API,
4. `stream` to collect tweets by directly using the TwitterAPI module.