from typing import Self

import nibabel as nib
from nibabel.orientations import aff2axcodes
from nibabel.nifti1 import Nifti1Image, Nifti1Header

import numpy as np

from utils.enums import Direction

class Image():
    """
    Setting the sform/qform affine of the image
    will automatically change the corresponding 
    sform/qform code. 
    
    This means the sform/qform code cannot be manually set.
    
    Reading the sform/qform code after changing the 
    sform/qform affine can be used to confirm
    that a change worked.
    
    Ensure that origin is known before flipping,
    as having an origin other than (0,0,0) can 
    cause unexpected behaviour.
    
    The origin is found in the qform matrix 
    because it based on the qoffset values.
    
    The algorithm is defined in the get_best_affine() method. It is:
    1. If sform_code != 0 (unknown) use the sform affine; else
    2. If qform_code != 0 (unknown) use the qform affine; else
    3. Use the fall-back affine.
 
    References: 
    1. https://stackoverflow.com/questions/47996388/python-boolean-methods-naming-convention
    2. https://nipy.org/nibabel/nibabel_images.html#loading-and-saving
    """
    def __init__(self, filename: str):
        self.__img = nib.load(filename=filename)
        self.__filename = filename
        self.check_best_affine()
    
    def check_best_affine(self) -> bool:
        hdr = self.get_header()
        if (hdr.get_best_affine() == self.get_sform()):
            print("Using sform affine")
        elif (hdr.get_best_affine() == self.get_qform()):
            print("Using qform affine")
        
    def get_filename(self) -> str:
        return self.__filename 

    def get_sform_code(self) -> None:
        return self.__img.header['sform_code']

    def get_qform_code(self) -> None:
        return self.__img.header['qform_code']
        
    def get_qform(self) -> np.array:
        return np.array(self.__img.header.get_qform())
    
    def set_qform(self, qform: np.ndarray):
        self.__img.header.set_qform(qform)
        print(f"{self.get_filename()} has new qform_code: {self.get_qform_code()}")
 
    def get_sform(self) -> np.array:
        return np.array(self.__img.header.get_sform())
       
    def set_sform(self, sform: np.ndarray):
        self.__img.header.set_sform(sform)
        print(f"{self.get_filename()} has new sform_code: {self.get_sform_code()}")
        
    def get_origin(self) -> np.array:
        return self.get_qform()[:,3][:-1]

    def is_matched_by_sform(self, other: Self) -> bool:
        return np.all(self.get_sform() == other.get_sform())
    
    def is_matched_by_qform(self, other: Self) -> bool:
        return np.all(self.get_qform() == other.get_sform())
    
    def is_matched_by_origin(self, other: Self) -> bool:
        return np.all(self.get_origin() == other.get_origin())
        
    def get_fdata(self) -> np.memmap | np.ndarray:
        return self.__img.get_fdata()

    def get_affine(self) -> np.ndarray:
        return self.__img.affine
    
    def get_header(self) -> Nifti1Header:
        return self.__img.header

    def set_header(self, hdr: Nifti1Header) -> None:
        self.__img = Nifti1Image(dataobj=self.get_fdata(), affine=self.get_affine(), header=hdr)

    def flip(self, direction: Direction):
        self.__img.affine[:, [direction.value]] *= -1

    def axcodes(self) -> tuple:
        return aff2axcodes(aff=self.__img.affine, labels=(('R', 'L'), ('A', 'P'), ('S', 'I')))

    def save(self, filename: str) -> None:
        self.__img.to_filename(filename=filename)

    # def align(self, other: Self): # causes image size to be quadrupled for some reason
    #     self.__img = Nifti1Image(self.get_fdata(), other.get_affine())
        

#    def align(self, reference: Self):
#        '''
#        Make sure that sform_code and qform_code match
#
#
#        If reference uses the sform affine,
#        self should also use the sform affine,
#        otherwise self should use the qform affine
#
#        Reference: https://nipy.org/nibabel/nifti_images.html#choosing-the-image-affine
#        '''
#        self.img.set_qform(reference.img.affine)
#
#        print(f"Old sform: {self.get_sform_code()}")
#        print(f"Old qform: {self.get_qform_code()}")
#
#        if (self.get_qform_code() != reference.get_qform_code()):
#            self.set_qform_code(reference.get_qform_code())
#
#        if (self.get_sform_code() != reference.get_sform_code()):
#            self.set_sform_code(reference.get_qform_code())
#
#        print(f"New sform: {self.get_sform_code()}")
#        print(f"New qform: {self.get_qform_code()}")
#        assert np.any((self.img.get_qform(), reference.img.get_qform()))
#        assert np.any((self.img.get_sform(), reference.img.get_sform()))
#
#        assert self.get_qform_code() == reference.get_qform_code()
#        assert self.get_sform_code() == reference.get_sform_code()
    

    # def check_alignment(self, other: Self) -> bool:
    #     for key in self.__img.header.keys():
    #         try:
    #             if key in ['dim', 'pixdim', 'srow_x', 'srow_y', 'srow_z']:
    #                 if not (np.any((self.__img.header[key], other.__img.header[key]))):
    #                     raise AssertionError
    #             else:
    #                 if (self.__img.header[key] != other.__img.header[key]):
    #                     raise AssertionError
    #         except AssertionError as e:
    #             print("Mismatch!")
    #             print(f"Key: {key} \nValue type: {type(self.__img.header[key])}")
    #             print(f"Value in {self.__img.get_filename()}: {self.__img.header[key]}\n \
    #                     Value in {other.__img.get_filename()}: {other.__img.header[key]}\n")
