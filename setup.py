#! /usr/bin/env python

DISTNAME = 'dbpediakit'
DESCRIPTION = """Python / SQL utilities to work with the DBpedia dumps"""
LONG_DESCRIPTION = open('README.md').read()
MAINTAINER = 'Olivier Grisel'
MAINTAINER_EMAIL = 'olivier.grisel@ensta.org'
URL = 'https://github.com/ogrisel/dbpediakit'
LICENSE = 'MIT'
VERSION = '0.1-git'

from distutils.core import setup


if __name__ == "__main__":

    setup(name=DISTNAME,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          url=URL,
          version=VERSION,
          long_description=LONG_DESCRIPTION,
          classifiers=[
              'Intended Audience :: Science/Research',
              'Intended Audience :: Developers',
              'License :: OSI Approved',
              'Programming Language :: Python',
              'Programming Language :: SQL',
              'Topic :: Software Development',
              'Topic :: Scientific/Engineering',
              'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Operating System :: MacOS'
             ]
    )
