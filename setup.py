#!/usr/bin/env python
from setuptools import setup, find_packages

PACKAGENAME = 'pytest_docstring'
VERSION = ''
DESCRIPTION = ''
AUTHOR = "Dan D'Avella"
AUTHOR_EMAIL = 'ddavella@stsci.edu'
LICENSE = ''
URL = ''
LONG_DESCRIPTION  = ''

entry_points = {
    'pytest11': ['docstring = pytest_docstring.plugin']
}

setup(name=PACKAGENAME,
      version=VERSION,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      url=URL,
      long_description=LONG_DESCRIPTION,
      entry_points=entry_points,
      packages=find_packages('src'),
      package_dir={'' : 'src'},
      py_modules=['pytest_docstring'],
      zip_safe = False,
      classifiers = [
          'Framework :: Pytest'
      ]
)
