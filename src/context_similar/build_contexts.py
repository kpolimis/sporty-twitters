#! /usr/bin/env python
import argparse
import json
import sys
import re
from collections import defaultdict

if __name__ == "__main__":

    contexts = defaultdict(list)
    for tweet in sys.stdin:
        words = set(re.split("\s+", tweet[:-1]))
        for word in words:
            context = set(w for w in words if w != word)
            contexts[word].append(context)

    print contexts#json.dumps(contexts)
