import sporty.sporty as sporty
import sporty.utils as utils
from sporty.datastructures import *
import argparse
import sys
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Command Line Interface for the sporty twitter project')
    # list of actions
    parser.add_argument('action',
                        type=str,
                        choices=['collect', 'label', 'benchmark'],
                        default='collect',
                        help='action to execute (default: collect)')
    # input(s)
    parser.add_argument('--input', '-i',
                        type=file,
                        help='path to input file(s) (default to sys.stdin)',
                        default=sys.stdin,
                        nargs='+')
    # output(s)
    parser.add_argument('--output', '-o',
                        type=argparse.FileType('a+'),
                        help='path to output file(s) (default to sys.stdout)',
                        default=sys.stdout,
                        nargs='+')
    # collect group
    collect_group = parser.add_argument_group('Collect tweets given words to track')
    collect_group.add_argument('--settings', '-s',
                               type=file,
                               help='path to settings file containing twitter key and token',
                               default=None)
    collect_group.add_argument('--count', '-c',
                               type=int,
                               help='action = collect: count of tweets to collect',
                               default=0)
    # label group
    label_group = parser.add_argument_group('Label a list of tweets')
    label_group.add_argument('--label-name', '-ln', dest='ln',
                             type=str,
                             help='name of the label(s)',
                             nargs='+')
    label_group.add_argument('--label-values', '-lv', dest='lv',
                             type=int,
                             help='possible values for the label(s)',
                             nargs='+')
    label_group.add_argument('--begin', '-b',
                             type=int,
                             help='line number to begin labeling',
                             default=0)
    # benchmark group
    benchmark_group = parser.add_argument_group('Benchmark a classifier')
    benchmark_group.add_argument('--stopwords', '-sw',
                                 type=file,
                                 help='path to the stopwords file',
                                 default=None)
    benchmark_group.add_argument('--min-df', 
                                 dest='mindf',
                                 type=int,
                                 default=5)
    # # filter group
    # filter_group = parser.add_argument_group('Get N tweets amongst a bulk of tweets by filtering on keywords')
    # filter_group.add_argument('n', type=int, default=10,
    #                           help='')

    args = parser.parse_args()

    if args.action == 'collect':
        if args.settings:
            api = sporty.api(settings_file=args.settings)
            totrack = []
            for i in args.input:
                totrack += LSF(i).tolist()
            totrack = set(totrack) # remove duplicates
            api.collect(totrack, args.output, count=args.count)
        else:
            raise Exception("No settings file defined, required to launch the tweets collect.")
    elif args.action == 'label':
        if args.ln and args.lv:
            api = sporty.api()
            input_file = args.input[0]
            output_file = args.output[0]
            api.load(input_file)
            labels = {l:args.lv for l in args.ln}
            api.label(labels, output_file, args.begin)
        else:
            raise Exception("Label name(s) and values are required when labeling tweets.")
    elif args.action == 'benchmark':
        if args.ln and args.lv:
            api = sporty.api()
            input_file = args.input[0]
            labels = {l:args.lv for l in args.ln}
            if len(labels.keys()) > 1:
                api.mood.clf = OneVsRestClassifier(SVC(kernel='linear'))
            tweets = Tweets(input_file)
            corpus = utils.Cleaner(stopwords=LSF(args.stopwords).tolist()).clean(tweets)

            tfidf_options = {'min_df': args.mindf}
            api.buildFeatures(corpus, labels=labels.keys())
            api.buildVectorizer()
            api.train()
            api.benchmark(cv=2)
        else:
            raise Exception("Label name(s) and values are required when labeling tweets.")
