#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='nose-timer',
    version='0.7.0',
    description='A timer plugin for nosetests',
    long_description=open('README.rst').read(),
    author=', '.join([
        'Juan Pedro Fisanotti',
        'Mahmoud Abdelkader',
        'Andres Riancho',
        'Ivan Kolodyazhny',
        'Kevin Burke',
        'Anton Egorov',
        'Dmitry Sandalov',
        'Stanislav Kudriashev',
        'Raoul Snyman',
        'Corey Goldberg',
        'Harald Nordgren',
    ]),
    url='https://github.com/mahmoudimus/nose-timer',
    packages=['nosetimer', ],
    install_requires=[
        'nose',
        'termcolor',
        'ordereddict',
    ],
    license='MIT',
    entry_points={
        'nose.plugins.0.10': [
            'nosetimer = nosetimer.plugin:TimerPlugin',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Testing',
        'Environment :: Console',
    ],
)
