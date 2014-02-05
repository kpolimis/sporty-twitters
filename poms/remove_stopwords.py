import argparse
import sys
import re

parser = argparse.ArgumentParser()
parser.add_argument("stopwords", type=str)

if __name__ == "__main__":
    args = parser.parse_args()
    # load stopwords file
    sw_file = open(args.stopwords, "r");
    sw = [x[:-1] for x in sw_file]

    # read in stdin
    for line in sys.stdin:
        # remove URLs
        line = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?]))''', '', line)

        # remove stopwords
        word = re.split(" ", line)
        word = [x for x in word if x not in sw]

        # write result in stdout
        sys.stdout.write(" ".join(word))
