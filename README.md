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

To install it, just clone this github repo, and run the following command:

    python setup.py install

## Usage

This project has been developed with the idea that it could be tweaked by developers that want to adapt this project to their need. To facilitate this, the sporty API has been developed. Moreover, it was also convenient to have an easy-to-use method to run the several experiments of this project without having to code it every time using the API. That is why the Command-Line Interface (CLI) has been developed.

### CLI

The CLI has been built using the [docopt](http://docopt.org/) package and relies on the sporty API. The current usage for the CLI is the following:

    Usage: 
        sporty -h | --help
        sporty mood benchmark <labeled_tweets> [-s SW] [-e E] [-b] [--no-AH --no-DD --no-TA] [--min-df=M] 
        sporty mood label <input_tweets> <labeled_tweets> [-l L] [--no-AH --no-DD --no-TA]
        sporty tweets collect <settings_file> <output_tweets> <track_file> [<track_file>...] [-c C]
        sporty tweets filter <input_tweets> <output_tweets> <track_file> [<track_file>...] [-c C] [--each] [--no-rt]
        sporty users collect_tweets <settings_file> <user_ids_file> <output_dir> [-c C]
        sporty users list_friends <settings_file> <user_ids_file> <output_dir>

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