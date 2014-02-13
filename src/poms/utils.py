import re

def loadPOMS(input_file, key="word"):
    # load poms words
    poms_file = open(input_file, "r");
    poms = dict()
    for line in poms_file:
        fields = re.split("\s+", line[:-1])
        if key == "word":
            poms[fields[1]] = fields[0]
        elif key == "category":
            if fields[0] in poms.keys():
                poms[fields[0]].append(fields[1])
            else:
                poms[fields[0]] = []
    return poms

    
