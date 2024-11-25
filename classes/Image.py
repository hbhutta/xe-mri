from typing import Self

import nibabel as nib
from nibabel.orientations import aff2axcodes
from nibabel.filebasedimages import FileBasedImage

import numpy as np

from utils.enums import Direction


class Image():
    def __init__(self, filename: str):
        self.img = nib.load(filename=filename)

    def get_qform_code(self) -> None:
        return self.img.header['qform_code']

    def set_qform_code(self, qform_code: int):
        self.img.header['qform_code'] = qform_code

    def align(self, reference: Self):
        '''
        Make sure that sform_code and qform_code match
       

        If reference uses the sform affine, 
        self should also use the sform affine,
        otherwise self should use the qform affine
        
        Reference: https://nipy.org/nibabel/nifti_images.html#choosing-the-image-affine
        '''
        self.img.set_qform(reference.img.affine)
        if (self.get_qform_code() != reference.get_qform_code()):
            self.set_qform_code(reference.get_qform_code())

        assert np.any((self.img.get_qform(), reference.img.get_qform()))
        assert self.get_qform_code() == reference.get_qform_code()

    def flip(self, direction: Direction):
        self.img.affine[:, [direction.value]] *= -1

    def check_alignment(self, other: Self) -> bool:
        for key in self.img.header.keys():
            try:
                if key in ['dim', 'pixdim', 'srow_x', 'srow_y', 'srow_z']:
                    if not (np.any((self.img.header[key], other.img.header[key]))):
                        raise AssertionError
                else:
                    if (self.img.header[key] != other.img.header[key]):
                        raise AssertionError
            except AssertionError as e:
                print("Mismatch!")
                print(f"Key: {key} \nValue type: {type(self.img.header[key])}")
                print(f"Value in {self.img.get_filename()}: {self.img.header[key]}\nValue in {other.img.get_filename()}: {other.img.header[key]}\n")

    def axcodes(self) -> tuple:
        return aff2axcodes(aff=self.img.affine, labels=(('R', 'L'), ('A', 'S'), ('S', 'I')))

    def save(self, filename: str) -> None:
        nib.save(img=self.img, filename=filename)

        using_sform = (self.get_sform_code() != 0)
        print(f"Saved!\n Save path: {filename}\nRAS axcodes: {self.axcodes()}\nsform_code: {self.get_sform_code(
        )}\nqform_code: {self.get_qform_code()}\nUsing: {"sform affine" if using_sform else "qform_affine"}")
