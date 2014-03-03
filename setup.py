#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='nose-timer',
    version='0.3.0',
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
    ]),
    url='https://github.com/mahmoudimus/nose-timer',
    packages=['nosetimer', ],
    license='LICENSE',
    entry_points='''
        [nose.plugins.0.10]
        nosetimer = nosetimer:TimerPlugin
    ''',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing',
        'Environment :: Console',
    ],
)
