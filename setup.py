from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gps2gis',
    version='0.1.0a1',
    description='Convert text gps log to gis data formats',
    long_description=long_description,
    url='https://github.com/bsurc/gps2gis',
    author='Tyler Bevan',
    author_email='tylerbevan@boisestate.edu',
    license='BSD 3 Clause',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['gdal', 'numpy', 'scipy'],
    entry_points={
        'console_scripts': [
            'gps2gis=gps2gis.main:main',
        ],
    },
)