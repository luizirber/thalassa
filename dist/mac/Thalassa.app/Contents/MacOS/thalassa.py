#!/usr/bin/python

# Do some stiff with sys.path

# Set CWD
import os
print 'CWD:', os.getcwd()

import sys
print 'ARGV:', sys.argv
print 'PATH:', sys.path
print 'ENV:', os.environ

if len(sys.argv) > 1 and sys.argv[1][:4] == '-psn':
    del sys.argv[1]

macos_dir = os.path.dirname(sys.argv[0])
bundle_dir = os.path.dirname(macos_dir)
execfile(bundle_dir + '/bin/thalassa', globals(), globals())

