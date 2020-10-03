#!/usr/bin/env python3

from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='beancount_share',
    version='0.0.1',
    description='Plugin for Beancount to share expenses.',

    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Kalvis \'Akuukis\' Kalnins',
    author_email='akuukis@kalvis.lv',
    download_url='https://pypi.python.org/pypi/beancount_share',
    license='GNU GPLv3',
    package_data={'beancount_share': ['../README.md']},
    package_dir={'beancount_share': 'beancount_share'},
    packages=['beancount_share'],
    requires=['beancount (>2.0)'],
    url='https://github.com/Akuukis/beancount_share',
)
