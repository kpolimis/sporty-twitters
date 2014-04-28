#! /usr/bin/env python
import argparse
import json
import sys
import re
from collections import defaultdict
from utils.load_poms import load_poms

parser = argparse.ArgumentParser()
parser.add_argument("poms_file", type=str)
parser.add_argument("cooccurrences_file", type=str)
parser.add_argument("category", nargs="*", type=str, default="all")
parser.add_argument("min_appearances", nargs="?", type=int, default=100)
parser.add_argument("words_per_category" nargs="?", type=int, default=100)


if __name__ == "__main__":
    args = parser.parse_args()
    
    # load poms words and categories
    poms = load_poms(args.poms_file, "category")
    # load cooccurences results
    freq_results = json.load(open(args.cooccurrences_file, "r"))

    # count the number of apparition for each word in the whole corpus
    doc_freq = defaultdict(int)
    for poms_word in freq_results.keys():
        cooccurrences = freq_results[poms_word]
        for cooc in cooccurrences.keys():
            doc_freq[cooc] += cooccurrences[cooc]

    # detect the categories to process
    if args.category == "all":
        categories = poms.keys()
    else:
        categories = args.category

    # create dictionaries for tfidf score and categories frequences
    tfidf = {c : dict() for c in categories}
    categories_freq = {c : dict() for c in categories}

    for cat in categories:
        cat_freq = defaultdict(int)
        # for each poms words of a given category
        for poms_word in poms[cat]:
            cooccurrences = freq_results[poms_word]
            for cooc in cooccurrences.keys():
                cat_freq[cooc] += cooccurrences[cooc]
        
        categories_freq[cat] = cat_freq
        for word in cat_freq.keys():
            if doc_freq[word] > args.min_appearances:
                tfidf[cat][word] = float(cat_freq[word])/float(doc_freq[word])

    for cat in categories:
        sorted_tfidf = sorted(tfidf[cat].keys(), key=tfidf[cat].get, reverse=True)
        print cat + ":"
        for i in range(args.words_per_category):
            print "\t" + sorted_tfidf[i] + "\t" + str(tfidf[cat][sorted_tfidf[i]]) + "\t" + str(categories_freq[cat][sorted_tfidf[i]]) + "\t" + str(doc_freq[sorted_tfidf[i]])
