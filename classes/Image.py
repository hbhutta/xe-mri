from typing import Self

import nibabel as nib
from nibabel.orientations import aff2axcodes
from nibabel.nifti1 import Nifti1Image, Nifti1Header

import numpy as np
import os
from utils.enums import SFORM_CODE, QFORM_CODE


class NII():
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

    Everytime the header is changed, the image private attribute 
    should be updated

    References: 
    1. https://stackoverflow.com/questions/47996388/python-boolean-methods-naming-convention
    2. https://nipy.org/nibabel/nibabel_images.html#loading-and-saving
    3. https://nipy.org/nibabel/coordinate_systems.html#the-affine-matrix-as-a-transformation-between-spaces
    4. https://nifti.nimh.nih.gov/pub/dist/src/niftilib/nifti1.h
    """

    def __init__(self, filename: str):
        self.__img = nib.load(filename=filename)
        self.__filename = filename

    def get_header(self) -> Nifti1Header:
        return self.__img.header.copy()

    def set_dims(self, dim_x: float | None = None, dim_y: float | None = None, dim_z: float | None = None) -> None:
        hdr = self.get_header()

        if not dim_x:
            hdr['srow_x'][0] += dim_x
        if not dim_y:
            hdr['srow_y'][1] += dim_y
        if not dim_z:
            hdr['srow_z'][2] += dim_z

        self.__save_header(hdr)

    def translate(self, x: float | None = 0.0, y: float | None = 0.0, z: float | None = 0.0) -> None:
        hdr = self.get_header()

        if (self.get_sform_code() == 1 and self.get_qform_code() == 0):  # same as having RAS axcod
            if not x:
                hdr['srow_x'][3] += x
            if not y:
                hdr['srow_y'][3] += y
            if not z:
                hdr['srow_z'][3] += z
        elif (self.get_sform_code() == 0 and self.get_qform_code() == 1):
            pass
        self.__save_header(hdr)

    def set_quaterns(self, quatern_b: float | None = None, quatern_c: float | None = None, quatern_d: float | None = None) -> None:
        hdr = self.get_header()

        if not quatern_b:
            hdr['quatern_b'] = quatern_b
        if not quatern_c:
            hdr['quatern_c'] = quatern_c
        if not quatern_d:
            hdr['quatern_d'] = quatern_d

        self.__save_header(hdr)

    def set_qfac(self, qfac: int) -> None:
        hdr = self.get_header()
        hdr['pixdim'][0] = qfac
        self.__save_header(hdr)

    """
    Should use best_affine() on new header 
    if we do self.__img.header.get_best_affine(),
    this would use the best affine from 
    the header of the old image, while the best 
    affine in the header of the new image may be different.
    """

    def __save_header(self, hdr: Nifti1Header) -> None:
        self.__img = Nifti1Image(dataobj=self.get_fdata(
        ), affine=hdr.get_best_affine(), header=hdr)

    def get_filename(self) -> str:
        return self.__filename

    def get_qfac(self) -> str:
        return self.get_header()['pixdim'][0]

    def get_sform_code(self) -> None:
        return self.get_header()['sform_code']

    def set_sform_code(self, sform: int):
        hdr = self.get_header()
        hdr['sform_code'] = sform
        self.__save_header(hdr)

    def set_qform_code(self, qform: int):
        hdr = self.get_header()
        hdr['qform_code'] = qform
        self.__save_header(hdr)

    def get_qform_code(self) -> None:
        return self.get_header()['qform_code']

    def get_qform(self) -> np.array:
        return np.array(self.__img.header.get_qform())

    def set_qform(self, qform: np.ndarray):
        self.get_header().set_qform(affine=qform)
        # null_sform = np.array([
        #     [0., 0., 0., 0.],
        #     [0., 0., 0., 0.],
        #     [0., 0., 0., 0.],
        #     [0., 0., 0., 1.]])

    def get_sform(self) -> np.array:
        return np.array(self.__img.header.get_sform())

    def set_sform(self, sform: np.ndarray):
        self.__img.header.set_sform(affine=sform, code=None)

    def get_origin(self) -> np.array:
        hdr = self.get_header()
        x = hdr['qoffset_x']
        y = hdr['qoffset_y']
        z = hdr['qoffset_z']
        return np.array([x, y, z], dtype=np.float64)

    def get_dims(self) -> np.array:
        hdr = self.get_header()
        dim_x = hdr['pixdim'][1]
        dim_y = hdr['pixdim'][2]
        dim_z = hdr['pixdim'][3]
        return np.array([dim_x, dim_y, dim_z])

    def is_matched_by_sform(self, other: Self) -> bool:
        return np.all(self.get_sform() == other.get_sform())

    def is_matched_by_qform(self, other: Self) -> bool:
        return np.all(self.get_qform() == other.get_sform())

    def is_matched_by_origin(self, other: Self) -> bool:
        return np.all(self.get_origin() == other.get_origin())

    def get_fdata(self) -> np.memmap | np.ndarray:
        return self.__img.get_fdata()

    def get_axcodes(self) -> tuple:
        return aff2axcodes(aff=self.__img.affine, labels=(('R', 'L'), ('A', 'P'), ('S', 'I')))

    def save(self, filename: str) -> None:
        if filename == self.get_filename():
            copy_filename = filename[:-4] + "_copy.nii"  # Create copy
            # Save copy with original filename
            nib.save(img=self.__img, filename=copy_filename)
            # Rename copy's name to original filename
            os.rename(src=copy_filename, dst=self.get_filename())
        else:
            nib.save(img=self.__img, filename=filename)