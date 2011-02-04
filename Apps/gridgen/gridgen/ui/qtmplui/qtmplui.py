#!/usr/bin/env python

import sys

from PyQt4 import QtGui, QtCore

from gridgen import MOM4Grid
from gridgen.ui import UI, MplUI, MplFigure
from gridgen.ui.qtmplui import Ui_QtMplWindow
from gridgen.ui.qtmplui import QtMplCanvas, QtMplWidget


class QtMplUI(QtGui.QMainWindow, Ui_QtMplWindow, UI):

    def __init__(self):
        super(QtMplUI, self).__init__()
        self.setupUi(self)
        self._figure = None

        self.statusBar().showMessage("GEA-INPE", 2011)

    @QtCore.pyqtSignature('bool')
    def on_actionOpen_triggered(self, checked):
        default_path = 'examples/data/grids_tupa/'
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open file', default_path)
        # TODO: open a dialog, showing the error if this doesn't work.
        raw_grid = MOM4Grid(filename)
        raw_grid.fix()

        self._figure = MplFigure(raw_grid)
        self.mapwidget.set_canvas(self._figure)
        self._figure.plot_grid()
        self.updateLatLonEdits()
        self.updateMinMaxValueEdits()
        self.updateZoomSlider()
        self._figure.set_changed_value_callback(self.updateCellValueEdit)

    def updateLatLonEdits(self):
        self.latEdit.setText(str(self._figure.get_plot_property('lat_0')))
        self.lonEdit.setText(str(self._figure.get_plot_property('lon_0')))

    def updateMinMaxValueEdits(self):
        self.minEdit.setText(str(self._figure.min_current_values()))
        self.maxEdit.setText(str(self._figure.max_current_values()))

    def updateZoomSlider(self):
        self.zoomSlider.setRange(0, self._figure.max_zoom_level)
        self.zoomSlider.setSliderPosition(self._figure.zoom_level)

    def updateCellValueEdit(self):
        if self._figure.selected_cell:
            new_value = self._figure.selected_value()
            self.cellValueEdit.setText("%.2f" % new_value)

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

    @QtCore.pyqtSignature('bool')
    def on_goMatXYButton_clicked(self):
        try:
            new_x = float(self.xPosEdit.text())
        except ValueError:
            pass # TODO: raise error

        try:
            new_y = float(self.yPosEdit.text())
        except ValueError:
            pass # TODO: raise error
        self._figure.change_position(new_x, new_y)

    @QtCore.pyqtSignature('bool')
    def on_valueRangeButton_clicked(self):
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
    def on_changeValueButton_clicked(self):
        new_value = float(self.cellValueEdit.text())
        self._figure.change_value(new_value)

    @QtCore.pyqtSignature('bool')
    def on_depthRadioButton_toggled(self, checked=False):
        self._figure.plot_depth_t()
        self.updateMinMaxValueEdits()

    @QtCore.pyqtSignature('bool')
    def on_levelsRadioButton_toggled(self, checked=False):
        self._figure.plot_num_levels()
        self.updateMinMaxValueEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveUpButton_clicked(self, checked):
        self._figure.rotate(lat_delta=5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveDownButton_clicked(self):
        self._figure.rotate(lat_delta=-5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveLeftButton_clicked(self):
        self._figure.rotate(lon_delta=-5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_moveRightButton_clicked(self):
        self._figure.rotate(lon_delta=5)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_zoomInButton_clicked(self):
        self._figure.zoom_in()
        self.updateZoomSlider()

    @QtCore.pyqtSignature('bool')
    def on_zoomOutButton_clicked(self):
        self._figure.zoom_out()
        self.updateZoomSlider()

    def on_zoomSlider_sliderReleased(self):
        self._figure.zoom(self.zoomSlider.value())

    @QtCore.pyqtSignature('bool')
    def on_actionQuit_triggered(self, checked):
        self.close()

    @QtCore.pyqtSignature('bool')
    def on_actionSave_triggered(self, checked):
        # TODO: return error when location is invalid?
        default_path = 'examples/data/grids_tupa/'
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save file', default_path)
        self._figure.save_diff(filename)

    def closeEvent(self, ce):
        self.close()
