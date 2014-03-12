import sys
import re
import json
from collections import defaultdict
  
def computeSimilarity(k1, k2, contexts):
    A = defaultdict(int, contexts[k1])
    B = defaultdict(int, contexts[k2])
    if len(A) < len(B):
        M = A
        N = B
    else:
        M = B
        N = A
    
    normA = sum([x**2 for x in A.values()])
    normB = sum([x**2 for x in B.values()])
    
    score = 0.
    for k in M.keys():
        score += float(M[k]*N[k])

    score /= float(normA*normB)
    return score

def getMoreSimilarTo(word, n, contexts, similarityMatrix):
    if word in contexts.keys():
        wordIdx = contexts.keys().index(word)
        similarities = {i: similarityMatrix[wordIdx][i] for i in range(len(similarityMatrix[wordIdx]))}
        sortedSimIdx = sorted(similarities, key=similarities.get)
        simWords = [contexts.keys()[x] for x in sortedSimIdx[:n]]
        return simWords
    else:
        return []

def getSimilarityMatrix(contexts):
    l = len(contexts)
    similarityMatrix = [[0.]*l]*l

    i = 0
    for k1 in contexts.keys():
        j = 0
        for k2 in contexts.keys():
            similarityMatrix[i][j] = computeSimilarity(k1, k2, contexts)
            j += 1
    return similarityMatrix

if __name__ == "__main__":

    contexts = json.load(sys.stdin)
    similarityMatrix = getSimilarityMatrix(contexts)

    print getMoreSimilarTo("sad", 10, contexts, similarityMatrix)
    sys.stdout.write(json.dumps(similarityMatrix))
