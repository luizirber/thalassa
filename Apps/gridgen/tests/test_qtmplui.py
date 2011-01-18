import os
from os.path import join, abspath
import sys

import pytest
from PyQt4 import QtGui

from gridgen import Grid
from gridgen.ui import QtMplUI


def test_qtmplui(tmpdir, testdata):
    qApp = QtGui.QApplication(sys.argv)

    aw = QtMplUI()
    aw.setWindowTitle("GridGen")  # TODO: change to final name
    aw.show()
    sys.exit(qApp.exec_())
