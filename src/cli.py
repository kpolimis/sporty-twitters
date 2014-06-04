"""
Usage: cli -h | --help
       cli tweets collect <settings_file> <output_tweets> <track_file> [<track_file>...] [--count=C]
       cli tweets filter <input_tweets> <output_tweets> <track_file> [<track_file>...] [--count=C] [--each] [--no-rt]
       cli users collect_tweets <settings_file> <user_ids_file> <output_dir> [--count=C]
       cli users list_friends <settings_file> <user_ids_file> <output_dir>
       cli mood label <input_tweets> <labeled_tweets> [--begin-line=L] [--no-AH --no-DD --no-TA]
       cli mood benchmark <labeled_tweets> [--stopwords=SW] [--emoticons=E] [--no-AH --no-DD --no-TA] [--min-df=M]

Options:
    -h, --help      Show this screen.
    --count=C       Number of tweets to collect/filter [default: 3200]
    --each          Filter C tweets for each of the tracked words
    --no-rt         Remove retweets when filtering
    --begin-line=L  Line to start labeling the tweets [default: 0]
    --no-AH         Do not label tweets on Anger/Hostility dimension
    --no-DD         Do not label tweets on Depression/Dejection dimension
    --no-TA         Do not label tweets on Tension/Anxiety dimension
    --stopwords=SW  Path to file containing the stopwords to remove from the corpus
    --emoticons=E   Path to file containing the list of emoticons to keep
    --min-df=M      See min_df from sklearn vectorizers [default: 1]
"""
import sporty.sporty as sporty
import sporty.utils as utils
from sporty.datastructures import *
from sporty.tweets import Tweets
from sporty.user import User
from docopt import docopt
import sys
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
import os.path

def main():
    args = docopt(__doc__)

    api = sporty.api()
    if args['tweets']:
        # Concatenate the words to track
        totrack = set()
        for i in args['<track_file>']:
            totrack = totrack.union(set(LSF(i).tolist()))

        if args['collect']:
            # Authenticate to the Twitter API
            api.tweets = sporty.tweets.api(settings_file=args['<settings_file>'])
            api.collect(totrack, args['<output_tweets>'], count=int(args['--count']))

        if args['filter']:
            api.load(args['<input_tweets>'])
            api.filter(int(args['--count']), totrack, each_word=args['--each'], output_file=args['<output_tweets>'], rt=args['--no-rt']==False)

    elif args['users']:
        if args['collect_tweets']:
            user = User(0, args['<settings_file>'])
            for uid in LSF(args['<user_ids_file>']).tolist():
                print 'Collect tweets for user ' + str(uid)
                user_path = os.path.join(args['<output_dir>'], uid)
                if os.path.isfile(user_path):
                    continue
                user.user_id = int(uid)
                user.collectTweets(int(args['--count']), user_path)

        if args['list_friends']:
            user = User(0, args['<settings_file>'])
            for uid in LSF(args['<user_ids_file>']).tolist():
                print 'Collect tweets for user ' + str(uid)
                user_path = os.path.join(args['<output_dir>'], uid)
                if os.path.isfile(user_path):
                    continue
                user.user_id = int(uid)
                with open(user_path, 'w') as f:
                    for friend_id in user.getFriends():
                        f.write(str(friend_id) + "\n")

    elif args['mood']:
        keys = ['AH', 'DD', 'TA']
        if args['--no-AH']:
            keys.remove('AH')
        if args['--no-DD']:
            keys.remove('DD')
        if args['--no-TA']:
            keys.remove('TA')

        labels = {x: [0,1] for x in keys}

        if args['label']:
            api.load(args['<input_tweets>'])
            api.label(labels, args['<labeled_tweets>'], int(args['--begin-line']))

        elif args['benchmark']:
            if len(keys) > 1:
                api.mood.clf = OneVsRestClassifier(SVC(kernel='linear'))
            tweets = Tweets(args['<labeled_tweets>'])
            corpus = utils.Cleaner(stopwords=args['--stopwords'],
                                   emoticons=args['--emoticons']).clean(tweets)
            tfidf_options = {'min_df': int(args['--min-df'])}
            api.buildFeatures(corpus, labels=keys)
            api.buildVectorizer(options=tfidf_options)
            api.train()
            api.benchmark(cv=2)

if __name__ == "__main__":
    main()
