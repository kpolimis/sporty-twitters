import re
from collections import defaultdict

def loadPOMS(input_file, key="word", cat=None):
    # load poms words
    poms_file = open(input_file, "r")
    poms = defaultdict(list)
    for line in poms_file:
        fields = re.split("\s+", line[:-1])
        if cat == None or cat == fields[0]:
            if key == "word":
                poms[fields[1]] = fields[0]
            elif key == "category":
                poms[fields[0]].append(fields[1])
    return poms 

def loadPOMSlegend(input_file):
    poms_file = open(input_file, "r")
    poms_legend = defaultdict(str)
    for line in poms_file:
        fields = re.split("\s+", line[:-1])
        poms_legend[fields[0]] = fields[1]
    return poms_legend