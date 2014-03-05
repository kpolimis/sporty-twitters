import sys
import re
import pickle
from collections import defaultdict
import argparse

def computeContextSimilarity(ctx1, ctx2):
    """Compute a similarity score between two contexts (i.e. between two lists)."""
    if len(ctx1) < len(ctx2):
        tmp = ctx1
        ctx1 = ctx2
        ctx2 = tmp
    maxlen = len(ctx1)
    minlen = len(ctx2)
    score = 0.
    div = max(1., float(maxlen))
    for i in range(maxlen):
        # increment score if a word is in both context
        if ctx1[i] in ctx2:
            score += 1.
            # increment the score once again if a word is in the same position
            # in both context
            if i < minlen and ctx1[i] == ctx2[i]:
                score += 1.
                div += 1.
    #print score, div
    score = score/div
    return score

def computeWordsSimilarity(idw1, idw2, w2ctx, w2wid, cid2c):
    """Compute a similarity score between two words based on their context in a given corpus. w2ctx, w2wid, and cid2c describe the corpus. It is computed using build_contexts.py."""
    assert idw1 != 0 and idw2 != 0

    score = 0.
    i = 0.
    for idctx1 in w2ctx[idw1]:
        for idctx2 in w2ctx[idw2]:
            score += computeContextSimilarity(cid2c[idctx1], cid2c[idctx2])
            i += 1.
    score /= i
    return score

# def findMoreSimilarWords(w, w2ctx, w2wid, cid2c, n=20):
#     """Find the n (20 by default) more similar words of a given word w."""
    
#     wid = w2wid[w]
#     assert wid != 0

#     for wid in w2ctx:
        
parser = argparse.ArgumentParser()
#parser.add_argument("word_1", type=str)
#parser.add_argument("word_2", type=str)
parser.add_argument("pickle_folder", type=str)
    
if __name__ == "__main__":
    args = parser.parse_args()

    print "Loading cid2c..."
    cid2c = pickle.load(open(args.pickle_folder + "/cid2c.pickle", "r"))
    print "Loading w2ctx..."
    w2ctx = pickle.load(open(args.pickle_folder + "/w2ctx.pickle", "r"))
    print "Loading w2wid..."
    w2wid = pickle.load(open(args.pickle_folder + "/w2wid.pickle", "r"))
 
    while True:
        w1 = raw_input("first word: ")
        w2 = raw_input("second word: ")
        print computeWordsSimilarity(w2wid[w1], w2wid[w2], w2ctx, w2wid, cid2c)
