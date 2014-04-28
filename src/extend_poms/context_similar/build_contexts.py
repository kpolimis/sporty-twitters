#! /usr/bin/env python
import json
import sys
import re
from collections import defaultdict

def run(in_stream=sys.stdin, out_stream=sys.stdout,debug=False):
    contextdict = defaultdict(lambda: defaultdict(int))
    
    if debug:
        sys.stderr.write("Start reading stream and create occurrences matrix...\n")
        sys.stderr.flush()  
    num_tweets = 1
    for tweet in in_stream:
        if debug:
            if num_tweets%10 == 0:
                sys.stderr.write("tweet " + str(num_tweets) + "\r")
                sys.stderr.flush()
        num_tweets += 1
        words = re.split("\s+", tweet[:-1])
        words = [x for x in words if x] # remove empty words

        target = 0
        for w in words:
            w_dic = contextdict[w]
            i = 0
            for i in range(max(0, target-3), target):
                entry = words[i] + "@" + str(i-target)
                w_dic[entry] += 1
            for i in range(target+1, min(target+3, len(words))):
                entry = words[i] + "@" + str(i-target)
                w_dic[entry] += 1
            target += 1

    if debug:
        sys.stderr.write("\nDone...\n")
        sys.stderr.flush()
    out_stream.write(json.dumps(contextdict))
    return contextdict

if __name__ == "__main__":
    contexts = run()
