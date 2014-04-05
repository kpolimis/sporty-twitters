from math import sqrt
from collections import defaultdict
import sys

   
def cosineSimilarity(k1, k2, contexts):
    A = defaultdict(int, contexts[k1])
    B = defaultdict(int, contexts[k2])
    if len(A) == 0 or len(B) == 0:
        return 0
    if len(A) < len(B):
        M = A
        N = B
    else:
        M = B
        N = A

    normA = sqrt(sum([x**2 for x in A.values()]))
    normB = sqrt(sum([x**2 for x in B.values()]))

    score = 0.
    score = sum([float(M[k]*N[k]) for k in M.keys()])/float(normA*normB)
    return score
