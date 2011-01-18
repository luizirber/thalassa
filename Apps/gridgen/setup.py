#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

classifiers = """\
Development Status :: 3 - Alpha
Environment :: X11 Applications :: Qt
Intended Audience :: Science/Research
Intended Audience :: Developers
Intended Audience :: Education
License :: OSI Approved :: GNU General Public License (GPL)
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Education
Topic :: Software Development :: Libraries :: Python Modules
"""

setup(name             = 'gridgen',
      version          = '1.0',
      author           = 'Luiz Irber',
      author_email     = 'luiz.irber@cptec.inpe.br',
      maintainer       = 'Luiz Irber',
      maintainer_email = 'luiz.irber@gmail.com',
      url              = 'http://www.ccst.inpe.br',
      description      = 'Grid editor for ocean models',
      long_description = """\
Grid editor for ocean models
""",
      download_url     = 'http://pypi.python.org/packages/source/g/gridgen/',
      packages         = ['gridgen', 'gridgen.ui'],
      classifiers      = filter(None, classifiers.split("\n")),
      platforms        = 'any',
      license          = 'GPL',
      keywords         = 'oceanography modeling',
    )
