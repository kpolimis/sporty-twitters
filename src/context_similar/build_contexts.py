#! /usr/bin/env python
import argparse
import json
import sys
import re
from collections import defaultdict
from collections import Counter
import numpy as np
import sys
import cProfile

def buildContexts(input_stream):
    contextdict = defaultdict(lambda: defaultdict(int))
    
    # sys.stderr.write("Start reading stream and create occurrences matrix...\n")
    # sys.stderr.flush()
    num_tweets = 1
    for tweet in input_stream:
        # if num_tweets%1000 == 0:
        #     sys.stderr.write("tweet " + str(num_tweets) + "\r")
        #     sys.stderr.flush()
        # num_tweets += 1
        words = re.split("\s+", tweet[:-1])
        words = [x for x in words if x] # remove empty words

        target = 0
        for w in words:
            w_dic = contextdict[w]
            i = 0
            for i in range(0, target):
                entry = words[i] + "@" + str(i-target)
                w_dic[entry] += 1
            for i in range(target+1, len(words)):
                entry = words[i] + "@" + str(i-target)
                w_dic[entry] += 1
            target += 1

    # sys.stderr.write("\nDone...\n")
    # sys.stderr.flush()
    return contextdict
    # counts = dict()
    # num_words = 1.
    # tot = float(len(contextdict.keys()))
    # for word in contextdict.keys():
    #     percentage = num_words*100./tot
    #     sys.stderr.write(str(int(percentage)) + "% done\r")
    #     num_words += 1
    #     counts[word] = Counter(contextdict[word])

    # sys.stderr.write("\nDone...\n")
    # return counts

if __name__ == "__main__":
    contexts = cProfile.run("buildContexts(sys.stdin)")
    # sys.stderr.write("Saving to JSON format...\n")
    # sys.stdout.write(json.dumps(contexts))
    # sys.stderr.write("Done\n")
    
    # # l = len(contexts)
    # similarityMatrix = [[0.]*l]*l

    # i = 0
    # for k1 in contexts.keys():
    #     j = 0
    #     for k2 in contexts.keys():
    #         similarityMatrix[i][j] = computeSimilarity(k1, k2, contexts)
    #         j += 1

    # sys.stdout.write(json.dumps(similarityMatrix))
