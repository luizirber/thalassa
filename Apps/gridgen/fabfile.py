from fabric.api import local, sudo

def freeze():
    local('cxfreeze --include-modules=sip,distutils --exclude-modules=tcl,Tkinter,Tkconstants bin/gridgen --target-dir=dist/mac/GridGen.app/Contents/MacOS --target-name=gridgen.bin')
    local('cp /usr/local/lib/libpng12.0.dylib dist/mac/GridGen.app/Contents/MacOS/')
    local('sudo cp /usr/local/lib/libgeos-3.3.0.dylib dist/mac/GridGen.app/Contents/MacOS/')
    local('sudo cp /usr/local/Cellar/qt/4.7.3/plugins/imageformats/*.dylib dist/mac/GridGen.app/Contents/MacOS/')
    local('sudo python dist/mac/freeze_fix.py')
    local('chmod +x dist/mac/GridGen.app/Contents/MacOS/gridgen')
    local('chmod +x dist/mac/GridGen.app/Contents/MacOS/gridgen.bin')
    local('mkdir -p dist/mac/GridGen.app/Contents/MacOS/lib/python2.6/config')
    local('cp /usr/lib/python2.6/config/Makefile dist/mac/GridGen.app/Contents/MacOS/lib/python2.6/config/Makefile')
    local('mkdir -p dist/mac/GridGen.app/Contents/MacOS/include/python2.6')
    local('cp /usr/include/python2.6/pyconfig.h dist/mac/GridGen.app/Contents/MacOS/include/python2.6/pyconfig.h')
    local('sudo cp -R /usr/local/lib/QtGui.framework/Resources/qt_menu.nib dist/mac/GridGen.app/Contents/Resources/')
