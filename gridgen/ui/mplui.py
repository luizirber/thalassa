#!/usr/bin/env python

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import numpy.ma as ma
from numpy.lib.scimath import logn
from mpl_toolkits import basemap

from thalassa.ui import UI


class MplFigure(Figure):

    def __init__(self, data):
        super(MplFigure, self).__init__()

        self.grid = data
        self.X = self.grid.X
        self.Y = self.grid.Y
        self.depth_t = self.grid.depth_t
        self.num_levels = self.grid.num_levels
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

        self.zoom_step = 1.9
        self.zoom_level = self._calc_zoom_level()
        self.max_zoom_level = self._max_zoom_level()
        self.selected_cell = None
        self.selected_cells = None
        self.pointed_cell = None
        self.pointed_cells = None
        self.changed_value_cb = None
        self.pointed_value_cb = None

        self._bmap = None
        self.cidpress = None
        self.cidrelease = None
        self.cidmotion = None

    def rotate(self, lat_delta=0, lon_delta=0):
        new_lat = self.options['lat_0'] + lat_delta
        new_lon = self.options['lon_0'] + lon_delta
        self.plot_grid(lat_0=new_lat, lon_0=new_lon)

    def zoom(self, level):
        p = self._from_zoom_level(level)
        self.plot_grid(llcrnrx=-p, llcrnry=-p, urcrnrx=p, urcrnry=p)

    def zoom_in(self):
        if self.zoom_level + 1 <= np.floor(self.max_zoom_level):
            p = self._from_zoom_level(self.zoom_level + 1)
            self.plot_grid(llcrnrx=-p, llcrnry=-p, urcrnrx=p, urcrnry=p)

    def zoom_out(self):
        if self.zoom_level > 0:
            p = self._from_zoom_level(self.zoom_level - 1)
            self.plot_grid(llcrnrx=-p, llcrnry=-p, urcrnrx=p, urcrnry=p)

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

    def disconnect_signals(self):
        self.canvas.mpl_disconnect(self.cidpress)
        self.cidpress = None
        self.canvas.mpl_disconnect(self.cidrelease)
        self.cidrelease = None
        self.canvas.mpl_disconnect(self.cidmotion)
        self.cidmotion = None

    def connect_signals(self):
        self.cidpress = self.canvas.mpl_connect('button_press_event',
            self.on_press)
        self.cidrelease = self.canvas.mpl_connect('button_release_event',
            self.on_release)
#        self.cidmotion = self.canvas.mpl_connect('motion_notify_event',
#            self.on_motion)

    def plot_grid(self, *args, **kwargs):
        self._parse_plot_args(kwargs)
        self.clear()
        self.disconnect_signals()
        self._calc_zoom_level()
        self._bmap = basemap.Basemap(**self.options)
        self._bmap.ax = self.add_axes((0.05, 0.10, 0.9, 0.9))
        self._bmap.ax.set_axis_bgcolor('black')

        self._parse_pcolor_args(kwargs)
        zs = self._calc_step()
        x, y = self._bmap(self.X[::zs, ::zs], self.Y[::zs, ::zs])
        self.x = self._mask_array(x)
        self.y = self._mask_array(y)
        self.cells = self._bmap.pcolor(
            self.x, self.y,
            self.current_values[zs / 2::zs, zs / 2::zs],
            **self.pcolor_options)

        if False:  # self.selected_cells:
            #TODO: check ranges
            posx, posy = self.selected_cells
            selected = np.zeros((posx[1] - posx[0], posy[1] - posy[0]))
            selected[:] = -5000
            self.cells = self._bmap.pcolor(
                self.x[posx[0] / zs:posx[1] / zs + 1,
                       posy[0] / zs:posy[1] / zs + 1],
                self.y[posx[0] / zs:posx[1] / zs + 1,
                       posy[0] / zs:posy[1] / zs + 1],
                selected,
                **self.pcolor_options)

        self._bmap.drawcoastlines(color='w')
        self._bmap.drawcountries(color='w')

        self.connect_signals()

        pos = self._bmap.ax.get_position()
        l, b, w, _ = pos.bounds
        # create axes instance for colorbar on bottom.
        cax = self.add_axes([l, b - 0.07, w, 0.04])
        # draw colorbar on bottom.
        self.colorbar(self.cells, cax=cax, orientation='horizontal')

        self.canvas.draw()

    def on_press(self, event):
        self.event = event

    def on_release(self, event):
        if self.event.x == event.x and self.event.y == event.y:
            x, y = self._bmap(event.xdata, event.ydata, inverse=True)
            posx, posy = self._calc_pos(
                self.grid.x_vert_T,
                self.grid.y_vert_T,
                x, y)
            self.selected_cells = (posx, posy)
            self.selected_cell = (posx[0], posy[0])
            self.selected_cell_changed()
            self.pointed_cells = (posx, posy)
            self.pointed_cell = (posx[0], posy[0])
            self.pointed_cell_changed(x, y)
#            self.plot_grid()
        else:  # multiple selection
            '''lx, ly = self.event.xdata, self.event.ydata
            cx, cy = event.xdata, event.ydata
            if cx < lx :
                cx, lx = lx, cx
            if cy > ly:
                cy, ly = ly, cy
            cx, cy = self._bmap(cx, cy, inverse=True)
            lx, ly = self._bmap(lx, ly, inverse=True)

            ptx, pty, pbx, pby = self._calc_region(
                self.grid.x_vert_T,
                self.grid.y_vert_T,
                cx, cy, lx, ly)

            #ptx, pty = self._calc_pos(
            #    self.grid.x_vert_T,
            #    self.grid.y_vert_T,
            #    cx, cy)
            #pbx, pby = self._calc_pos(
            #    self.grid.x_vert_T,
            #    self.grid.y_vert_T,
            #    lx, ly)

            # TODO: corner cases. What if I select over one of the limits
            # (north pole or vertical)?

            print 'initial', (ptx, pty), 'final', (pbx, pby)'''
            pass
        self.event = None

    def on_motion(self, event):
        x, y = self._bmap(event.xdata, event.ydata, inverse=True)
        posx, posy = self._calc_pos(
            self.grid.x_vert_T,
            self.grid.y_vert_T,
            x, y)
        self.pointed_cell = (posx[0], posy[0])
        self.pointed_cell_changed(x, y)

    def _calc_pos(self, xarray, yarray, x, y):
        posx, posy = self.grid.calc_pos(xarray, yarray, x, y)
        zs = self._calc_step()
        xstart = posx - zs / 2
        xend = posx + zs / 2
        ystart = posy - zs / 2
        yend = posy + zs / 2
        return (xstart, xend), (ystart, yend)

    def _calc_region(self, xarray, yarray, tx, ty, bx, by):
        px = (((xarray[2] > tx) | (xarray[3] > tx)) &
              ((xarray[1] < bx) | (xarray[0] < bx)))
        py = (((yarray[2] > ty) | (yarray[1] > ty)) &
              ((yarray[3] < by) | (yarray[0] < by)))
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
        return (self.depth_t[self.selected_cell[0], self.selected_cell[1]],
                self.num_levels[self.selected_cell[0], self.selected_cell[1]])

    def set_pointed_value_callback(self, func, args=None):
        self.pointed_value_cb = (func, args)

    def pointed_cell_changed(self, lat, lon):
        if self.pointed_value_cb:
            func, args = self.pointed_value_cb
            if args:
                func(lat, lon, args)
            else:
                func(lat, lon)

    def change_position(self, x, y):
        lon = self.X[x, y]
        lat = self.Y[x, y]
        self.plot_grid(lat_0=lat, lon_0=lon)
        self.selected_cell = (x, y)
        self.selected_cell_changed()

    def change_value(self, depth_t, num_levels):
        if self.selected_cells:
            px, py = self.selected_cells
            self.grid.change_value(px, py, depth_t, num_levels)
            self.plot_grid()

    def save_diff(self, filename):
        diffs = self.grid.compare_differences('depth_t', self.depth_t)
        self.grid.save_differences(filename, diffs)

    def load_changes(self, filename):
        self.grid.load_differences(filename)

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

    def _mask_array(self, array):
        return ma.masked_values(
            np.where((array < self._bmap.llcrnrx * .85) |
                     (array > self._bmap.urcrnrx * 1.15), 1.e30, array),
            1.e30)

    def _from_zoom_level(self, level):
        if level > 0 and level <= self.max_zoom_level:
            p = (self.options['rsphere'] / self.zoom_step ** (level - 1)) / 2
            self.zoom_level = level
        elif level > self.max_zoom_level:
            p = (self.options['rsphere'] / self.zoom_step ** (level - 1)) / 2
            self.zoom_level = self.max_zoom_level
        else:
            p = self.options['rsphere']
            self.zoom_level = 0
        return p

    def _max_zoom_level(self):
        self.max_zoom_level = logn(self.zoom_step,
             max(self.current_values.shape)) - 6

    def _calc_step(self):
        self._calc_zoom_level()
        self._max_zoom_level()
        items = max(self.current_values.shape)
        zs = int(items / (self.zoom_step ** (self.zoom_level + 6)))
        if zs < 1:
            zs = 1
        return zs

    def _parse_plot_args(self, opts):
        changed = False
        float_options = ('llcrnrx', 'llcrnry', 'urcrnrx', 'urcrnry',
            'llcrnrlon', 'llcrnrlat', 'urcrnrlon', 'urcrnrlat',
            'width', 'height')
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
        for opt in float_options:
            if opt in opts:
                self.options[opt] = float(opts[opt])
                del opts[opt]
                changed = True
        if 'resolution' in opts:
            resolutions = ('c', 'l', 'i', 'h', 'f')
            if opts['resolution'] in resolutions:
                self.options['resolution'] = str(opts['resolution'])
                del opts['resolution']
                changed = True
        return changed

    def _parse_pcolor_args(self, opts):
        changed = False
        if 'edgecolors' in opts:
            if opts['edgecolors'] != self.pcolor_options['edgecolors']:
                self.pcolor_options['edgecolors'] = str(opts['edgecolors'])
                del opts['edgecolors']
                changed = True
        for opt in ('vmax', 'vmin'):
            if opt in opts:
                if opts[opt] != self.pcolor_options[opt]:
                    self.pcolor_options[opt] = float(opts[opt])
                    del opts[opt]
                    changed = True
        return changed


class MplUI(FigureCanvas, UI):

    def __init__(self, figure):
        super(MplUI, self).__init__(figure)
        self._fig = figure

    def plot(self):
        self._fig.plot_grid()
