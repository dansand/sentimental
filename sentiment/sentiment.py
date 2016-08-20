import io
import re

import click
import requests
import nltk
from nltk.corpus import movie_reviews
from bs4 import BeautifulSoup
from newspaper import Article
from collections import namedtuple

SentimentalArticle = namedtuple('SentimentalArticle', 'author title body')


@click.group()
def cli():
    """
    Welcome to sentimental!

    This is a small program built to perform some simple sentiment mining.
    Please browse the relevant commands below.
    """

    pass


@cli.command()
@click.option('--url', help='Search URL returned by a Google News query', type=str, required=True)
@click.option('--output-file', help='Write articles to this file.', type=click.Path(writable=True),
              default='output.txt')
def get_articles(url, output_file):
    """
    Search, query, and download articles from the web.
    :param url: URL string from a Google News query.
    """

    get_articles_run(url, output_file)


@cli.command()
@click.option('--input-file', help='Previously downloaded txt file',
              type=click.Path(exists=True, readable=True), required=True)
def get_sentiment(input_file):
    """
    Perform sentiment analysis on downloaded files.
    :param input_file: Result of get_articles.
    :return:
    """

    articles = parse_downloaded_file(input_file)
    for article in articles:
        analyse(article.body)


def features(words):
    """
    Using a simplified bag of words model. Features are the words themselves.
    :param words: List of words to analyse.
    :return: Dictionary of words with tag 'True'.
    """
    return dict([(word, True) for word in words])


def analyse(raw_text):
    """
    Perform sentiment analysis on a string.
    :param raw_text: String of interest.
    :type raw_text: str
    :return:
    """

    # Tokenize the raw text and transform to something NLTK understands.
    text = nltk.word_tokenize(raw_text)
    query = features(text)

    # Get positive and negative reviews.
    neg_ids = movie_reviews.fileids('neg')
    pos_ids = movie_reviews.fileids('pos')

    # Get the words in each review.
    neg_features = [(features(movie_reviews.words(fileids=[f])), 'neg')
                    for f in neg_ids]
    pos_features = [(features(movie_reviews.words(fileids=[f])), 'pos')
                    for f in pos_ids]

    # Get percentage to use in training.
    cutoff = int(len(neg_features) * 3 / 4)

    # Separate into training and testing sets.
    train = neg_features[:cutoff] + pos_features[:cutoff]
    test = neg_features[cutoff:] + pos_features[cutoff:]

    # Train with NaiveBayes classifier.
    classifier = nltk.classify.NaiveBayesClassifier.train(train)
    return classifier.classify(query)


def parse_downloaded_file(input_file):
    """
    Open a previously downloaded news archive, and split into articles.
    :param input_file: Path to downloaded file.
    :return: List of named tuples containing SentimentalArticles.
    """

    with io.open(input_file, 'r', encoding='utf-8') as fh:
        lines = fh.read()

    body, header = [], []
    segments = lines.split('-' * 80)
    for i, s in enumerate(segments):
        # Even numbers are article bodies
        if i != 0 and not i % 2:
            body.append(s)
        # Odd numbers are the headers.
        elif i % 2:
            clean = re.split('AUTHORS: |TITLE: ', s.replace('\n', '').strip())[1:]
            header.append({'AUTHORS': clean[0].strip(),
                           'TITLE': clean[1].strip()})

    return [SentimentalArticle(author=h['AUTHORS'], title=h['TITLE'], body=b)
            for h, b in zip(header, body)]


def get_articles_run(url, output_file):
    """
    Search, query, and download articles from the web.
    """

    # Get raw html from server.
    raw = requests.get(url)

    # Parse html.
    soup = BeautifulSoup(raw.text, 'html.parser')

    # Find all external links in file, and save
    valid_links = []
    for link in soup.find_all('a'):
        trial_link = link.get('href')
        if trial_link.startswith('/url?q='):
            # Actual seems to be bounded by above string and ampersand
            valid_links.append(trial_link[7:].split('&')[0])

    # Remove duplicates
    valid_links = sorted(list(set(valid_links)))

    # Download articles
    full_text = []
    with click.progressbar(valid_links[:5], label="Downloading...") as bar:
        for link in bar:
            article = Article(link)
            article.download()
            article.parse()
            full_text.append(
                {"authors": u','.join(article.authors).encode('utf-8'),
                 "date": article.publish_date,
                 "title": u''.join(article.title).encode('utf-8'),
                 "body": u''.join(article.text).encode('utf-8'),
                 'additional': article.meta_data})

    # Write formatted output to file
    with io.open(output_file, 'w', encoding='utf-8') as fh:
        for article in full_text:
            # Header
            fh.write('-' * 80 + '\n')
            fh.write('AUTHORS:  ' + article['authors'].decode('utf-8') + '\n')
            fh.write('TITLE:    ' + article['title'].decode('utf-8') + '\n')
            fh.write('-' * 80 + '\n')
            # Article
            fh.write(article['body'].decode('utf-8') + '\n\n')
