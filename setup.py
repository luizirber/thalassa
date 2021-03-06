#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

from distutils.core import Command
from distutils.command.build import build as _build_orig
from distutils.filelist import findall
import os
from os.path import isdir, exists, join, splitext, split, dirname
import sys


def compile_ui(ui_file, py_dir=None):
    if py_dir is None:
        py_dir = ''
    py_file = join(py_dir, splitext(split(ui_file)[-1])[0] + ".py")
    try:
        from PyQt4 import uic
        fp = open(py_file, 'w')
        uic.compileUi(ui_file, fp)
        fp.close()
        print "compiled", ui_file, "into", py_file
    except Exception, e:
        print 'Unable to compile user interface', e
        return

def compile_rc(qrc_file, py_dir=None):
    if py_dir is None:
        py_dir = ''
    py_file = join(py_dir, splitext(split(qrc_file)[-1])[0] + "_rc.py")
    if os.system('pyrcc4 "%s" -o "%s"' % (qrc_file, py_file)) > 0:
        print "Unable to generate python module for resource file", qrc_file
    else:
        print "compiled", qrc_file, "into", py_file

def build_qt_ui(src='data', dest=''):
    print src, dest
    for dirpath, _, filenames in os.walk(src):
        for filename in filenames:
            if filename.endswith('.ui'):
                compile_ui(join(dirpath, filename),
                    os.path.join(dest, 'thalassa', 'ui', 'qtmplui'))
            elif filename.endswith('.qrc'):
                compile_rc(join(dirpath, filename),
                    os.path.join(dest, 'thalassa', 'ui', 'qtmplui'))


class generate_qtui(Command):

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        build_qt_ui()


class build(_build_orig):
    sub_commands = [
        ('generate_qtui', None)
        ] + _build_orig.sub_commands

cmdclass = {
    'build': build,
    'generate_qtui': generate_qtui,
}

kwargs = {}
data_files = []
if 'py2exe' in sys.argv:
    import py2exe
    import matplotlib
    import mpl_toolkits.basemap as basemap

    data_files = matplotlib.get_py2exe_datafiles()
    data_files.append((join('mpl_toolkits', 'basemap', 'data'),
                       findall(join(dirname(basemap.__file__), 'data')) ))
    kwargs['windows'] = [{'script': "bin/thalassa",
                          'data_files': data_files}],
    kwargs['options'] = {"py2exe": {"skip_archive":True,
                                    "includes": ["sip", "netCDF4_utils",
                                                 "netcdftime", "mpl_toolkits.basemap"],
                                    "dll_excludes": ["MSVCP90.dll"]}},

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


long_description = """\
Grid editor for ocean models. Supports MOM4p1 grids (tested with tripolar grids)
and outputs a file ready to be used as input for edit_grid.
"""

requires = ['matplotlib', 'basemap', 'numpy', 'netCDF4', 'PIL']

setup(name             = 'Thalassa',
      version          = '1.2',
      author           = 'Luiz Irber',
      author_email     = 'luiz.irber@cptec.inpe.br',
      maintainer       = 'Luiz Irber',
      maintainer_email = 'luiz.irber@gmail.com',
      url              = 'https://bitbucket.org/luizirber/thalassa',
      description      = 'Grid editor for ocean models',
      long_description = long_description,
      packages         = ['thalassa', 'thalassa.ui', 'thalassa.ui.qtmplui', 'thalassa.grid'],
      scripts          = ["bin/thalassa"],
      cmdclass         = cmdclass,
      install_requires = requires,
      classifiers      = filter(None, classifiers.split("\n")),
      platforms        = 'any',
      license          = 'GPL',
      keywords         = 'oceanography modeling',
      **kwargs
    )
