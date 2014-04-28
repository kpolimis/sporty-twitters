#! /usr/bin/env python
import argparse
import sys
import json
from collections import defaultdict
from collections import OrderedDict
from similarity_scores import *
from utils.load_poms import *

def getNMostSimilarTo(words, n, similarityMatrix, debug=False):
    allscores = defaultdict(float)
    for w in words: # for each word in the list of words belonging to one category
        dict4word = similarityMatrix[w] # get the score for a given word
        for context_w in dict4word: # for each word that was in the contexts
            allscores[context_w] += dict4word[context_w]
    sortedSim = sorted(allscores, key=allscores.get, reverse=True)
    # get the n first elements of the sorted list
    simWords = OrderedDict()
    for w in sortedSim[:n]:
        simWords[w] = allscores[w]/float(len(words))
    return simWords

def getSimilarityMatrix(contexts, wordlist, similarityMethod=cosineSimilarity, debug=False):
    w = len(contexts)
    h = len(wordlist)
    similarityMatrix = defaultdict(lambda:defaultdict(float))
    total = h*w # number of elements in the similarity matrix

    for k1 in wordlist:
        count = 1 # actual element
        for k2 in contexts.keys():
            similarityMatrix[k1][k2] = similarityMethod(k1, k2, contexts)
            if debug:
                percentage = 100.*float(count)/float(w)
                if int(percentage)%5 == 0:
                    sys.stderr.write("finding similar words for '" + k1 + "': " + str(int(percentage)) + "% \r")
                count += 1
        sys.stderr.write("\n")
    return similarityMatrix

def run(poms, poms_legend, n, args_categories, in_stream = sys.stdin, out_stream=sys.stdout, debug=False):
    if debug:
        sys.stderr.write("Loading JSON contexts...")
        sys.stderr.flush()
    contexts = json.load(in_stream)
    if debug:
        sys.stderr.write("Done\n")
        sys.stderr.flush()

    # load poms words and categories
    if debug:
        sys.stderr.write("Loading POMS legend...")
        sys.stderr.flush()
    poms_legend = load_poms_legend(poms_legend)
    categories = poms_legend.keys()

    if args_categories != "all":
        categories = set(categories).intersection(set(args_categories))
    if debug:
        sys.stderr.write("Done\n")
        sys.stderr.flush()

    for c in categories:
        if debug:
            sys.stderr.write("Loading POMS for category '" + c + "'...")
            sys.stderr.flush()
        poms_words = load_poms(poms, "word", c)
        if debug:
            sys.stderr.write("Done\n")
            sys.stderr.flush()
        processed_words = [x for x in poms_words if x in contexts.keys()]
        similarityMatrix = getSimilarityMatrix(contexts, processed_words, debug=debug)
        mostSimilarWords = getNMostSimilarTo(processed_words, n, similarityMatrix, debug=debug)

        for word in mostSimilarWords:
            out_stream.write(c + "\t" + word + "\t" + str(mostSimilarWords[word]) + "\n")
        out_stream.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("poms_file", type=str) 
    parser.add_argument("poms_legend_file", type=str) 
    parser.add_argument("n", nargs="?", type=int, default=20)
    parser.add_argument("categories", nargs="*", type=str, default=all)
    args = parser.parse_args()

    run(args.poms_file, args.poms_legend_file, args.n, args.categories, debug=True)
