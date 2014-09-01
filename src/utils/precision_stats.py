from sporty.stats import *
import numpy as np

if __name__ == '__main__':
    statsTree = StatsTree()

    # Set commands
    head_cmd = ['mood', 'benchmark', '-t', '/data/1/sporty/nort/3K_labeled',
                '--min-df=3', '--n-folds=10', '--n-examples=30']
    liwc_only_cmd = ['-f', '["liwcFeature"]']
    emo_cmd = ['-e', '../inputs/params/emoticons']
    sw_cmd = ['-s', '../inputs/params/stopwords']
    reduce_cmd = ['-r', 'lambda x,y: x or y']
    liwc_cmd = ['--liwc', '../inputs/liwc.dic']
    logreg_opt_cmd = ['--clf-options={"class_weight":"auto"}']
    svm_opt_cmd = ['--clf-options={"kernel":"linear","class_weight":"auto"}']

    # Set options
    clf_list = ['logistic-reg']
    kfeatures_range = np.arange(160, 250, 10)
    probability_range = np.arange(0, 1, 0.01)

    statsTree.addNodes([
        ('head', {True: head_cmd}, 'emoticons'),

        ('emoticons', {True: emo_cmd}, 'liwc'),

        ('liwc', {True: liwc_cmd}, 'clf'),

        ('clf',
         {c: ['--clf=' + c] for c in clf_list},
         {c: c + '-options' for c in clf_list}),

        ('logistic-reg-options', {True: logreg_opt_cmd}, 'kfeatures'),

        ('kfeatures',
         {k: ['-k', str(k)] for k in kfeatures_range},
         'probability'),

        ('probability',
         {p: ['--proba=' + str(p)] for p in probability_range},
         None)
        ])

    # statsTree.cmdlen()
    statsTree.tofile('../outputs/stats_threshold_noreduce/cumulated.csv')
