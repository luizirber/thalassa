#!/usr/bin/env python

import operator

import numpy as np
from netCDF4 import Dataset


class Grid(object):

    def __init__(self, filename, *args, **kwargs):
        self.data = Dataset(filename, 'r', format="NETCDF4")
        self.preprocessing()

    def preprocessing(self):
        pass

    def postprocessing(self):
        self.data.close()


class MOM4Grid(Grid):

    def __init__(self, filename, *args, **kwargs):
        super(MOM4Grid, self).__init__(filename, args, kwargs)

    def preprocessing(self):
        super(MOM4Grid, self).preprocessing()
        self.x_vert_T = self.data.variables['x_vert_T']
        self.y_vert_T = self.data.variables['y_vert_T']
        self.X = self._close_north_pole(self.x_vert_T)
        self.Y = self._close_north_pole(self.y_vert_T)
        self.depth_t = self.data.variables['depth_t'][:]
        self.num_levels = self.data.variables['num_levels'][:]
        self.zb = self.data.variables['zb'][:]
        self.join_lat = self.data.join_lat

    def compare_differences(self, variable, cmpe):
        diff = (self.data.variables[variable] == cmpe)
        px, py = np.where(diff == False)
        cmpes = []
        for x, y in zip(px, py):
            cmpes.append(cmpe[x][y])
        return zip(map(operator.add, py, [1] * len(py)),
                   map(operator.add, px, [1] * len(px)),
                   cmpes)

    def save_differences(self, filename, diffs):
        f = open(filename, 'w')
        f.writelines([('%d, %d, %.2f\n' % p) for p in diffs])
        f.close()

    def load_differences(self, filename):
        changes = open(filename, 'r')
        for py, px, value in (change.split(',') for change in changes):
            self.change_value_for_pos(int(px) - 1, int(py) - 1, float(value))
        changes.close()

    def calc_pos(self, xarray, yarray, x, y):
        posx = posy = 0
        if y <= self.join_lat:
            # Still using this method because it's much quicker
            px = (((xarray[2] > x) | (xarray[3] > x)) &
                  ((xarray[1] < x) | (xarray[0] < x)))
            py = (((yarray[2] > y) | (yarray[1] > y)) &
                  ((yarray[3] < y) | (yarray[0] < y)))
            cond = px & py
        else:
            cond = self._inside_poly(
                self.x_vert_T,
                self.y_vert_T,
                (x, y))
        p = np.where(cond)
        posx, posy = int(p[0][0]), int(p[1][0])
        return posx, posy

    def change_value(self, px, py, depth_t, num_levels):
        sx, sy = self._build_slices(px, py)
        # TODO: check the middle cell, not the first, to follow the
        # shown value at the edits
        if (self.num_levels[px[0], py[0]] == num_levels and
            self.depth_t[px[0], py[0]] == depth_t):
            # TODO: raise error, should change only one. Just setting
            # depth_t and we're done for now.
            self.change_value_for_pos(px, py, depth_t)
        elif self.num_levels[px[0], py[0]] != num_levels:
            self.num_levels[sx, sy] = num_levels
            if num_levels <= 0:
                self.depth_t[sx, sy] = self.zb[0]
            else:
                self.depth_t[sx, sy] = self.zb[int(num_levels) - 1]
        else:
            self.change_value_for_pos(px, py, depth_t)

    def change_value_for_pos(self, px, py, depth_t):
        sx, sy = self._build_slices(px, py)
        new_num_levels = np.where(self.zb >= depth_t)[0][0]
        if new_num_levels > 0:
            self.num_levels[sx, sy] = new_num_levels + 1
        else:
            self.num_levels[sx, sy] = new_num_levels
        self.depth_t[sx, sy] = depth_t

    def _build_slices(self, px, py):
        try:
            px[0]
        except TypeError:
            sx = px
            sy = py
        else:
            if px[0] == px[1]:
                sx = px[0]
                sy = py[0]
            else:
                sx = slice(px[0], px[1])
                sy = slice(py[0], py[1])
        return sx, sy

    def _close_north_pole(self, array):
        _, y, x = array.shape
        R = np.zeros((y + 1, x + 1))
        R[:y, :x] = array[0, :]
        R[y, :x] = array[2, -1, :]
        R[:y, x] = array[3, :, -1]
        R[y, x] = array[1, -1, -1]
        return R

    def _inside_poly(self, poly_x, poly_y, p):
        p1x = poly_x[:] - p[0]
        p1y = poly_y[:] - p[1]
        p2x = np.roll(poly_x, 1, axis=0) - p[0]
        p2y = np.roll(poly_y, 1, axis=0) - p[1]
        theta1 = np.arctan2(p1y, p1x)
        theta2 = np.arctan2(p2y, p2x)
        dtheta = (theta2 - theta1 + np.math.pi) % (2 * np.math.pi) - np.math.pi
        dtheta = sum(dtheta, 0)
        return abs(dtheta) >= np.math.pi
