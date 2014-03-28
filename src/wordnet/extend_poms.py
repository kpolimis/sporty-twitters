import argparse
from nltk.corpus import wordnet as wn
from utils.loadPOMS import loadPOMS
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("poms_file", type=str)
parser.add_argument("category", nargs="*", type=str, default="all")

if __name__ == "__main__":
    args = parser.parse_args()

    # load poms words and categories
    poms = loadPOMS(args.poms_file, "category")
    poms_words = set(poms.keys())

    if args.category == "all":
        categories = poms.keys()
    else:
        categories = args.category

    # initialize the dictionary of synonyms
    syn = defaultdict(set)
    for c in categories:
        for w in poms[c]:
            synset = wn.synsets(w, pos=wn.ADJ)
            for s in synset:
                syn[c] = syn[c].union(set([l.name for l in s.lemmas]))
        for w in syn[c]:
            print c + "\t" + w

