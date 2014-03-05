#! /usr/bin/env python
import argparse
import json
import pickle
import sys
import re
from collections import defaultdict

def computeWordContextMatrix(input_stream):
    cur_cid = 1
    cur_wid = 1
    w2ctx = defaultdict(list)
    c2cid = defaultdict(int)
    cid2c = defaultdict(tuple)
    w2wid = defaultdict(int)
    wid2w = defaultdict(str)

    for tweet in input_stream:
        words = re.split("\s+", tweet[:-1])
        for w in words:
            ctx = tuple(x for x in words if x != w)
            cid = c2cid[ctx]
            wid = w2wid[str(w)]
            if cid == 0:
                cid = c2cid[ctx] = cur_cid
                cur_cid += 1
            if wid == 0:
                wid = w2wid[w] = cur_wid
                cur_wid += 1
            wid2w[wid] = str(w)
            cid2c[cid] = ctx
            w2ctx[wid].append(cid)
    return w2ctx, c2cid, cid2c, w2wid, wid2w

if __name__ == "__main__":
    w2ctx, c2cid, cid2c, w2wid, wid2w = computeWordContextMatrix(sys.stdin)
    with open("w2ctx.pickle", "w") as f:
        f.write(pickle.dumps(w2ctx))
             
    # with open("c2cid.pickle", "w") as f:
    #     f.write(pickle.dumps(c2cid))

    with open("cid2c.pickle", "w") as f:
        f.write(pickle.dumps(cid2c))

    with open("w2wid.pickle", "w") as f:
        f.write(pickle.dumps(w2wid))

    with open("wid2w.pickle", "w") as f:
        f.write(pickle.dumps(wid2w))

