#! /usr/bin/env python
import argparse
import json
import sys
import re
from collections import defaultdict
from utils.loadPOMS import loadPOMS

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
