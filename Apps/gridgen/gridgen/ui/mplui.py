#!/usr/bin/env python

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
from mpl_toolkits import basemap

from gridgen.ui import UI
from gridgen import MOM4Grid


class MplFigure(Figure):

    def __init__(self):
        super(MplFigure, self).__init__()
        raw_grid = MOM4Grid('examples/data/lowres.nc') # TODO: fix hardcoded path
        raw_grid.fix()

        self.grid = raw_grid
        self.X = self.grid.X
        self.Y = self.grid.Y
        self.depth_t = self.grid.depth_t

        self.lat_0 = -30
        self.lon_0 = -70
        self.zoom_level = 5

        self._bmap = None


    def plot_grid(self, *args, **kwargs):
#llcrnrlon=None, llcrnrlat=None,
#                     urcrnrlon=None, urcrnrlat=None,
#                     llcrnrx=None, llcrnry=None,
#                     urcrnrx=None, urcrnry=None,
#                     width=None, height=None,
#                     projection='cyl', resolution='c',
#                     area_thresh=None, rsphere=6370997.0,
#                     lat_ts=None,
#                     lat_1=None, lat_2=None,
#                     lat_0=None, lon_0=None,
#                     lon_1=None, lon_2=None,
#                     no_rot=False,
#                     suppress_ticks=True,
#                     satellite_height=35786000,
#                     boundinglat=None,
#                     fix_aspect=True,
#                     anchor='C',
#                     ax=None):

        if not self._bmap:
            self._bmap = basemap.Basemap(projection='ortho', lat_0=self.lat_0,
                lon_0=self.lon_0, resolution='c')
            self._bmap.ax = self.add_axes((0, 0, 1, 1))

        options = kwargs.keys()
        if "lat_0" in options or "lon_0" in options:
            self.clear()
            lat_0_old = self.lat_0
            lon_0_old = self.lon_0

            self.lat_0 = float(kwargs.get('lat_0', self.lat_0))
            if self.lat_0 > 90:
                self.lat_0 = 90
            elif self.lat_0 < -90:
                self.lat_0 = -90

            self.lon_0 = float(kwargs.get('lon_0', self.lon_0))
            if self.lon_0 > 180:
                self.lon_0 -= 360
            elif self.lon_0 < -180:
                self.lon_0 += 360

            self._bmap = basemap.Basemap(projection='ortho',
                lat_0=self.lat_0, lon_0=self.lon_0,
                resolution='c')
            self._bmap.ax = self.add_axes((0, 0, 1, 1))

        zl = self.zoom_level
        x, y = self._bmap(self.X[::zl, ::zl], self.Y[::zl, ::zl])

        self._bmap.pcolor(x, y, self.depth_t[zl/2::zl, zl/2::zl],
            edgecolors=kwargs.get('edgecolors', 'none'))
        self._bmap.drawcoastlines(color='w')

        self.canvas.draw()


class MplUI(FigureCanvas, UI):

    def __init__(self, figure):
        super(MplUI, self).__init__(figure)
        self._fig = figure

    def plot(self):
        self._fig.plot_grid()
