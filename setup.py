# This file is placed in the Public Domain

from setuptools import setup

def readme():
    with open('README.rst') as file:
        return file.read()

setup(
    name='obot',
    version='22',
    url='https://github.com/bthate/obot',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="bot library",
    long_description=readme(),
    license='Public Domain',
    install_requires=["ob", "feedparser"],
    packages=["obot"],
    zip_safe=True,
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: Public Domain',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 'Topic :: Utilities'
                ]
)
