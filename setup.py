#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='nose-timer',
    version='0.1.1',
    description=u'A timer plugin for nosetests',
    long_description=open('README.rst').read(),
    author = u'Juan Pedro Fisanotti',
    author_email = 'fisadev@gmail.com',
    url='https://github.com/fisadev/nose-timer',
    packages=['nosetimer', ],
    license='LICENSE.txt',
    entry_points = '''
        [nose.plugins.0.10]
        nosetimer = nosetimer:TimerPlugin
    ''',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
        'Environment :: Console',
    ],
)
