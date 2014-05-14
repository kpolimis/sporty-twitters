from build_features import *
from sklearn import cross_validation
from sklearn import svm
import numpy as np
from sklearn import metrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stopwords", "-sw", type=str, default='')
    args = parser.parse_args()

    if args.stopwords:
        with open(args.stopwords, "r") as sw_file:
            sw = set(x.strip() for x in sw_file)

    corpus, labels = build_features(stopwords=sw, label=True, binary=True)
    X = get_X(corpus, labels)

    clf = svm.SVC(kernel='linear', C=1)#.fit(X_train, y_train)

    scores = cross_validation.cross_val_score(clf, X, labels, cv=10)
    print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))