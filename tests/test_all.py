import io
import os
import nltk

import pickle
from sentiment import sentiment


def test_get_articles():
    """
    Test whether or not we can download a known set of files. Note that this will probably fail once google news is
    updated.
    """
    # Path to first page of Sault articles.
    test_url = u'https://www.google.com/search?cf=all&hl=en&pz=1&ned=ca&tbm=nws&gl=ca&as_q' \
               '=Makayla%20Sault&as_occt=any&tbs=ar%3A1&authuser=0'.encode('utf-8')

    # Get test Sault articles.
    sentiment.get_articles_run(test_url, 'output.txt')

    # Ensure that it is the same as that saved.
    with io.open(os.path.join('tests/data/trial_output.txt'), 'r', encoding='utf-8') as fh:
        ideal = fh.readlines()
    with io.open(os.path.join('output.txt'), 'r', encoding='utf-8') as fh:
        actual = fh.readlines()
    assert actual == ideal
    os.remove(os.path.join('output.txt'))


def test_parse_files():
    """
    Test whether we can properly parse a downloaded text file.
    """
    with io.open('tests/data/trial_parse.pkl', 'rb') as fh:
        ideal = pickle.load(fh)
    assert sentiment.parse_downloaded_file(os.path.join('./tests/data/trial_output.txt')) == ideal


def test_get_sentiment():
    """
    Test whether we get the sentiments we expect.
    """
    nltk.download('punkt')
    ground_truth = ['pos', 'pos', 'pos', 'pos', 'pos']
    articles = sentiment.parse_downloaded_file('./tests/data/trial_output.txt')
    for t, article in zip(ground_truth, articles):
        assert t == sentiment.analyse(article.body)
