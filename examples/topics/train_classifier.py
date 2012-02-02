import numpy as np
import sys
import csv
from time import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.utils import shuffle


def parse_multilabel_dataset(filename):
    """Each document is assigned one or several labels"""
    documents = []
    target = []
    all_categories = set()
    with open(filename, 'rt') as f:
        for _, cats, text in csv.reader(f, dialect="excel"):
            documents.append(text)
            cats = cats.split()
            target.append(cats)
            all_categories.update(cats)
    target_names = np.array(list(sorted(all_categories)))
    target_vocabulary = dict((cat, i) for i, cat in enumerate(target_names))
    target = [[target_vocabulary[c] for c in cats] for cats in target]
    return documents, target, target_names, target_vocabulary


def parse_multiclass_dataset(filename):
    """Each document is classified in one and only one class"""
    documents = []
    target = []
    with open(filename, 'rt') as f:
        for _, cats, text in csv.reader(f, dialect="excel"):
            documents.append(text)
            cats = cats.split()
            target.append(cats[0])
    all_categories = set(target)
    target_names = np.array(list(sorted(all_categories)))
    target_vocabulary = dict((cat, i) for i, cat in enumerate(target_names))
    target = [target_vocabulary[c] for c in target]
    return documents, target, target_names, target_vocabulary


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Examples CSV file required as command line argument"
        sys.exit(1)
    examples_filename = sys.argv[1]
    # parse the CSV file and treat is a multiclass problem
    documents, target, target_names, target_vocabulary = \
            parse_multiclass_dataset(examples_filename)

    # split the dataset into a trainin and test set
    n_samples = len(documents)
    n_split = int(2. / 3 * n_samples)
    documents, target = shuffle(documents, target, random_state=0)
    doc_train, doc_test = documents[:n_split], documents[n_split:]
    target_train, target_test = target[:n_split], target[n_split:]

    # build a processing pipeline with a text feature extractor and a
    # multilabel classifier (compound perceptrons in one-vs-the-rest
    # scheme for each target).
    pipeline = Pipeline([
        ('vect', CountVectorizer(max_df=0.75)),
        ('tfidf', TfidfTransformer()),
        ('clf', SGDClassifier(loss='hinge', penalty="elasticnet",
                              alpha=0.00001, n_iter=10))
    ])
    #pipeline.set_params(vect__analyzer__max_n=2)

    # train the model on the dataset
    print "Training model..."
    t0 = time()
    pipeline.fit(doc_train, target_train)
    print "done in %0.3fs" % (time() - t0)

    # evaluate the model prediction on the held out data
    print "Predicting on evaluation set..."
    t0 = time()
    predicted = pipeline.predict(doc_test)
    print "done in %0.3fs" % (time() - t0)

    print classification_report(target_test, predicted,
                                target_names=target_names)
