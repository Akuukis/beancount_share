#!/usr/bin/env python3

from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='beancount_share',
    version='0.1.10',
    description='Plugin for Beancount to share expenses.',

    long_description=long_description,
    long_description_content_type='text/markdown',

    author='Akuukis',
    author_email='akuukis@kalvis.lv',
    download_url='https://pypi.python.org/pypi/beancount_share',
    license='GNU AGPLv3',
    package_data={'beancount_share': ['../README.md', 'requirements.txt']},
    package_dir={'beancount_share': 'beancount_share'},
    packages=['beancount_share'],
    install_requires=['beancount >= 2.0', 'beancount_plugin_utils >= 0.0.4'],
    url='https://github.com/Akuukis/beancount_share',
)
