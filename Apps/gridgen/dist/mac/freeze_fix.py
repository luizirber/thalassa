import os
import subprocess

#Change the absolute paths in all library files to relative paths
distDir = 'dist/mac/GridGen.app/Contents/MacOS'
shippedfiles=os.listdir(distDir)

for file in shippedfiles:
    #Do the processing for any found file or dir, the tools will just
    #fail for files for which it does not apply
    filepath=os.path.join(distDir,file)

    #Let the library itself know its place    
    subprocess.call(('install_name_tool','-id','@executable_path/'+file,filepath))

    #Find the references
    otool=subprocess.Popen(('otool','-L', filepath),stdout=subprocess.PIPE)
    libs=otool.stdout.readlines()

    for lib in libs:
        #For each referenced library, chech if it is in the set of
        #files that we ship. If so, change the reference to a path
        #relative to the executable path
        lib=lib.decode()
        filename,_,_=lib.strip().partition(' ')
        prefix,name=os.path.split(filename)
        if name in shippedfiles:
            newfilename='@executable_path/'+name
            print ('%s => %s' % (name,newfilename))
            subprocess.call(('install_name_tool','-change',filename,newfilename,filepath))
