"""
Usage: odds_ratio.py <dir> [<dir>...] [-l]
"""
#!/usr/bin/python
import math
import sys
from docopt import docopt
from collections import defaultdict
import os.path

def compute_odds_ratio(directories, log):
    if log:
        func=math.log
    else:
        func=lambda x:x
    dimensions = ["AH", "DD", "TA"]
    extensions = ["_pos", "_neg"]
    # build dictionaries
    dictionaries = defaultdict(lambda: defaultdict(int))
    for d in directories:
        for dim in dimensions:
            for ext in extensions:
                fpath = os.path.join(d, dim+ext+"_count")
                sys.stderr.write("Processing " + str(fpath) + "\n")
                with open(fpath) as f:
                    for line in f:
                        c, w = line.split(" ")
                        w = w.strip()
                        dictionaries[dim+ext][w] += int(c)
    for dim in dimensions:
        for w in dictionaries[dim+"_pos"]:
            pos_val = dictionaries[dim+"_pos"][w]
            neg_val = dictionaries[dim+"_neg"][w]
            odd_ratio = func(float(pos_val+1)/float(neg_val+1))
            print ",".join(map(str,[dim, odd_ratio, w, pos_val, neg_val]))

def main():
    args = docopt(__doc__)
    compute_odds_ratio(args['<dir>'],
                       args['-l'])

if __name__=="__main__":
    main()
