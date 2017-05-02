#!/usr/bin/env python3

import sys

from setuptools import setup, find_packages
from setuptools.command.install import install
from codecs import open
from os import path

import selfupdate

if sys.version_info < (2, 6):
    print("THIS MODULE REQUIRES PYTHON 2.6, 2.7, OR 3.3+. YOU ARE CURRENTLY USING PYTHON {0}".format(sys.version))
    sys.exit(1)

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="selfupdate",
    version=selfupdate.__version__,

    description="Python project that allow scripts to easily and safely update themselves if they are in a git repo",
    long_description=long_description,

    url="https://github.com/beeedy/SelfUpdate",
    author=selfupdate.__author__,
    author_email=selfupdate.__email__,

    license=selfupdate.__license__,

    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='git autoupdate selfupdate update',
    packages=find_packages(exclude=[]),
    install_requires=['gitpython'],
)