"""setup."""

from __future__ import unicode_literals
from setuptools import setup, find_packages

from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements("requirements.txt", session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

description = """Pulls data from agile systems and analyzes it."""
author = "cmheisel"
README = open('README.md', 'r').read()
try:
    version = open('version.txt', 'r').read().strip()
except FileNotFoundError:
    version = "unknown"

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
    install_requires=reqs
)
