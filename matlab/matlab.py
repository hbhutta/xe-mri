from oct2py import octave 
octave.addpath("matlab")

"""
Resizes nifti files in dir
"""
def resize(dir: str, files: str) -> None:
    octave.resize(dir, files)
    
def calculate_rbc_m_ratio(calibration_filename: str, calibration_filepath: str) -> None:
   octave.calculate_rbc(calibration_filename, calibration_filepath)