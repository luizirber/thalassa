#!/usr/bin/env python

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import numpy.ma as ma
from numpy.lib.scimath import logn
from mpl_toolkits import basemap

import gridgen
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
        self._bmap.ax = self.add_axes((0.05,0.10,0.9,0.9))

        self._parse_pcolor_args(kwargs)
        zs = self._calc_step()
        x, y = self._bmap(self.X[::zs, ::zs], self.Y[::zs, ::zs])
        self.x = ma.masked_values(
            np.where((x < self._bmap.llcrnrx * .85) |
                     (x > self._bmap.urcrnrx * 1.15), 1.e30, x),
            1.e30)
        self.y = ma.masked_values(
            np.where((y < self._bmap.llcrnry * .85) |
                     (y > self._bmap.urcrnry * 1.15), 1.e30, y),
            1.e30)
        self.cells = self._bmap.pcolor(
            self.x, self.y,
            self.current_values[zs / 2::zs, zs / 2::zs],
            **self.pcolor_options)

        if False:#self.selected_cells:
            #TODO: check ranges
            posx, posy = self.selected_cells
            selected = np.zeros((posx[1]-posx[0], posy[1]-posy[0]))
            selected[:] = -5000
            self.cells = self._bmap.pcolor(
                self.x[posx[0]/zs:posx[1]/zs+1, posy[0]/zs:posy[1]/zs+1],
                self.y[posx[0]/zs:posx[1]/zs+1, posy[0]/zs:posy[1]/zs+1],
                selected,
                **self.pcolor_options)

        self._bmap.drawcoastlines(color='w')
        self._bmap.drawcountries(color='w')

        self.connect_signals()

        pos = self._bmap.ax.get_position()
        l, b, w, _ = pos.bounds
        # create axes instance for colorbar on bottom.
        cax = self.add_axes([l, b-0.07, w, 0.04])
        # draw colorbar on bottom.
        self.colorbar(self.cells, cax=cax,orientation='horizontal')

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
        px = (((xarray[2] > x) | (xarray[3] > x)) &
              ((xarray[1] < x) | (xarray[0] < x)))
        py = (((yarray[2] > y) | (yarray[1] > y)) &
              ((yarray[3] < y) | (yarray[0] < y)))
        p = np.where(px & py)
        posx, posy = int(p[0][0]), int(p[1][0])
        zs = self._calc_step()
        xstart = posx - zs/2
        xend = posx + zs/2
        ystart = posy - zs/2
        yend = posy + zs/2
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
            # TODO: check the middle cell, not the first, to follow the
            # shown value at the edits
            if (self.num_levels[px[0], py[0]] == num_levels and
                self.depth_t[px[0], py[0]] == depth_t):
                # TODO: raise error, should change only one. Or just set
                # depth_t and we're done?
                pass
            elif self.num_levels[px[0], py[0]] != num_levels:
                self.num_levels[px[0]:px[1], py[0]:py[1]] = num_levels
                self.depth_t[px[0], py[0]] = self.grid.zb[int(num_levels) - 1]
            else:
                self.change_value_for_pos(px, py, depth_t)
            self.plot_grid()

    def change_value_for_pos(self, px, py, depth_t):
        new_num_levels = np.where(self.grid.zb[:] >= depth_t)[0][0]
        if new_num_levels > 0:
            if px[0] == px[1]:
                self.num_levels[px[0], py[0]] = new_num_levels + 1
            else:
                self.num_levels[px[0]:px[1], py[0]:py[1]] = new_num_levels + 1
        else:
            if px[0] == px[1]:
                self.num_levels[px[0], py[0]] = new_num_levels
            else:
                self.num_levels[px[0]:px[1], py[0]:py[1]] = new_num_levels

        if px[0] == px[1]:
            self.depth_t[px[0], py[0]] = depth_t
        else:
            self.depth_t[px[0]:px[1], py[0]:py[1]] = depth_t

    def save_diff(self, filename):
        diffs = self.grid.compare_differences('depth_t', self.depth_t)
        self.grid.save_differences(filename, diffs)

    def load_changes(self, filename):
        changes = open(filename, 'r')
        for change in changes:
            py, px, value = change.split(',')
            self.change_value_for_pos(int(px)-1, int(py)-1, float(value))

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
