#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from os.path import isdir, exists, join, walk, splitext

class build_qt(build):
    def compile_ui(self, ui_file, py_file=None):
        if py_file is None:
            py_file = splitext(ui_file)[0] + ".py"
        try:
            from PyQt4 import uic
            fp = open(py_file, 'w')
            uic.compileUi(ui_file, fp)
            fp.close()
            print "compiled", ui_file, "into", py_file
        except Exception, e:
            print 'Unable to compile user interface', e
            return

    def compile_rc(self, qrc_file, py_file=None):
        if py_file is None:
            py_file = splitext(qrc_file)[0] + "_rc.py"
        if os.system('pyrcc4 "%s" -o "%s"' % (qrc_file, py_file)) > 0:
            print "Unable to generate python module for resource file", qrc_file

    def run(self):
        for dirpath, _, filenames in os.walk('data'):
            for filename in filenames:
                if filename.endswith('.ui'):
                    self.compile_ui(join(dirpath, filename),
                        os.path.join('gridgen', 'ui', ''))
                elif filename.endswith('.qrc'):
                    self.compile_rc(join(dirpath, filename))
        build.run(self)

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
