from fabric.api import local, sudo

def freeze():
    local('cxfreeze --include-modules=sip,distutils bin/gridgen --target-dir=dist/mac/GridGen.app/Contents/')
    local('sudo python dist/mac/freeze_fix.py')
    local('chmod +x dist/gridgen')
    local('tar czvf gridgen.tar.gz dist/')
    local('scp -P 2222 gridgen.tar.gz localhost:')

