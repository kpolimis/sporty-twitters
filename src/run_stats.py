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


if __name__ == '__main__':
    statsTree = StatsTree()

    head = StatsNode('head',
		    {True: ['mood', 'benchmark', '-t', '/data/1/sporty/nort/3K_labeled',
                             '--min-df=3', '--n-folds=10', '--n-examples=30']},
                     'liwc_only')

    liwc_only = StatsNode('liwc_only',
                          {True: ['-f', '["liwcFeature"]'], False: []},
                          {True: None, False: 'emoticons'})

    emoticons = StatsNode('emoticons',
                          {True: ['-e', '../inputs/params/emoticons'], False: []},
                          'stopwords')

    stopwords = StatsNode('stopwords',
                          {True: ['-s', '../inputs/params/stopwords'], False: []},
                          'reducefunc')

    reducefunc = StatsNode('reducefunc',
                           {True: ['-r', 'lambda x,y: x or y'], False: []},
                           'liwc')

    liwc = StatsNode('liwc',
                     {True: ['--liwc', '../inputs/liwc.dic'], False: []},
                     'clf')

    clf_list = ['logistic-reg', 'svm', 'decision-tree', 'naive-bayes', 'kneighbors']
    clf = StatsNode('clf',
                    {c: ['--clf=' + c] for c in clf_list},
                    {c: c + '-options' for c in clf_list})

    logistic_reg_options = StatsNode('logistic-reg-options',
                                     {True: ['--clf-options={"class_weight":"auto"}']},
                                     'kfeatures')

    svm_options = StatsNode('svm-options',
                            {True: ['--clf-options={"kernel":"linear","class_weight":"auto"}']},
                            'kfeatures')

    decision_tree_options = StatsNode('decision-tree-options',
                                      {True: []},
                                      'kfeatures')

    naive_bayes_options = StatsNode('naive-bayes-options',
                                    {True: []},
                                    'kfeatures')

    #kneighbors_range = np.arange(10, 0, -2)
    #kneighbors_options = StatsNode('kneighbors-options',
    #                               {k: ['--clf-options={"n_neighbors":"' + str(k) + '"}']
    #                                for k in kneighbors_range},
    #                               'kfeatures')

    kneighbors_options = StatsNode('kneighbors-options',
                                   {True: []},
                                   'kfeatures')

    kfeatures_range = np.arange(300, 0, -30)
    kfeatures = StatsNode('kfeatures',
                          {k: ['-k', str(k)] for k in kfeatures_range},
                          None)

    statsTree.addNodes([head,
                        liwc_only,
                        emoticons,
                        stopwords,
                        reducefunc,
                        liwc,
                        clf,
                        logistic_reg_options,
                        svm_options,
                        decision_tree_options,
                        naive_bayes_options,
                        kneighbors_options,
                        kfeatures])

    dictwriter = None
    cumulated_out_name = '../stats/cumulated.csv'
    cumulated_out = open(cumulated_out_name, 'w')

    def printcmd(cmd):
        print cmd
    def save_benchmark(cmd):
        global dictwriter
        cmd2filename = lambda p: ''.join(c for c in p if c not in set(string.punctuation))
        filename = '_'.join(map(cmd2filename, cmd[4:]))
        filename = '../stats/' + filename

        stdout = sys.stdout
        with open(filename, 'w') as statsout:
            sys.stdout = statsout
            args, results = cli.main(cmd)
            args['rocauc'] = results
            if not dictwriter:
                dictwriter = csv.DictWriter(cumulated_out, args.keys())
                dictwriter.writeheader()
                cumulated_out.flush()
            dictwriter.writerow(args)

    statsTree.traverse(save_benchmark)
    #statsTree.traverse(printcmd)
    cumulated_out.close()
