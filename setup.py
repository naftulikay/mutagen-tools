#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "mutagentools",
    version = "1.0.0",
    packages = find_packages('src'),
    package_dir = { '': 'src'},
    author = "Naftuli Kay",
    author_email = "me@naftuli.wtf",
    url = "https://github.com/naftulikay/mutagen-tools",
    install_requires = [
        'setuptools',
        'mutagen',
    ],
    dependency_links = [],
    entry_points = {
        'console_scripts': [
            'flac2id3 = mutagentools.cli.flac2id3:main',
            'flacjson = mutagentools.cli.flacjson:main',
            'id3-clean = mutagentools.cli.id3clean:main',
            'id3json = mutagentools.cli.id3json:main',
        ]
    }
)
