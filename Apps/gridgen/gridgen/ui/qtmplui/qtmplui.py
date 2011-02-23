#!/usr/bin/env python

from PyQt4 import QtGui, QtCore

from gridgen import MOM4Grid
from gridgen.ui import UI, MplFigure
from gridgen.ui.qtmplui import Ui_QtMplWindow


class QtMplUI(QtGui.QMainWindow, Ui_QtMplWindow, UI):

    def __init__(self):
        super(QtMplUI, self).__init__()
        self.setupUi(self)
        self._figure = None

        self.positionLabel = QtGui.QLabel('teste')
        self.statusBar().addPermanentWidget(self.positionLabel, 10)

    def updateLatLonEdits(self):
        self.latEdit.setText(str(self._figure.get_plot_property('lat_0')))
        self.lonEdit.setText(str(self._figure.get_plot_property('lon_0')))

    def updateMinMaxValueEdits(self):
        self.minEdit.setText(str(self._figure.min_current_values()))
        self.maxEdit.setText(str(self._figure.max_current_values()))

    def updateZoomSlider(self):
        self.zoomSlider.setRange(0, self._figure.max_zoom_level)
        self.zoomSlider.setSliderPosition(self._figure.zoom_level)

    def updateCellValueEdits(self):
        if self._figure.selected_cell:
            depth_t, num_levels = self._figure.selected_value()
            self.cellDepth_TEdit.setText("%.2f" % depth_t)
            self.cellNum_LevelsEdit.setText("%d" % num_levels)

    def updatePositionLabel(self, lat=0, lon=0):
        text_items = []
        if self._figure.pointed_cell:
            text_items.append(("Lat: %.2f | Lon: %.2f | i: %d | j: %d" % (
                lat, lon, self._figure.pointed_cell[0],
                self._figure.pointed_cell[1])))
        if self._figure.selected_cell:
            text_items.append(("selected -> i: %d | j: %d" % (
                self._figure.selected_cell[0],
                self._figure.selected_cell[1])))
        self.positionLabel.setText(' || '.join(text_items))

    @QtCore.pyqtSignature('bool')
    def on_goLatLonButton_clicked(self, checked):
        try:
            new_lat = float(self.latEdit.text())
        except ValueError:
            pass  # TODO: raise error

        try:
            new_lon = float(self.lonEdit.text())
        except ValueError:
            pass  # TODO: raise error

        # TODO: validade inputs
        self._figure.plot_grid(lat_0=new_lat, lon_0=new_lon)
        self.updateLatLonEdits()

    @QtCore.pyqtSignature('bool')
    def on_goMatXYButton_clicked(self):
        try:
            new_x = int(self.xPosEdit.text())
        except ValueError:
            pass  # TODO: raise error

        try:
            new_y = int(self.yPosEdit.text())
        except ValueError:
            pass  # TODO: raise error
        self._figure.change_position(new_x - 1, new_y - 1)

    @QtCore.pyqtSignature('bool')
    def on_valueRangeButton_clicked(self):
        try:
            new_min = float(self.minEdit.text())
        except ValueError:
            pass  # TODO: raise error

        try:
            new_max = float(self.maxEdit.text())
        except ValueError:
            pass  # TODO: raise error
        self._figure.plot_grid(vmin=new_min, vmax=new_max)
        self.updateMinMaxValueEdits()

    @QtCore.pyqtSignature('bool')
    def on_cellChangeValueButton_clicked(self):
        new_depth_t = float(self.cellDepth_TEdit.text())
        new_num_levels = int(self.cellNum_LevelsEdit.text())
        self._figure.change_value(new_depth_t, new_num_levels)
        self.updateCellValueEdits()

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

    @QtCore.pyqtSignature('int')
    def on_resolutionComboBox_activated(self, index):
        resolutions = ('c', 'l', 'i', 'h', 'f')
        self._figure.plot_grid(resolution=resolutions[index])

    def on_zoomSlider_sliderReleased(self):
        self._figure.zoom(self.zoomSlider.value())

    @QtCore.pyqtSignature('bool')
    def on_actionQuit_triggered(self, checked):
        self.close()

    @QtCore.pyqtSignature('bool')
    def on_actionSaveGridChanges_triggered(self, checked):
        # TODO: return error when location is invalid?
        default_path = 'examples/data/grids_tupa/'
        filename = QtGui.QFileDialog.getSaveFileName(
            self,
            'Save file',
            default_path)
        self._figure.save_diff(filename)

    @QtCore.pyqtSignature('bool')
    def on_actionOpenGrid_triggered(self, checked):
        default_path = 'examples/data/grids_tupa/'
        filename = QtGui.QFileDialog.getOpenFileName(
            self,
            'Open file',
            default_path)
        # TODO: open a dialog, showing the error if this doesn't work.
        grid = MOM4Grid(filename)

        self._figure = MplFigure(grid)
        self.mapwidget.set_canvas(self._figure)
        self._figure.plot_grid()
        self.updateLatLonEdits()
        self.updateMinMaxValueEdits()
        self.updateZoomSlider()
        self._figure.set_changed_value_callback(self.updateCellValueEdits)
        self._figure.set_pointed_value_callback(self.updatePositionLabel)

    @QtCore.pyqtSignature('bool')
    def on_actionLoadGridChanges_triggered(self, checked):
        default_path = 'examples/data/grids_tupa/'
        filenames = QtGui.QFileDialog.getOpenFileNames(self,
            'Load grid changes',
            default_path)
        # TODO: open a dialog, showing the error if this doesn't work.
        for filename in filenames:
            self._figure.load_changes(filename)
        self._figure.plot_grid()

    def closeEvent(self, ce):
        self.close()
