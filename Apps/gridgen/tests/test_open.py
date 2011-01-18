import os
from os.path import join, abspath

import pytest

from gridgen import Grid
from gridgen.ui import MplUI, QtMplUI


def test_open_grid(tmpdir, testdata):
    a = Grid(join(testdata, 'lowres.nc'))
    print a
    #base = os.path.join(tmpdir.basename, tmpdir.dirname)
    #path = join(base, 'calib')
    #assert make_cruise_dir(base, 'calib') == path
    assert 0 == 0
