from cli import cli
import sys
import numpy as np
import csv
import os
import string
import re


class StatsNode(object):
    def __init__(self, name, choices, nextNode=[]):
        super(StatsNode, self).__init__()
        self.name = name
        self.choices = choices
        self.nextNode = nextNode

    @staticmethod
    def emptyNode(name, nextNode=[]):
        return StatsNode(name, {True: []}, nextNode)


class StatsTree(object):
    def __init__(self):
        super(StatsTree, self).__init__()
        self.head = None
        self.nodes = {}
        self.count = 0
        self.sortedKeys = None

    def addNode(self, n):
        if isinstance(n, StatsNode):
            self.nodes[n.name] = n
            if not self.head:
                self.head = n
            return n
        else:
            raise Exception('Wrong type: should be StatsNode but is ' + type(n) + '.')

    def addNodes(self, nodes):
        for n in nodes:
            if type(n) == tuple and len(n) == 3:
                self.addNode(StatsNode(*n))
            elif isinstance(n, StatsNode):
                self.addNode(n)
            else:
                raise Exception('Wrong type: should be StatsNode but is ' + type(n) + '.')

    def traverse(self, func):
        cmd = []
        self.__traverseNode('head', func, cmd)

    def __traverseNode(self, nodeName, func, cmd):
        n = None
        if not nodeName:
            func(cmd)
            return
        elif nodeName in self.nodes:
            n = self.nodes[nodeName]
        else:
            raise Exception('No node named ' + nodeName + ' in this tree.')

        for choice in n.choices:
            cmd += n.choices[choice]

            nextNode = None
            if type(n.nextNode) == str:
                nextNode = n.nextNode
            elif type(n.nextNode) == dict:
                if choice in n.nextNode:
                    nextNode = n.nextNode[choice]

            self.__traverseNode(nextNode, func, cmd)

            for args in n.choices[choice]:
                cmd.pop(-1)

    def tofile(self, cumulated_filename):
        cumulated_out = open(cumulated_filename, 'w')
        parent_dir = os.path.abspath(os.path.dirname(cumulated_filename))
        self.count = 0
        self.sortedKeys = None

        def save_benchmark(cmd):
            self.count += 1
            # create unique filename
            cmdmap = lambda p: ''.join(c for c in p if c not in set(string.punctuation))
            cmdmap2 = lambda p: p.replace(' ', '_')
            cmdcpy = map(cmdmap, cmd[7:])
            cmdcpy = map(cmdmap2, cmdcpy)
            filename = '_'.join(cmdcpy)
            filename = str(self.count) + '_' + filename
            filename = os.path.join(parent_dir, filename)

            stdout = sys.stdout
            with open(filename, 'w') as statsout:
                sys.stdout = statsout
                args, stats = cli.main(cmd)
                for s in stats:
                    args[s] = stats[s]
                if not self.sortedKeys:
                    self.sortedKeys = sorted(args.keys(), reverse=True)
                    header = ','.join(self.sortedKeys) + "\n"
                    cumulated_out.write(header)
                cumulated_out.write(','.join(map(lambda x: str(args.get(x)),
                                                 self.sortedKeys))
                                    + "\n")
                cumulated_out.flush()

        self.traverse(save_benchmark)
        cumulated_out.close()
