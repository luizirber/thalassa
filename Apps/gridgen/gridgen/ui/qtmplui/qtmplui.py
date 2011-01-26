#!/usr/bin/env python

import sys

from PyQt4 import QtGui, QtCore

from gridgen.ui import UI, MplUI
from gridgen.ui.qtmplui import Ui_QtMplWindow
from gridgen.ui.qtmplui import QtMplCanvas, QtMplWidget


class QtMplUI(QtGui.QMainWindow, Ui_QtMplWindow, UI):

    def __init__(self, figure):
        super(QtMplUI, self).__init__()
        self.setupUi(self)
        self._figure = figure

        self.mapwidget.set_canvas(self._figure)
        self._figure.plot_grid()
        self.updateLatLonEdits()
        self.updateMinMaxValueEdits()

        self.statusBar().showMessage("GEA-INPE", 2011)

    def updateLatLonEdits(self):
        self.latEdit.setText(str(self._figure.get_plot_property('lat_0')))
        self.lonEdit.setText(str(self._figure.get_plot_property('lon_0')))

    def updateMinMaxValueEdits(self):
        self.minEdit.setText(str(self._figure.min_current_values()))
        self.maxEdit.setText(str(self._figure.max_current_values()))

    @QtCore.pyqtSignature('bool')
    def on_goLatLonButton_clicked(self, checked):
        try:
            new_lat = float(self.latEdit.text())
        except ValueError:
            pass # TODO: raise error

        try:
            new_lon = float(self.lonEdit.text())
        except ValueError:
            pass # TODO: raise error

        # TODO: validade inputs
        self._figure.plot_grid(lat_0=new_lat, lon_0=new_lon)
        self.updateLatLonEdits()
        print 'new position!!'

    @QtCore.pyqtSignature('bool')
    def on_valueRangeButton_clicked(self):
        print 'change range!'
        try:
            new_min = float(self.minEdit.text())
        except ValueError:
            pass # TODO: raise error

        try:
            new_max = float(self.maxEdit.text())
        except ValueError:
            pass # TODO: raise error
        self._figure.plot_grid(vmin=new_min, vmax=new_max)
        self.updateMinMaxValueEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveUpButton_clicked(self, checked):
        print 'up!'
        self._figure.rotate(lat_delta=5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_depthRadioButton_toggled(self, checked=False):
        print 'plot depth'
        self._figure.plot_depth_t()
        self.updateMinMaxValueEdits()

    @QtCore.pyqtSignature('bool')
    def on_levelsRadioButton_toggled(self, checked=False):
        print 'plot levels'
        self._figure.plot_num_levels()
        self.updateMinMaxValueEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveDownButton_clicked(self):
        print 'down!'
        self._figure.rotate(lat_delta=-5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveLeftButton_clicked(self):
        print 'left!'
        self._figure.rotate(lon_delta=-5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveRightButton_clicked(self):
        print 'right!'
        self._figure.rotate(lon_delta=5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_zoomInButton_clicked(self):
        print 'zoom in!'
        self._figure.zoom_in()

    @QtCore.pyqtSignature('bool')
    def on_zoomOutButton_clicked(self):
        print 'zoom out!'
        self._figure.zoom_out()

    def on_zoomSlider_sliderReleased(self):
        print 'slider released', self.zoomSlider.value()
        self._figure.zoom(self.zoomSlider.value())

    def on_actionQuit_triggered(self):
        self.close()

    def closeEvent(self, ce):
        self.close()
