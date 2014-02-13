#! /usr/bin/env python
import argparse
import json
import sys
import re
from collections import defaultdict
from utils import loadPOMS

MIN_APPEARANCES    = 100
WORDS_PER_CATEGORY = 10

parser = argparse.ArgumentParser()
parser.add_argument("poms_file", type=str)
parser.add_argument("coocurrences_file", type=str)
parser.add_argument("category", nargs="*", type=str, default="all")

if __name__ == "__main__":
    args = parser.parse_args()
    
    # load poms words and categories
    poms = loadPOMS(args.poms_file, "category")
    freq_results = json.load(open(args.coocurrences_file, "r"))

    # count the number of apparition for each word
    doc_freq = defaultdict(int)
    for poms_word in freq_results.keys():
        coocurrences = freq_results[poms_word]
        for cooc in coocurrences.keys():
            doc_freq[cooc] += coocurrences[cooc]

    if args.category == "all":
        categories = poms.keys()
    else:
        categories = [args.category]

    tfidf = {c : dict() for c in categories}
    for cat in categories:
        cat_freq = defaultdict(int)
        for poms_word in poms[cat]:
            coocurrences = freq_results[poms_word]
            for cooc in coocurrences.keys():
                cat_freq[cooc] += coocurrences[cooc]

        for word in cat_freq.keys():
            if doc_freq[word] > 30:
                tfidf[cat][word] = float(cat_freq[word])/float(doc_freq[word])

    for cat in categories:
        sorted_tfidf = sorted(tfidf[cat].keys(), key=tfidf[cat].get, reverse=True)
        print cat + ":"
        for i in range(100):
            print "\t" + sorted_tfidf[i] + "\t" + str(tfidf[cat][sorted_tfidf[i]])
