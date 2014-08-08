"""
Usage: cli -h | --help
       cli mood benchmark <labeled_tweets> [-bmptu] [-s SW] [-e E] [-k K]
                          [--min-df=M] [--n-folds=K] [--n-examples=N]
                          [--clf=C [--clf-options=O]] [--proba=P] [--roc=R]
                          [--reduce-func=R] [--features-func=F] [--liwc=L]
       cli mood label <input_tweets> <labeled_tweets> [-l L]
       cli mood predict_user <labeled_tweets> <users_dir> <user_ids_file>
                            [-bmptu] [-s SW] [-e E] [--liwc=L]
                            [--forbid=F] [--clf=C [--clf-options=O]]
                            [--proba=P] [--min-df=M] [--reduce-func=R]
                            [--features-func=F]
       cli tweets collect <settings_file> <output_tweets> <track_file>
                          [<track_file>...] [-c C]
       cli tweets filter <input_tweets> <output_tweets> <track_file>
                         [<track_file>...] [-c C] [--each] [--no-rt]
       cli users collect_tweets <settings_file> <user_ids_file> <output_dir>
                                [-c C]
       cli users list_friends <settings_file> <user_ids_file> <output_dir>
       cli users most_similar <user_ids_file> <users_dir> <friends_dir>
                              [--no-tweets]
       cli users show <settings_file> <input_dir>

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
    --liwc=L                Path to the LIWC dictionary [default: /data/1/lexicons/liwc.dic]
    --min-df=M              See min_df from sklearn vectorizers [default: 3]
    --n-examples=N          Number of wrongly classified examples to display
                            [default: 0]
    --n-folds=K             Number of folds for the cross validation
                            [default: 3]
    --no-rt                 Remove retweets when filtering
    --no-tweets             Do not use the tweets of the users to infer their
                            location
    --proba=P               Classify a tweet as positive only if the
                            probability to be positive is greater than P [default: 0.91]
    --roc=R                 Plot the ROC curve with R the test set size given
                            as a ratio (e.g. 0.2 for 20 percent of the data)
                            and return. Note: the benchmark is not run
    -b, --binary            No count of features, only using binary features
    -c C, --count=C         Number of tweets to collect/filter [default: 3200]
    -e E, --emoticons=E     Path to file containing the dictionary of emoticons
                            [default: /home/virgile/sporty-twitters/inputs/params/emoticons]
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
"""
import sporty.sporty as sporty
from sporty.datastructures import *
from sporty.tweets import Tweets
from sporty.utils import FeaturesBuilder
from docopt import docopt
import sys
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.multiclass import OneVsRestClassifier
import os.path
from os import listdir


def main(argv=None):
    args = docopt(__doc__, argv)
    api = sporty.api()
    if args['tweets']:
        # Concatenate the words to track
        totrack = set()
        for i in args['<track_file>']:
            totrack = totrack.union(set(LSF(i).tolist()))

        if args['collect']:
            # Authenticate to the Twitter API
            api.tweets = sporty.tweets.api(args['<settings_file>'])
            api.tweets.collect(totrack, args['<output_tweets>'],
                               count=int(args['--count']))

        elif args['filter']:
            api.tweets.load(args['<input_tweets>'])
            api.tweets.filter(int(args['--count']), totrack,
                              each_word=args['--each'],
                              output_file=args['<output_tweets>'],
                              rt=not args['--no-rt'])

    elif args['users']:
        # Authenticate to the Twitter API
        api.users = sporty.users.api(args['<user_ids_file>'],
                                     args['<settings_file>'])
        if args['collect_tweets']:
            api.users.collectTweets(args['<output_dir>'], int(args['--count']))

        elif args['list_friends']:
            api.users.outputFriendsIds(args['<output_dir>'])

        elif args['show']:
            files = [os.path.join(args['<input_dir>'], f)
                     for f in listdir(args['<input_dir>'])
                     if os.path.isfile(os.path.join(args['<input_dir>'], f))
                     and f.find('extended') == -1]
            for f in files:
                if os.path.isfile(f + '.extended'):
                # friends list already exists for this user
                    continue
                with open(f + '.extended', 'w') as fout:
                    api.users.loadIds(f)
                    extended = api.users.extendFromIds()
                    for user in extended:
                        fout.write(json.dumps(user) + "\n")

        elif args['most_similar']:
            api.users.loadIds(args['<user_ids_file>'])
            most_similar_list = api.users.getSimilarFriends(args['<users_dir>'],
                                                            args['<friends_dir>'],
                                                            not args['--no-tweets'])
            # for entry in most_similar_list:
            #     print ";".join(map(str, entry))

    elif args['mood']:
        keys = ['AH', 'DD', 'TA']
        labels = {x: [0, 1] for x in keys}
        if args['label']:
            api.tweets.load(args['<input_tweets>'])
            api.tweets.label(labels, args['<labeled_tweets>'],
                             int(args['--begin-line']))

        elif args['benchmark'] or args['predict_user']:
            # Build the right classifier given the CLI options
            classifier_choices = {'logistic-reg': LogisticRegression,
                                  'svm': SVC,
                                  'decision-tree': DecisionTreeClassifier,
                                  'naive-bayes': GaussianNB,
                                  'kneighbors': KNeighborsClassifier}

            if not args['--clf']:
                # default classifier
                clf = LogisticRegression()
            elif args['--clf'] in classifier_choices.keys():
                clfoptions = {}
                if args['--clf-options']:
                    clfoptions = json.loads(args['--clf-options'])
                    # avoid raising exception when setting SVM kernel using CLI
                    if 'kernel' in clfoptions:
                        clfoptions['kernel'] = str(clfoptions['kernel'])
                clf = classifier_choices[args['--clf']](**clfoptions)
            else:
                raise Exception("Wrong value for clf: must be amongst "
                                + str(classifier_choices.keys()))
            api.mood.clf = clf

            # Build the cleaner options, the TF-IDF vectorizer options,
            # and the FeaturesBuilder options.
            cleaner_options = {'stopwords': args['--stopwords'],
                               'emoticons': args['--emoticons'],
                               'rm_mentions': not args['-m'],
                               'rm_punctuation': not args['-p'],
                               'rm_unicode': not args['-u']}
            tfidf_options = {'min_df': int(args['--min-df']),
                             'binary': args['--binary'],
                             'ngram_range': (1, 1),
                             'lowercase': False}
            # get the list of functions to run from the FeaturesBuilder
            if args['--features-func']:
                func_list = eval(args['--features-func'])
                for f in func_list:
                    if f not in dir(FeaturesBuilder):
                        raise Exception(f + " is not a function of "
                                        + "FeaturesBuilder.")
            else:
                func_list = None
            # get the reducing function
            if args['--reduce-func']:
                reduce_func = eval(args['--reduce-func'])
            else:
                reduce_func = None
            fb_options = {"labels": keys,
                          "labels_reduce_f": reduce_func,
                          "func_list": func_list,
                          "liwc_path": args['--liwc']}

            # Load the tweets
            tweets = Tweets(args['<labeled_tweets>'])

            # Build features and the vectorizer
            api.mood.buildX(tweets, int(args['--k-features']),
                            cleaner_options, fb_options, tfidf_options)

            # Plot the ROC curve if asked:
            if args['benchmark'] and args['--roc']:
                api.mood.ROC_curve(float(args['--roc']))
                return

            argproba = float(args['--proba'])

            if args['benchmark']:
                # Run the benchmark
                return args, api.mood.benchmark(int(args['--n-folds']),
                                                int(args['--n-examples']),
                                                args['--top-features'],
                                                argproba)
            elif args['predict_user']:
                user_ids = LSF(args['<user_ids_file>']).tolist()
                forbidden_words = set(LSF(args['--forbid']).tolist())
                return api.mood.classifyUser(args['<users_dir>'],
                                             user_ids,
                                             forbidden_words,
                                             argproba)
if __name__ == "__main__":
    main()
