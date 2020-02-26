import numpy as np
import os
from xml.etree.cElementTree import iterparse


def process_item(item):
    review = item.find("text").text
    rating = float(item.find("rating").text)

    # category = item.find("category").text
    # asin = item.find("asin").text
    # date = item.find("date").text
    # summary = item.find("summary").text

    return review, rating


def parse_file(file):
    X, y = [], []
    for _, elem in iterparse(file):
        if elem.tag == "item":
            review, rating = process_item(elem)
            if rating <= 2:
                X.append(review)
                y.append(0)
            elif rating >= 4:
                X.append(review)
                y.append(1)
    return np.array(X), np.array(y)


def get_data(folder):
    train_file = os.path.join(folder, 'train.review')
    test_file = os.path.join(folder, 'test.review')

    with open(train_file, 'r') as f_train:
        X_train, y_train = parse_file(f_train)

    with open(test_file, 'r') as f_test:
        X_test, y_test = parse_file(f_test)

    # Stats
    print('> Folder: ' + folder)
    print('  Len Train: {}. Len Test: {}.'.format(len(X_train), len(X_test)))

    return X_train, y_train, X_test, y_test
