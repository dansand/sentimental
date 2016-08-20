import io
import os

from sentiment import sentiment


def test_get_articles():
    # Path to first page of Sault articles.
    test_url = u'https://www.google.com/search?cf=all&hl=en&pz=1&ned=ca&tbm=nws&gl=ca&as_q' \
               '=Makayla%20Sault&as_occt=any&tbs=ar%3A1&authuser=0'.encode('utf-8')

    # Get test Sault articles.
    sentiment.get_articles_run(test_url)

    # Ensure that it is the same as that saved.
    with io.open(os.path.join('tests/data/trial_output.txt'), 'r', encoding='utf-8') as fh:
        ideal = fh.readlines()
    with io.open(os.path.join('output.txt'), 'r', encoding='utf-8') as fh:
        actual = fh.readlines()
    assert actual == ideal
    os.remove(os.path.join('output.txt'))

