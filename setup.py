#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='nose-timer',
    version='0.7.3',
    description='A timer plugin for nosetests',
    long_description=open('README.rst').read(),
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
    packages=['nosetimer', ],
    install_requires=[
        'nose',
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Testing',
        'Environment :: Console',
    ],
)
