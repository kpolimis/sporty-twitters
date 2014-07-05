from cli import cli
import sys
import numpy as np
import csv
import os
from collections import OrderedDict

clf_list = ['logistic-reg', 'svm', 'decision-tree', 'naive-bayes', 'kneighbors']
k_range = np.arange(300, 0, -30)

binary_choice = [True, False]
begin = ['mood', 'benchmark', '-t', '../inputs/3K_labeled']
emoticons = ['-e', '../inputs/params/emoticons']
stopwords = ['-s', '../inputs/params/stopwords']
liwc = ['--liwc', '../inputs/liwc.dic']
liwc_only = liwc + ['-f', '["liwcFeature"]']
static_params = ['--min-df=3', '--n-folds=10', '--n-examples=30']
reduce_func = ['-r', 'lambda x,y: x or y']
svm_options = ['--clf-options={"kernel":"linear","class_weight":"auto"}']
logreg_options = ['--clf-options={"class_weight":"auto"}']

fstats = open("../stats/cumulated_stats", "w")
first_write = True
cumulated_stats = []
cmd = []

for emo_cond in binary_choice:
    # empty command at the beginning of each iteration
    cmd = []
    cmd += begin
    # empty stats dictionary
    stats = OrderedDict()

    stats['emoticons'] = emo_cond
    if emo_cond:
        cmd += emoticons
    for sw_cond in binary_choice:
        stats['stopwords'] = sw_cond
        if sw_cond:
            cmd += stopwords
        for liwc_cond in binary_choice:
            stats['liwc'] = liwc_cond
            if liwc_cond:
                cmd += liwc
            for reduce_cond in binary_choice:
                stats['reduce'] = reduce_cond
                if reduce_cond:
                    cmd += reduce_func
                for clf in clf_list:
                    stats['clf'] = clf
                    clf_str = ['--clf=' + clf]
                    if clf == 'logistic-reg':
                        options = logreg_options
                    elif clf == 'svm':
                        options = svm_options
                    else:
                        options = []
                    cmd += clf_str + options
                    cmd += static_params
                    for k in k_range:
                        stats['k'] = k
                        name = '../stats/' +
                        '_'.join([v[0] + str(stats[v]) for v in stats.keys() if v != 'rocauc'])
                        sys.stderr.write("Writing benchmark to " + name + "\n")
                        k_opt = ['-k', str(k)]
                        try:
                            with open(name, 'w') as f:
                                sys.stdout = f
                                stats['rocauc'] = cli.main(cmd + k_opt)
                                w = csv.DictWriter(fstats, stats.keys())
                                if first_write:
                                    w.writeheader()
                                    first_write = False
                                w.writerow(stats)
                                fstats.flush()
                        except ValueError, e:
                            sys.stderr.write(str(e) + "\n")
                            os.remove(name)
                            continue
                    [cmd.pop(-1) for x in clf_str + options + static_params]
                if reduce_cond:
                    [cmd.pop(-1) for x in reduce_func]
            if liwc_cond:
                [cmd.pop(-1) for x in liwc]
        if sw_cond:
            [cmd.pop(-1) for x in stopwords]
    if emo_cond:
        [cmd.pop(-1) for x in emoticons]
    sys.stderr.write(str(cumulated_stats))
