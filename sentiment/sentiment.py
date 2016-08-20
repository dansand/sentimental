import io

import click
import requests
from bs4 import BeautifulSoup
from newspaper import Article


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
def get_articles(url):
    """
    Search, query, and download articles from the web.
    :param url: URL string from a Google News query.
    """

    get_articles_run(url)


def get_articles_run(url):
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
    with io.open('output.txt', 'w', encoding='utf-8') as fh:
        for article in full_text:
            # Header
            fh.write('-' * 80 + '\n')
            fh.write('AUTHORS:  ' + article['authors'].decode('utf-8') + '\n')
            fh.write('TITLE:    ' + article['title'].decode('utf-8') + '\n')
            fh.write('-' * 80 + '\n')
            # Article
            fh.write(article['body'].decode('utf-8') + '\n\n')
