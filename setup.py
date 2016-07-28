"""setup."""

from __future__ import unicode_literals
from setuptools import setup, find_packages

import agile_analytics


README = open('README.md', 'r').read()
version = ".".join(map(str, agile_analytics.__version__))
author = agile_analytics.__author__
description = agile_analytics.__doc__

setup(
    name='agile-analytics',
    version=version,
    description=description,
    long_description=README,
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='jira agile lean kanban metrics',
    author=author,
    author_email='chris@heisel.org',
    url='https://github.com/cmheisel/agile-analytics',
    license='MIT License',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
)
