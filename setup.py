from __future__ import unicode_literals
from setuptools import setup, find_packages

from jira_agile_extractor import jira_agile_extractor


README = file('README.md', 'r').read()
version = ".".join(map(str, jira_agile_extractor.__version__))
author = jira_agile_extractor.__author__
description = jira_agile_extractor.__doc__

setup(
    name='jira-agile-extractor',
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
    url='http://github.com/joke2k/django-environ',
    license='MIT License',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
)
