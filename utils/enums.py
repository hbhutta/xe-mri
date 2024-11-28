from enum import Enum
# https://nipy.org/nibabel/nifti_images.html#the-sform-affine  
class CODE(Enum):
    UNKNOWN = "unknown" # 0 
    SCANNER = "scanner" # 1
    ALIGNED = "aligned" # 2
    TALAIRACH = "talairach" # 3
    MNI = "mni" # 4
    

# class ReorientKey(Enum):
#     CT = "CT"
#     VENT = "VENT" 

# class Direction(Enum):
#     X = 0
#     Y = 1
#     Z = 2
  