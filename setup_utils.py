#!/usr/bin/env python

import os
from os.path import isdir, exists, join, splitext, split, dirname


def compile_ui(ui_file, py_dir=None):
    if py_dir is None:
        py_dir = ''
    py_file = join(py_dir, splitext(split(ui_file)[-1])[0] + ".py")
    try:
        from PyQt4 import uic
        fp = open(py_file, 'w')
        uic.compileUi(ui_file, fp)
        fp.close()
        print "compiled", ui_file, "into", py_file
    except Exception, e:
        print 'Unable to compile user interface', e
        return

def compile_rc(qrc_file, py_dir=None):
    if py_dir is None:
        py_dir = ''
    py_file = join(py_dir, splitext(split(qrc_file)[-1])[0] + "_rc.py")
    if os.system('pyrcc4 "%s" -o "%s"' % (qrc_file, py_file)) > 0:
        print "Unable to generate python module for resource file", qrc_file
    else:
        print "compiled", qrc_file, "into", py_file

def build_qt_ui(src='data', dest=''):
    print src, dest
    for dirpath, _, filenames in os.walk(src):
        for filename in filenames:
            if filename.endswith('.ui'):
                compile_ui(join(dirpath, filename),
                    os.path.join(dest, 'thalassa', 'ui', 'qtmplui'))
            elif filename.endswith('.qrc'):
                compile_rc(join(dirpath, filename),
                    os.path.join(dest, 'thalassa', 'ui', 'qtmplui'))
