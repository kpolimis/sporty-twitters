"""
Usage: freq2odds.py <input_file>
"""
import sys
from docopt import docopt
from collections import defaultdict
import json
import numpy as np

def freq2odds(input_file):
    # Store the frequencies in a dictionary
    freq = defaultdict(lambda: defaultdict(tuple))
    with open(input_file) as f:
        for line in f:
            tokens = line.strip().split(",")
            freq[tokens[0]][tokens[2]] = (int(tokens[3]), int(tokens[4]))

    # Compute the number of words and the sum of all the frequencies for the positive and negative class of each dimension (AH, DD, TA)
    cat_properties = {}
    for cat in freq.keys():
        cat_properties[cat] = {}
        cat_properties[cat]["sum_freq"] = (sum(freq[cat][w][0] for w in freq[cat].keys()),
                                           sum(freq[cat][w][1] for w in freq[cat].keys()))
        cat_properties[cat]["norm_freq"] = (sum(freq[cat][w][0] > 0 for w in freq[cat].keys()),
                                            sum(freq[cat][w][1] > 0 for w in freq[cat].keys()))
        cat_properties[cat]["numerator_proba"] = (float(cat_properties[cat]["sum_freq"][0] + cat_properties[cat]["norm_freq"][0]),
                                                  float(cat_properties[cat]["sum_freq"][1] + cat_properties[cat]["norm_freq"][1]))

    # Compute the probability of each word for each category
    proba = defaultdict(lambda: defaultdict(tuple))
    logodds = defaultdict(lambda: defaultdict(float))
    for cat in cat_properties.keys():
        for w in freq[cat].keys():
            proba[cat][w] = (float(freq[cat][w][0] + 1)/cat_properties[cat]["numerator_proba"][0],
                             float(freq[cat][w][1] + 1)/cat_properties[cat]["numerator_proba"][1])
            logodds[cat][w] = np.log(proba[cat][w][0]/proba[cat][w][1])
            print ",".join(map(str,[cat, '{0:.16f}'.format(logodds[cat][w]), w, 
                                    '{0:.16f}'.format(proba[cat][w][0]),
                                    '{0:.16f}'.format(proba[cat][w][1])]))
    return proba

def main():
    args = docopt(__doc__)
    input_f = args['<input_file>']
    freq2odds(input_f)

if __name__ == "__main__":
    main()
