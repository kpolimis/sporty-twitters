# Sporty Twitters

## Abstract

This project has been realized on a 6 month period (2014/1 - 2014/7) at the Illinois Institute of Technology. It has been supervised by [Dr. Aron Culotta](http://cs.iit.edu/~culotta/).

The goal of this project is to find a correlation between the well-being of a person and the fact that this person regularly exercises.

This project relies on machine learning techniques, it uses the Twitter API to collect data on users, and it depends of sport tracking apps (RunKeeper, Nike+, ...) to detect sportive users.

## Installation

This project is written in Python and uses the following packages:

- [sklearn](http://scikit-learn.org/stable/)
- [TwitterAPI](https://github.com/geduldig/TwitterAPI)
- [docopt](http://docopt.org/)

To install it, just clone this github repo, and run the following command:

    python setup.py install

## Usage

This project has been developed with the idea that it could be tweaked by developers that want to adapt this project to their need. To facilitate this, the sporty API has been developed. Moreover, it is often convenient to have an easy way to run the several experiments from a terminal instead of having to code it every time using the API: that is the purpose of the Command-Line Interface (CLI).

### CLI

The CLI has been built using the [docopt](http://docopt.org/) package and relies on the sporty API. The current usage for the CLI is the following:

```
Usage: cli -h | --help
       cli mood benchmark <labeled_tweets> [-bmptu] [-s SW] [-e E] [--no-AH --no-DD --no-TA]
                          [--min-df=M] [--n-folds=K] [--n-examples=N] [--clf=C [--clf-options=O]]
                          [--reduce-func=R] [--features-func=F] [--liwc=L] [-k K] [--roc=R]
                          [--proba=P]
       cli mood label <input_tweets> <labeled_tweets> [-l L] [--no-AH --no-DD --no-TA]
       cli tweets collect <settings_file> <output_tweets> <track_file> [<track_file>...] [-c C]
       cli tweets filter <input_tweets> <output_tweets> <track_file> [<track_file>...] [-c C]
                         [--each] [--no-rt]
       cli users collect_tweets <settings_file> <user_ids_file> <output_dir> [-c C]
       cli users list_friends <settings_file> <user_ids_file> <output_dir>
       cli users show <settings_file> <input_dir>

Options:
    -h, --help              Show this screen.
    --clf=C                 Classifier type to use for the task: can be 'logistic-reg', 'svm',
                            'decision-tree', 'naive-bayes', 'kneighbors'
    --clf-options=O         Options for the classifier in JSON
    --each                  Filter C tweets for each of the tracked words
    --liwc=L                Path to the LIWC dictionary
    --min-df=M              See min_df from sklearn vectorizers [default: 1]
    --n-examples=N          Number of wrong classified examples to display [default: 0]
    --n-folds=K             Number of folds [default: 3]
    --no-AH                 Do not label tweets on Anger/Hostility dimension
    --no-DD                 Do not label tweets on Depression/Dejection dimension
    --no-TA                 Do not label tweets on Tension/Anxiety dimension
    --no-rt                 Remove retweets when filtering
    --proba=P               Classify a tweet as positive only if the probability to be positive
                            is greater than P
    --roc=R                 Plot the ROC curve with R the test set size given as a ratio
                            (e.g. 0.2 for 20 percent of the data) and return. Note: the benchmark
                            is not run.
    -b, --binary            No count of features, only using binary features.
    -c C, --count=C         Number of tweets to collect/filter [default: 3200]
    -e E, --emoticons=E     Path to file containing the list of emoticons to keep
    -f F, --features-func=F List of functions to execute amongst the functions of the
                            FeatureBuilder class. The functions of this list will begin
                            executed in order.
    -k K, --k-features=K    Number of features to keep during the features selection [default: 100]
    -l, --begin-line=L      Line to start labeling the tweets [default: 0]
    -m                      Keep mentions when cleaning corpus
    -p                      Keep punctuation when cleaning corpus
    -r R, --reduce-func=R   Function that will be used to reduced the labels into one general
                            label (e.g. 'lambda x, y: x or y')
    -s SW, --stopwords=SW   Path to file containing the stopwords to remove from the corpus
    -t, --top-features      Display the top features during the benchmark
    -u                      Keep URLs when cleaning corpus
```