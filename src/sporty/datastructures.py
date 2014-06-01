import json
import os
from collections import defaultdict
import re

class TSV():
    """
    Tool to load a TSV file into several dictionaries. It is used in this project to load the POMS
    vocabulary and the emoticons. Each word of these vocabularies belong to a category. This data
    structure give access to a dictionary 'keys' that maps a category to a list of words belonging
    to this category, and a dictionary 'values' that maps each word in the vocabulary to the 
    category it belongs to.
    """
    def __init__(self, tsv_file):
        self.tsv_file = tsv_file
        self.keys = defaultdict(list)
        self.values = {}
        self.load()
        
    def load(self):
        if not self.tsv_file:
            return
        if type(self.tsv_file) == str:
            tsv_file = open(self.tsv_file)
        elif type(self.tsv_file) == file:
            tsv_file = self.tsv_file
        else:
            raise Exception("Unsupported type for tsv file.")
        for line in tsv_file:
            fields = re.split("\s+", line.strip())
            if len(fields) > 1:
                self.keys[fields[0]].append(fields[1])
                self.values[fields[1]] = fields[0]

class LSF():
    """
    Tool to load a Line-Separated File. This kind of file contains a list of words, one word on 
    each line.
    """
    def __init__(self, input_file):
        self.input_file = input_file
        self.words = []
        self.load()
    
    def load(self):
        if not self.input_file:
            return
        if type(self.input_file) == str:
            input_file = open(self.input_file)
        elif type(self.input_file) == file:
            input_file = self.input_file
        else:
            raise Exception("Unsupported type for input file.")
        for line in input_file:
            self.words.append(line.strip())

    def tolist(self):
        return self.words
