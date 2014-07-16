from sporty.stats import *

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
    # clf_list = ['logistic-reg', 'svm', 'naive-bayes']

    clf = StatsNode('clf',
                    {c: ['--clf=' + c] for c in clf_list},
                    {c: c + '-options' for c in clf_list})

    logistic_reg_options = StatsNode('logistic-reg-options',
                                     {True: ['--clf-options={"class_weight":"auto"}']},
                                     'kfeatures')

    svm_options = StatsNode('svm-options',
                            {True: ['--clf-options={"kernel":"linear","class_weight":"auto"}']},
                            'kfeatures')

    decision_tree_options = statsTree.emptyNode('decision-tree-options', 'kfeatures')
    naive_bayes_options = statsTree.emptyNode('naive-bayes-options', 'kfeatures')
    kneighbors_options = statsTree.emptyNode('kneighbors-options', 'kfeatures')

    # kfeatures_range = np.arange(800, 0, -80)
    kfeatures_range = np.arange(200, 150, -20)
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

    i = 0

    def save_benchmark(cmd):
        global dictwriter
        global i
        i += 1
        # create unique filename
        cmdmap = lambda p: ''.join(c for c in p if c not in set(string.punctuation))
        cmdmap2 = lambda p: p.replace(' ', '_')
        cmdcpy = map(cmdmap, cmd[7:])
        cmdcpy = map(cmdmap2, cmdcpy)
        filename = '_'.join(cmdcpy)
        filename = '../stats/' + str(i) + '_' + filename

        stdout = sys.stdout
        with open(filename, 'w') as statsout:
            sys.stdout = statsout
            args, results = cli.main(cmd)
            sys.stderr.write(str(cmd) + "\n" + str(results) + "\n")
            args['rocauc'] = results
            if not dictwriter:
                dictwriter = csv.DictWriter(cumulated_out, args.keys())
                dictwriter.writeheader()
                cumulated_out.flush()
            dictwriter.writerow(args)

    statsTree.traverse(save_benchmark)
    cumulated_out.close()
