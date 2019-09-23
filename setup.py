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
    version='11',
    url='https://bitbucket.org/bthate/obot',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="pure python3 channel bot.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    license='Public Domain',
    zip_safe=True,
    install_requires=["feedparser", "dnspython", "pyasn1_modules==0.1.5", "pyasn1==0.3.6", "sleekxmpp==1.3.1"],
    scripts=["bin/obot", "bin/ob", "bin/obd", "bin/obs", "bin/obudp", "bin/obps"],
    packages=["ob", "ob.cmd", "obot"],
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: Public Domain',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 'Topic :: Utilities'
                ]
)
