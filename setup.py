#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# OBOT - object bot. 

""" setup.py """

from setuptools import setup

def readme():
    with open('README.rst') as file:
        return file.read()

setup(
    name='obot',
    version='16',
    url='https://bitbucket.org/bthate/obot',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Framework to program bots",
    long_description=readme(),
    long_description_content_type="text/markdown",
    license='Public Domain',
    zip_safe=True,
    install_requires=["ob"],
    packages=["obot"],
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: Public Domain',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 'Topic :: Utilities'
                ]
)
