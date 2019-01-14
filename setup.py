"""Fast, unsupervised biomedical concept extraction from medical text.

NOTE: 
Skeleton for this and some comments came from PyPA sample project which illustrates a sample setuptools project:
https://github.com/pypa/sampleproject

See:
https://github.com/Georgetown-IR-Lab/QuickUMLS
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='QuickUMLS',
    version='1.3.0',
    description='Fast, unsupervised biomedical concept extraction from medical text',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Georgetown-IR-Lab/QuickUMLS',
    author='Georgetown Information Retrieval Lab',

    classifiers=[
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',
        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='nlp umls ner',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # NOTE : For Windows, easiest way to build simstring is with Visual Studio and Anaconda for dependencies
    install_requires=['simstring', 'leveldb'],

    project_urls={
        'Bug Reports': 'https://github.com/Georgetown-IR-Lab/QuickUMLS/issues',
        'Source': 'https://github.com/Georgetown-IR-Lab/QuickUMLS',
    },
)
