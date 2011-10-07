import os
from os.path import join, abspath

import pytest

from gridgen import Grid
from gridgen.ui import MplUI


def test_mplui(tmpdir, testdata):
    a = MplUI()
