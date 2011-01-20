#!/usr/bin/env python

from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg


class QtMplCanvas(FigureCanvasQTAgg):
    def __init__(self, figure):
        self.fig = figure
        FigureCanvasQTAgg.__init__(self, self.fig)
        FigureCanvasQTAgg.setSizePolicy(self,
                                        QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)
