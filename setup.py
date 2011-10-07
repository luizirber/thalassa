#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup, Command
from distutils.command.build import build as _build_orig
from distutils.filelist import findall
from os.path import join, dirname
import sys

from setup_utils import build_qt_ui

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

setup(name             = 'Thalassa',
      version          = '1.0',
      author           = 'Luiz Irber',
      author_email     = 'luiz.irber@cptec.inpe.br',
      maintainer       = 'Luiz Irber',
      maintainer_email = 'luiz.irber@gmail.com',
      url              = 'https://bitbucket.org/luizirber/thalassa',
      description      = 'Grid editor for ocean models',
      long_description = """\
Grid editor for ocean models
""",
      packages         = ['thalassa', 'thalassa.ui', 'thalassa.ui.qtmplui', 'thalassa.grid'],
      scripts          = ["bin/thalassa"],
      cmdclass         = cmdclass,
      classifiers      = filter(None, classifiers.split("\n")),
      platforms        = 'any',
      license          = 'GPL',
      keywords         = 'oceanography modeling',
      **kwargs
    )
