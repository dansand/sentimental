from setuptools import setup

setup(
    name='sentimental',
    entry_points='''
    [console_scripts]
    sentimental=sentiment.sentiment:cli
    ''', install_requires=['newspaper3k', 'click', 'bs4']
)