from setuptools import setup

def readme():
    with open('README') as file:
        return file.read()

setup(
    name='obot',
    version='19',
    url='https://bitbucket.org/bthate/obot',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="24/7 channel daemon",
    long_description=readme(),    
    license='Public Domain',
    zip_safe=True,
    install_requires=["olib", "omod"],
    packages=["omod"],
    namespace_packages=["omod"],
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: Public Domain',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 'Topic :: Utilities'
                ]
)
