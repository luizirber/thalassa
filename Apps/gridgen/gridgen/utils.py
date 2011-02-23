#!/usr/bin/env python


def debug_trace():
    '''Set a tracepoint in the Python debugger that works with Qt'''
    from PyQt4.QtCore import pyqtRemoveInputHook
    from ipdb import set_trace
    pyqtRemoveInputHook()
    set_trace()
