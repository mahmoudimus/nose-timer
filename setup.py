#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

with open('nosetimer/__init__.py') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='nose-timer',
    version=version,
    description='A timer plugin for nosetests',
    long_description=long_description,
    author=', '.join([
        'Alister Cordiner',
        'Andres Riancho',
        'Anton Egorov',
        'Arthur Kulik',
        'Corey Goldberg',
        'Dmitry Sandalov',
        'Harald Nordgren',
        'Ivan Kolodyazhny',
        'Juan Pedro Fisanotti',
        'Kevin Burke',
        'Mahmoud Abdelkader',
        'Raoul Snyman',
        'Stanislav Kudriashev',
    ]),
    url='https://github.com/mahmoudimus/nose-timer',
    packages=[
        'nosetimer',
    ],
    install_requires=[
        'nose',
    ],
    license='MIT',
    entry_points={
        'nose.plugins.0.10': [
            'nosetimer = nosetimer.plugin:TimerPlugin',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
)
