# OBOT - 24/7 channel daemon
#
#

from setuptools import setup

def readme():
    with open('README.rst') as file:
        return file.read()

setup(
    name='obot',
    version='21',
    url='https://github.com/bthate/obot',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="24/7 channel daemon",
    long_description=readme(),
    license='Public Domain',
    install_requires=["ob", "feedparser"],
    packages=["obot"],
    scripts=["bin/obot", "bin/obctl", "bin/obotd", "bin/obudp"],
    zip_safe=True,
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: Public Domain',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 'Topic :: Utilities'
                ]
)
