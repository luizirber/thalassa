#!/usr/bin/env python

from mpl_toolkits.basemap import pupynere


class Grid(object):

    def __init__(self, filename, *args, **kwargs):
        self.data = pupynere.netcdf_file(filename, 'r', mmap=False)#args, kwargs)
        self.preprocessing()

    def preprocessing(self):
        pass

    def postprocessing(self):
        self.data.close()


class MOM4Grid(Grid):

    def __init__(self, filename, *args, **kwargs):
        super(MOM4Grid, self).__init__(filename, args, kwargs)

    def fix(self):
        '''
        X[:200,:360] = x_vert_T[0,:]
        X[200,:360] = x_vert_T[1,-1,:]
        X[:200,360] = x_vert_T[3,:,-1]
        X[200,360] = x_vert_T[2,-1,-1]

        Y[:200,:360] = y_vert_T[0,:]
        Y[200,:360] = y_vert_T[1,-1,:]
        Y[:200,360] = y_vert_T[3,:,-1]
        Y[200,360] = y_vert_T[2,-1,-1]

        '''
        pass
