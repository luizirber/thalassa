#!/usr/bin/env python

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import numpy.ma as ma
from numpy.lib.scimath import logn
from mpl_toolkits import basemap

from gridgen.ui import UI


class MplFigure(Figure):

    def __init__(self, data):
        super(MplFigure, self).__init__()

        self.grid = data
        self.X = self.grid.X
        self.Y = self.grid.Y
        self.depth_t = self.grid.depth_t[:, :]
        self.num_levels = self.grid.num_levels[:, :]
        self.current_values = self.depth_t

        self.options = {
            'llcrnrlon': None,
            'llcrnrlat': None,
            'urcrnrlon': None,
            'urcrnrlat': None,
            'rsphere': 6370997.0,
            'llcrnrx': -6370997.,
            'llcrnry': -6370997.,
            'urcrnrx': 6370997.,
            'urcrnry': 6370997.,
            'width': None,
            'height': None,
            'projection': 'ortho',
            'resolution': 'c',  # c, l, i, h, f
            'area_thresh': None,
            'lat_ts': None,
            'lat_1': None,
            'lat_2': None,
            'lat_0': 30,
            'lon_0': -70,
            'lon_1': None,
            'lon_2': None,
            'no_rot': False,
            'suppress_ticks': True,
            'satellite_height': 35786000,
            'boundinglat': None,
            'fix_aspect': True,
            'anchor': 'C'
        }

        self.pcolor_options = {
          'cmap': None,
          'norm': None,
          'edgecolors': 'none',
          'vmin': np.min(self.current_values),
          'vmax': np.max(self.current_values),
        }

        self.zoom_step = 2
        self.zoom_level = self._calc_zoom_level()
        self.max_zoom_level = self._max_zoom_level()
        self.selected_cell = None
        self.changed_value_cb = None

        self._bmap = None
        self.cidpress = None
        self.cidrelease = None

    def rotate(self, lat_delta=0, lon_delta=0):
        new_lat = self.options['lat_0'] + lat_delta
        new_lon = self.options['lon_0'] + lon_delta
        self.plot_grid(lat_0=new_lat, lon_0=new_lon)

    def zoom(self, level):
        p = self._from_zoom_level(level)
        self.plot_grid(llcrnrx=-p, llcrnry=-p, urcrnrx=p, urcrnry=p)

    def zoom_in(self):
        if self.zoom_level + 1 <= np.floor(self.max_zoom_level):
            lx = self.options['llcrnrx'] / self.zoom_step
            ly = self.options['llcrnry'] / self.zoom_step
            ux = self.options['urcrnrx'] / self.zoom_step
            uy = self.options['urcrnry'] / self.zoom_step
            self.plot_grid(llcrnrx=lx, llcrnry=ly, urcrnrx=ux, urcrnry=uy)

    def zoom_out(self):
        lx = self.options['llcrnrx'] * self.zoom_step
        ly = self.options['llcrnry'] * self.zoom_step
        ux = self.options['urcrnrx'] * self.zoom_step
        uy = self.options['urcrnry'] * self.zoom_step
        self.plot_grid(llcrnrx=lx, llcrnry=ly, urcrnrx=ux, urcrnry=uy)

    def plot_depth_t(self):
        self.current_values = self.depth_t
        self.pcolor_options['vmin'] = np.min(self.current_values)
        self.pcolor_options['vmax'] = np.max(self.current_values)
        self.plot_grid()

    def plot_num_levels(self):
        self.current_values = self.num_levels
        self.pcolor_options['vmin'] = np.min(self.current_values)
        self.pcolor_options['vmax'] = np.max(self.current_values)
        self.plot_grid()

    def plot_grid(self, *args, **kwargs):
        self._parse_plot_args(kwargs)
        self.clear()
        self.canvas.mpl_disconnect(self.cidpress)
        self.cidpress = None
        self.canvas.mpl_disconnect(self.cidrelease)
        self.cidrelease = None
        self._calc_zoom_level()
        self._bmap = basemap.Basemap(**self.options)
        self._bmap.ax = self.add_axes((0, 0, 1, 1))

        self._parse_pcolor_args(kwargs)
        zs = self._calc_step() or 1
        x, y = self._bmap(self.X[::zs, ::zs], self.Y[::zs, ::zs])
        self.x = ma.masked_values(
            np.where((x < self._bmap.llcrnrx * .9) |
                     (x > self._bmap.urcrnrx * 1.1), 1.e30, x),
            1.e30)
        self.y = ma.masked_values(
            np.where((y < self._bmap.llcrnry * .9) |
                     (y > self._bmap.urcrnry * 1.1), 1.e30, y),
            1.e30)
        self.cells = self._bmap.pcolor(
            self.x, self.y,
            self.current_values[zs / 2::zs, zs / 2::zs],
            **self.pcolor_options)

        self._bmap.drawcoastlines(color='w')
        self._bmap.drawcountries(color='w')

        if zs == 1:
            self.cidpress = self.canvas.mpl_connect('button_press_event',
                self.on_press)
            self.cidrelease = self.canvas.mpl_connect('button_release_event',
                self.on_release)

        self.canvas.draw()

    def on_press(self, event):
        self.event = event

    def on_release(self, event):
        if self.event.x == event.x and self.event.y == event.y:
            x, y = self._bmap(event.xdata, event.ydata, inverse=True)
            posx, posy = self._calc_pos(self.X, self.Y, x, y)
            self.selected_cell = (posx, posy)
            self.selected_cell_changed()
#            self.depth_t[posx, posy] = -5000
#            self.plot_grid()
        self.event = None

    def _calc_pos(self, xarray, yarray, xvalue, yvalue):
        e = 1  # TODO: declare conditions for where, avoid hardcode
        px = abs(xarray - xvalue) < e
        py = abs(yarray - yvalue) < e
        p = np.where(px & py)
        return int(p[0][0]), int(p[1][0])

    def set_changed_value_callback(self, func, args=None):
        self.changed_value_cb = (func, args)

    def selected_cell_changed(self):
        if self.changed_value_cb:
            func, args = self.changed_value_cb
            if args:
                func(args)
            else:
                func()

    def selected_value(self):
        return self.current_values[self.selected_cell[0], self.selected_cell[1]]

    def change_position(self, x, y):
        pass

    def change_value(self, new_value):
        if self.selected_cell:
            px, py = self.selected_cell
            self.current_values[px, py] = new_value
            self.plot_grid()

    def save_diff(self, filename):
        if self.current_values is self.depth_t:
            variable = 'depth_t'
        else:
            variable = 'num_levels'
        diffs = self.grid.compare_differences(variable, self.current_values)
        self.grid.save_differences(filename, diffs)

    def get_plot_property(self, key):
        return self.options.get(key, None)

    def min_current_values(self):
        return self.pcolor_options['vmin']

    def max_current_values(self):
        return self.pcolor_options['vmax']

    def _calc_zoom_level(self):
        d = self.options
        self.zoom_level = 1 + int(
            logn(self.zoom_step,
                 d['rsphere'] / (abs(d['llcrnrx']) + abs(d['urcrnrx']))))
#        if self.zoom_level < 3:
#            self.options['resolution'] = 'c'
#        elif self.zoom_level < 5:
#            self.options['resolution'] = 'l'
#        elif self.zoom_level < 7:
#            self.options['resolution'] = 'i'

    def _from_zoom_level(self, level):
        #TODO: verify if level is valid
        p = (self.options['rsphere'] / self.zoom_step ** (level - 1)) / 2
        self.zoom_level = level
        return p

    def _max_zoom_level(self):
        self.max_zoom_level = logn(self.zoom_step,
             max(self.current_values.shape)) - 6

    def _calc_step(self):
        self._calc_zoom_level()
        self._max_zoom_level()
        items = max(self.current_values.shape)
        return items / (self.zoom_step ** (self.zoom_level + 6))

    def _parse_plot_args(self, opts):
        changed = False
        if "lat_0" in opts:
            lat_0 = float(opts['lat_0'])
            if lat_0 > 90:
                lat_0 = 90
            elif lat_0 < -90:
                lat_0 = -90
            if lat_0 != self.options['lat_0']:
                self.options['lat_0'] = lat_0
                changed = True
            del opts['lat_0']
        if "lon_0" in opts:
            lon_0 = float(opts['lon_0'])
            if lon_0 > 180:
                lon_0 = -(360 % lon_0)
            elif lon_0 < -180:
                lon_0 = lon_0 % 360
            if lon_0 != self.options['lon_0']:
                self.options['lon_0'] = lon_0
                changed = True
            del opts['lon_0']
#        if 'width' in opts:
#            #TODO: validate
#            self.options['width'] = opts['width']
#            del opts['width']
#            changed = True
#        if 'height' in opts:
#            #TODO: validate
#            self.options['height'] = opts['height']
#            del opts['height']
#            changed = True
#        if 'llcrnrlon' in opts:
#            self.options['llcrnrlon'] = float(opts['llcrnrlon'])
#            del opts['llcrnrlon']
#            changed = True
#        if 'llcrnrlat' in opts:
#            self.options['llcrnrlat'] = float(opts['llcrnrlat'])
#            del opts['llcrnrlat']
#            changed = True
#        if 'urcrnrlon' in opts:
#            self.options['urcrnrlon'] = float(opts['urcrnrlon'])
#            del opts['urcrnrlon']
#            changed = True
#        if 'urcrnrlat' in opts:
#            self.options['urcrnrlat'] = float(opts['urcrnrlat'])
#            del opts['urcrnrlat']
#            changed = True
        if 'llcrnrx' in opts:
            self.options['llcrnrx'] = float(opts['llcrnrx'])
            del opts['llcrnrx']
            changed = True
        if 'llcrnry' in opts:
            self.options['llcrnry'] = float(opts['llcrnry'])
            del opts['llcrnry']
            changed = True
        if 'urcrnrx' in opts:
            self.options['urcrnrx'] = float(opts['urcrnrx'])
            del opts['urcrnrx']
            changed = True
        if 'urcrnry' in opts:
            self.options['urcrnry'] = float(opts['urcrnry'])
            del opts['urcrnry']
            changed = True
        return changed

    def _parse_pcolor_args(self, opts):
        changed = False
        if 'edgecolors' in opts:
            if opts['edgecolors'] != self.pcolor_options['edgecolors']:
                self.pcolor_options['edgecolors'] = opts['edgecolors']
                del opts['edgecolors']
                changed = True
        if 'vmin' in opts:
            if opts['vmin'] != self.pcolor_options['vmin']:
                self.pcolor_options['vmin'] = float(opts['vmin'])
                del opts['vmin']
                changed = True
        if 'vmax' in opts:
            if opts['vmax'] != self.pcolor_options['vmax']:
                self.pcolor_options['vmax'] = float(opts['vmax'])
                del opts['vmax']
                changed = True
#        return changed or not self._bmap # TODO: is it needed to test this?
        return True

class MplUI(FigureCanvas, UI):

    def __init__(self, figure):
        super(MplUI, self).__init__(figure)
        self._fig = figure

    def plot(self):
        self._fig.plot_grid()
