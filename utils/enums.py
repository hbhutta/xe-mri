from enum import Enum

# class ReorientKey(Enum):
#     CT = "CT"
#     VENT = "VENT" 

# class Direction(Enum):
#     X = 0
#     Y = 1
#     Z = 2
  
  
# https://nipy.org/nibabel/nifti_images.html#the-sform-affine  
class SFORM_CODE(Enum):
    UNKNOWN = 0 
    SCANNER = 1
    ALIGNED = 2
    TALAIRACH = 3
    MNI = 4
    
#class QFORM_CODE(Enum):
#    UNKNOWN = 0
#    SCANNER = 1 
#