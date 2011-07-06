from cx_Freeze import setup, Executable
 
setup(
    name = "GridGen",
    version = "1.0",
    description = "Ocean model grid editor",
    executables = [Executable("bin/gridgen")]
    )
