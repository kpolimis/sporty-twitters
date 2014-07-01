from cli import cli
import sys
import numpy as np
clf_list = ['logistic-reg', 'svm', 'decision-tree', 'naive-bayes', 'kneighbors']
k_range = np.arange(20, 250, 20)
begin = ['mood', 'benchmark', '-t', '../inputs/3K_labeled']
emoticons = ['-e', '../inputs/params/emoticons']
stopwords = ['-s', '../inputs/params/stopwords']
liwc = ['--liwc', '../inputs/liwc.dic']
liwc_only = liwc + ['-f', '["liwcFeature"]']
static_params = ['--min-df=3', '--n-folds=10', '--n-examples=30']
reduce_func = ['-r', 'lambda x,y: x or y']
svm_options = ['--clf-options={"kernel":"linear","class_weight":"auto"}']
logreg_options = ['--clf-options={"class_weight":"auto"}']

for clf in clf_list:
    clf_str = ['--clf=' + clf]
    if clf == 'logistic-reg':
        options = logreg_options
    elif clf == 'svm':
        options = svm_options
    else:
        options = []

    for k in k_range:
        name = '../stats/' + clf + "k" + str(k)
        sys.stderr.write("Writing benchmark to " + name + "\n")
        k_opt = ['-k', str(k)]
        with open(name, 'w') as f:
            sys.stdout = f
            cli.main(begin + emoticons + stopwords + k_opt + liwc + static_params + clf_str
                     + options)
