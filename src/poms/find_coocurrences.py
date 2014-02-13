#! /usr/bin/env python
import argparse
import json
import sys
import re
from collections import defaultdict
from utils import loadPOMS

parser = argparse.ArgumentParser()
parser.add_argument("poms_file", type=str)
    
if __name__ == "__main__":
    args = parser.parse_args()
    
    # load poms words and categories
    poms = loadPOMS(args.poms_file)
    poms_words = set(poms.keys())

    # init the term frequency, category frequency, and document frequency dictionaries
    tf = {w : defaultdict(int) for w in poms_words}

    # for each tweet
    for line in sys.stdin:
        # keep only the words that are in poms and in tweets
        tweet_words = set(re.split("\s+", line[:-1]))
        common = [w for w in tweet_words if w in poms_words]

        for w in common:
            d = tf[w]
            list_words = filter(lambda x: x != w, tweet_words)
            for tw in list_words:
                d[tw] += 1

    print json.dumps(tf)

    # for category in cf.keys():
    #     tfidf = dict()                        

    #     for term in cf[category]:
    #         if term:
    #             tfidf[term] = float(cf[category][term])*float(df[term])
    #     sorted_tdidf = sorted(tfidf.keys(), key=tfidf.get, reverse=True)

    #     print category + ":"
    #     i = 0
    #     while (i < WORDS_PER_CATEGORY and i < len(sorted_tdidf)):
    #         term = sorted_tdidf[i]
    #         print "\t" + term + "\t" + str(tfidf[term])
    #         i += 1

    # for poms_w in poms_words:
    #     d = tf[poms_w]
    #     keys = sorted(d.keys(), key=d.get, reverse=True)
    #     print poms_w + ":"
    #     for k in keys:
    #         if d[k] > MIN_APPEARANCES:
    #             print "\t" + k + "\t" + str(d[k])
