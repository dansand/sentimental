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
def get_articles():
    """
    Search, query, and download articles from the web.
    """

    # Get raw html from server.
    url = 'https://www.google.com/search?cf=all&hl=en&pz=1&ned=ca&tbm=nws&gl=ca&as_q' \
          '=Makayla%20Sault&as_occt=any&tbs=ar%3A1&authuser=0'
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
    valid_links = list(set(valid_links))

    # Download articles
    full_text = []
    with click.progressbar(valid_links[:5], label="Downloading...") as bar:
        for link in bar:
            article = Article(link)
            article.download()
            article.parse()
            full_text.append(
                {"authors": ','.join(article.authors),
                 "date": article.publish_date,
                 "title": article.title,
                 "body": article.text,
                 'additional': article.meta_data})

    # Write formatted output to file
    with open('output.txt', 'w') as fh:
        for article in full_text:
            # Header
            fh.write('-' * 80 + '\n')
            fh.write('AUTHORS:  ' + article['authors'] + '\n')
            fh.write('TITLE:    ' + article['title'] + '\n')
            fh.write('-' * 80 + '\n')
            # Article
            fh.write(article['body'] + '\n\n')
