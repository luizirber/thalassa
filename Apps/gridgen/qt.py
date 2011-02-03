#!/usr/bin/env python

import sys

from PyQt4 import QtGui
import matplotlib
matplotlib.use('QT4Agg')

from gridgen.ui import QtMplUI


qApp = QtGui.QApplication(sys.argv)

aw = QtMplUI()
aw.show()
sys.exit(qApp.exec_())
