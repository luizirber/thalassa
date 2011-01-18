#!/usr/bin/env python

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from mpl_toolkits import basemap

from gridgen.ui import UI
from gridgen import MOM4Grid


class MplFigure(Figure):

#    def __init__(self, *args, **kwargs):
    def __init__(self):
        super(MplFigure, self).__init__()

    def plot_grid(self):
        raw_grid = MOM4Grid('examples/data/lowres.nc', mmap=False)

        x_vert_T = raw_grid.data.variables['x_vert_T']
        y_vert_T = raw_grid.data.variables['y_vert_T']
        depth_t = raw_grid.data.variables['depth_t']

        z, y, x = x_vert_T.shape

        X = np.zeros((y+1, x+1))
        X[:y,:x] = x_vert_T[0,:]
        X[y,:x] = x_vert_T[2,-1,:]
        X[:y,x] = x_vert_T[3,:,-1]
        X[y,x] = x_vert_T[1,-1,-1]

        Y = np.zeros((y+1, x+1))
        Y[:y,:x] = y_vert_T[0,:]
        Y[y,:x] = y_vert_T[2,-1,:]
        Y[:y,x] = y_vert_T[3,:,-1]
        Y[y,x] = y_vert_T[1,-1,-1]

        bmap = basemap.Basemap(projection='ortho', lat_0=90, lon_0=120, resolution='l')

        bmap.ax = self.add_axes((0, 0, 1, 1))

        x, y = bmap(X, Y)

        bmap.pcolor(x, y, depth_t, edgecolors='k')
        bmap.drawcoastlines(color='w')

        plt.show()


class MplUI(FigureCanvas, UI):

    def __init__(self, figure):
        super(MplUI, self).__init__(figure)
        self._fig = figure

    def plot(self):
        self._fig.plot_grid()
