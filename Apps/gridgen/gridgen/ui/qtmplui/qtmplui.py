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

        self.statusBar().showMessage("GEA-INPE", 2011)

    def updateLatLonEdits(self):
        self.latEdit.setText(str(self._figure.lat_0))
        self.lonEdit.setText(str(self._figure.lon_0))

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
    def on_moveUpButton_clicked(self, checked):
        print 'up!'
        self._figure.plot_grid(lat_0=self._figure.lat_0 + 5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveDownButton_clicked(self):
        print 'down!'
        self._figure.plot_grid(lat_0=self._figure.lat_0 - 5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveLeftButton_clicked(self):
        print 'left!'
        self._figure.plot_grid(lon_0=self._figure.lon_0 - 5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveRightButton_clicked(self):
        print 'right!'
        self._figure.plot_grid(lon_0=self._figure.lon_0 + 5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_zoomInButton_clicked(self):
        print 'zoom in!'

    @QtCore.pyqtSignature('bool')
    def on_zoomOutButton_clicked(self):
        print 'zoom out!'

    @QtCore.pyqtSignature('bool')
    def on_zoomSlider_sliderReleased(self):
        print 'slider changed'

    def on_actionQuit_triggered(self):
        self.close()

    def closeEvent(self, ce):
        self.close()
