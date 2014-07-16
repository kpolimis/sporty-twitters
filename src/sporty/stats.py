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


class StatsTree(object):
    def __init__(self):
        super(StatsTree, self).__init__()
        self.head = None
        self.nodes = {}

    def emptyNode(name, nextNode=[]):
        return StatsNode(name, {True: []}, nextNode)

    def addNode(self, statsNode):
        self.nodes[statsNode.name] = statsNode
        if not self.head:
            self.head = statsNode
        return statsNode

    def addNodes(self, nodes):
        for n in nodes:
            self.addNode(n)

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
