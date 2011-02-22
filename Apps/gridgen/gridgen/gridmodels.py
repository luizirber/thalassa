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

    def fix(self):
        x_vert_T = self.data.variables['x_vert_T']
        y_vert_T = self.data.variables['y_vert_T']
        depth_t = self.data.variables['depth_t']
        num_levels = self.data.variables['num_levels']
        zb = self.data.variables['zb']

        _, y, x = x_vert_T.shape

        X = np.zeros((y + 1, x + 1))
        X[:y, :x] = x_vert_T[0, :]
        X[y, :x] = x_vert_T[2, -1, :]
        X[:y, x] = x_vert_T[3, :, -1]
        X[y, x] = x_vert_T[1, -1, -1]

        Y = np.zeros((y + 1, x + 1))
        Y[:y, :x] = y_vert_T[0, :]
        Y[y, :x] = y_vert_T[2, -1, :]
        Y[:y, x] = y_vert_T[3, :, -1]
        Y[y, x] = y_vert_T[1, -1, -1]

        self.X = X
        self.Y = Y
        self.x_vert_T = x_vert_T
        self.y_vert_T = y_vert_T
        self.depth_t = depth_t
        self.num_levels = num_levels
        self.zb = zb

    def compare_differences(self, variable, cmpe):
        diff = (self.data.variables[variable] == cmpe)
        px, py = np.where(diff == False)
        cmpes = []
        for x, y in zip(px, py):
            cmpes.append(cmpe[x][y])
        return zip(map(operator.add, py, [1]*len(py)),
                   map(operator.add, px, [1]*len(px)),
                   cmpes)

    def save_differences(self, filename, diffs):
        f = open(filename, 'w')
        f.writelines([('%d, %d, %.2f\n' % p) for p in diffs])
        f.close()
