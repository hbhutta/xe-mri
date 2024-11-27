from enum import Enum

class ReorientKey(Enum):
    CT = "CT"
    VENT = "VENT" 

class Direction(Enum):
    X = 0
    Y = 1
    Z = 2
    
class SFORM_CODE(Enum):
    UNKNOWN = 0 
    SCANNER = 1
    
class QFORM_CODE(Enum):
    UNKNOWN = 0
    SCANNER = 1 
