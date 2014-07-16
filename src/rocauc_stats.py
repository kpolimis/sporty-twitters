from sporty.stats import *

if __name__ == '__main__':
    statsTree = StatsTree()

    # '/data/1/sporty/nort/3K_labeled'
    # Set commands
    head_cmd = ['mood', 'benchmark', '-t', '../inputs/3K_labeled',
                '--min-df=3', '--n-folds=10', '--n-examples=30']
    liwc_only_cmd = ['-f', '["liwcFeature"]']
    emo_cmd = ['-e', '../inputs/params/emoticons']
    sw_cmd = ['-s', '../inputs/params/stopwords']
    reduce_cmd = ['-r', 'lambda x,y: x or y']
    liwc_cmd = ['--liwc', '../inputs/liwc.dic']
    logreg_opt_cmd = ['--clf-options={"class_weight":"auto"}']
    svm_opt_cmd = ['--clf-options={"kernel":"linear","class_weight":"auto"}']

    # Set options
    clf_list = ['logistic-reg', 'svm', 'decision-tree', 'naive-bayes', 'kneighbors']
    kfeatures_range = np.arange(800, 0, -80)

    statsTree.addNodes([
        ('head', {True: head_cmd}, 'liwc_only'),

        ('liwc_only', {True: liwc_only_cmd, False: []}, {True: None, False: 'emoticons'}),

        ('emoticons', {True: emo_cmd, False: []}, 'stopwords'),

        ('stopwords', {True: sw_cmd, False: []}, 'reducefunc'),

        ('reducefunc', {True: reduce_cmd, False: []}, 'liwc'),

        ('liwc', {True: liwc_cmd, False: []}, 'clf'),

        ('clf',
         {c: ['--clf=' + c] for c in clf_list},
         {c: c + '-options' for c in clf_list}),

        ('logistic-reg-options', {True: logreg_opt_cmd}, 'kfeatures'),

        ('svm-options', {True: svm_opt_cmd}, 'kfeatures'),

        StatsNode.emptyNode('decision-tree-options', 'kfeatures'),

        StatsNode.emptyNode('naive-bayes-options', 'kfeatures'),

        StatsNode.emptyNode('kneighbors-options', 'kfeatures'),

        ('kfeatures',
         {k: ['-k', str(k)] for k in kfeatures_range},
         None)
        ])

    statsTree.tofile('../stats/cumulated.csv')
