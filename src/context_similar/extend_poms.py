#! /usr/bin/env python
import argparse
import sys
import re
import json
from collections import defaultdict
from collections import OrderedDict
from similarity_scores import *
from utils.loadPOMS import *

def getNMostSimilarTo(words, n, similarityMatrix):
    allscores = defaultdict(float)
    for w in words: # for each word in the list of words belonging to one category
        dict4word = similarityMatrix[w] # get the score for a given word
        for context_w in dict4word: # for each word that was in the contexts
            allscores[context_w] += dict4word[context_w]
    sortedSim = sorted(allscores, key=allscores.get, reverse=True)
    # get the n first elements of the sorted list
    simWords = OrderedDict()
    for w in sortedSim[:n]:
        simWords[w] = allscores[w]
    return simWords

def getSimilarityMatrix(contexts, wordlist, similarityMethod=cosineSimilarity):
    w = len(contexts)
    h = len(wordlist)
    similarityMatrix = defaultdict(lambda:defaultdict(float))
    total = h*w # number of elements in the similarity matrix

    for k1 in wordlist:
        count = 1 # actual element
        for k2 in contexts.keys():
            similarityMatrix[k1][k2] = similarityMethod(k1, k2, contexts)
            percentage = 100.*float(count)/float(w)
            if int(percentage)%5 == 0:
                sys.stderr.write("finding similar words for '" + k1 + "': " + str(int(percentage)) + "% \r")
            count += 1
        sys.stderr.write("\n")
    return similarityMatrix

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("poms_file", type=str) 
    parser.add_argument("poms_legend_file", type=str) 
    parser.add_argument("n", nargs="?", type=int, default=20)
    parser.add_argument("categories", nargs="*", type=str, default=all)
    args = parser.parse_args()

    sys.stderr.write("Loading JSON contexts...")
    sys.stderr.flush()
    contexts = json.load(sys.stdin)
    sys.stderr.write("Done\n")
    sys.stderr.flush()

    # load poms words and categories
    sys.stderr.write("Loading POMS legend...")
    sys.stderr.flush()
    poms_legend = loadPOMSlegend(args.poms_legend_file)
    categories = poms_legend.keys()

    if args.categories != "all":
        categories = set(categories).intersection(set(args.categories))
    sys.stderr.write("Done\n")
    sys.stderr.flush()

    for c in categories:
        sys.stderr.write("Loading POMS for category '" + c + "'...")
        sys.stderr.flush()
    	poms_words = loadPOMS(args.poms_file, "word", c)
        sys.stderr.write("Done\n")
        sys.stderr.flush()
        processed_words = [x for x in poms_words if x in contexts.keys()]
        similarityMatrix = getSimilarityMatrix(contexts, processed_words)
        mostSimilarWords = getNMostSimilarTo(processed_words, args.n, similarityMatrix)

        for word in mostSimilarWords:
        	sys.stdout.write(c + "\t" + word + "\t" + str(mostSimilarWords[word]) + "\n")
        sys.stdout.flush()