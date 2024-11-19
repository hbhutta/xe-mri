from oct2py import octave 
octave.addpath("matlab")

"""
Resizes nifti files in dir
"""
def resize(dir: str, files: str):
    octave.resize(dir, files)
   