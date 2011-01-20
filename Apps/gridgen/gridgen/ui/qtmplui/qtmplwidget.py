#!/usr/bin/env python

from PyQt4 import QtGui

from gridgen.ui.qtmplui import QtMplCanvas

class QtMplWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.vbl = QtGui.QVBoxLayout()
        self.setLayout(self.vbl)

    def set_canvas(self, figure):
        self.canvas = QtMplCanvas(figure)
        self.vbl.addWidget(self.canvas)
