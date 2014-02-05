import argparse
import json
import sys
import re

parser = argparse.ArgumentParser()
parser.add_argument("poms_words", type=str)

if __name__ == "__main__":
    args = parser.parse_args()

    # load poms words
    poms_file = open(args.poms_words, "r");
    poms_words = [x[:-1] for x in poms_file]

    freq = {w : dict() for w in poms_words}

    for line in sys.stdin:
        tweet_words = re.split(" ", line)
        common = [w for w in tweet_words if w in poms_words]
        if common:
            for w in common:
                d = freq[w]
                list_words = filter(lambda x: x != w, tweet_words)
                if list_words:
                    for tw in list_words:
                        if tw in d.keys():
                            d[tw] += 1
                        else:
                            d[tw] = 1
                            
    for poms_w in poms_words:
        d = freq[poms_w]
        keys = sorted(d.keys(), key=d.get, reverse=True)
        print poms_w + ":"
        for k in keys:
            if d[k] > 3:
                print "\t" + k + "\t" + str(d[k])
