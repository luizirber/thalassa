#!/usr/bin/env python

import sys

from PyQt4 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg

from gridgen.ui import UI, MplUI


class QtMplUI(QtGui.QMainWindow, UI):

    def __init__(self, figure):
        super(QtMplUI, self).__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("GridGen")  # TODO: change to final name
        self.setMinimumSize(QtCore.QSize(800, 600))
        self._figure = figure

        menuBar = QtGui.QMenuBar()
        self.setMenuBar(menuBar)

        self.file_menu = QtGui.QMenu("&File", self)
        self.file_menu.addAction("&Quit", self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        menuBar.addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu("&Help", self)
        menuBar.addSeparator()
        menuBar.addMenu(self.help_menu)

        self.help_menu.addAction("&About", self.about)

        self.main_widget = QtGui.QWidget(self)

        l = QtGui.QHBoxLayout(self.main_widget)
        mc = FigureCanvasQTAgg(self._figure)
        l.addWidget(mc)
        self._figure.plot_grid()

        vbox = QtGui.QVBoxLayout()
        l.addLayout(vbox)

        button = QtGui.QPushButton('horario')
        button.clicked.connect(self.print_clicked)
        vbox.addWidget(button)

        button = QtGui.QPushButton('anti-horario')
        button.clicked.connect(self.print_clicked)
        vbox.addWidget(button)

        button = QtGui.QPushButton('cima')
        button.clicked.connect(self.print_clicked)
        vbox.addWidget(button)

        button = QtGui.QPushButton('baixo')
        button.clicked.connect(self.print_clicked)
        vbox.addWidget(button)

        button = QtGui.QPushButton('show grid')
        button.clicked.connect(self.print_clicked)
        vbox.addWidget(button)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("GEA-INPE", 2011)

    def print_clicked(self):
        print 'clicou!'

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        pass
