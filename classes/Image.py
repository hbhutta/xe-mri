from typing import Self

import nibabel as nib
from nibabel.orientations import aff2axcodes
from nibabel.nifti1 import Nifti1Image, Nifti1Header

import numpy as np
import os
from logger import logger
from utils.enums import CODE


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

    Changing the origin in the srow matrix in the header
    changes the origin but does not change the qoffset values

    Changing the qoffset values does not change the origin
    in the image information displayed in ITK-SNAP. It also
    does not change the origin values as they appear in the 
    srow matrix.

    This means the srow matrix, and not the qoffset values,
    should be directly manipulated to cause a translation

    Everytime the header is changed, the image private attribute 
    should be updated
    
    Should use best_affine() on new header 
    if we do self.__img.header.get_best_affine(),
    this would use the best affine from 
    the header of the old image, while the best 
    affine in the header of the new image may be different.
    
    the set_qform function in nifti1.py also sets the qfac (pixdim[0])

    References: 
    1. https://stackoverflow.com/questions/47996388/python-boolean-methods-naming-convention
    2. https://nipy.org/nibabel/nibabel_images.html#loading-and-saving
    3. https://nipy.org/nibabel/coordinate_systems.html#the-affine-matrix-as-a-transformation-between-spaces
    4. https://nifti.nimh.nih.gov/pub/dist/src/niftilib/nifti1.h
    5. https://nipy.org/nibabel/nifti_images.html#choosing-the-image-affine
    """

    def __init__(self, filename: str):
        self.__img = nib.load(filename=filename)
        self.__filename = filename

    def get_header(self) -> Nifti1Header:
        return self.__img.header.copy()
    
    def __save_header(self, hdr: Nifti1Header, verbose: bool | None = False) -> None:
        self.__img = Nifti1Image(dataobj=self.get_fdata(), affine=self.get_affine(), header=hdr)
        if (verbose):
            logger.info(f"Updated header of {self.get_filename()}")
            using_sform = self.get_sform_code() != 0
            logger.info(f"Using %s: {hdr['sform_code']}" % "sform_code" if using_sform else "qform_code")

    def set_dims(self, dim_x: float | None = 0.0, dim_y: float | None = 0.0, dim_z: float | None = 0.0) -> None:
        hdr = self.get_header()
        hdr['srow_x'][0] += dim_x
        hdr['srow_y'][1] += dim_y
        hdr['srow_z'][2] += dim_z
        self.__save_header(hdr)

    def translate(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        hdr = self.get_header()

        logger.info(f"Origin of {self.get_filename()} before translation: {self.get_origin()}")
        logger.info(f"Translating {self.get_filename()} by (x={x}, y={y}, z={z})")

        # srow matrix is being used as affine (srow matrix visible in header)
        if (self.get_sform_code() == 1):
            logger.info(f"{self.get_filename()} has sform code: {self.get_sform_code()}")

            hdr['srow_x'][3] += x
            hdr['srow_y'][3] += y
            hdr['srow_z'][3] += z

        elif (self.get_sform_code() == 0):
            pass

        self.__save_header(hdr)
        logger.info(f"Origin of {self.get_filename()} after translation: {self.get_origin()}")

    def get_quatern(self, quatern: str) -> int:
        hdr = self.get_header()
        return hdr['quatern_' + quatern] 
    
    def get_unit_quaternion(self) -> np.array:
        hdr = self.get_header()
        b = self.get_quatern('b')
        c = self.get_quatern('c')
        d = self.get_quatern('d')
        a = np.sqrt(1.0 - (b**2 + c**2 + d**2))
        
        return np.asarray([a, b, c, d])
 
    def set_quaterns(self, quatern_b: float | None = 0.0, quatern_c: float | None = 0.0, quatern_d: float | None = 0.0) -> None:
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

    def get_qfac(self) -> str:
        hdr = self.get_header()
        return hdr['pixdim'][0]

    def get_filename(self) -> str:
        return self.__filename

    def get_sform(self) -> np.array:
        hdr = self.get_header()
        sform = hdr.get_sform(coded=False)
        return sform

    def get_qform(self) -> np.array:
        hdr = self.get_header()
        qform = hdr.get_qform(coded=False)
        return qform
    
    def get_sform_code(self) -> int:
        hdr = self.get_header()
        _, sform_code = hdr.get_sform(coded=True)
        return sform_code

    def get_qform_code(self) -> int:
        hdr = self.get_header()
        _, qform_code = hdr.get_qform(coded=True)
        return qform_code

    def set_sform_code(self, sform_code: CODE):
        hdr = self.get_header()
        hdr.set_sform(self.get_sform(), code=sform_code.value)
        self.__save_header(hdr, verbose=True)

    def set_qform_code(self, qform_code: CODE):
        hdr = self.get_header()
        hdr.set_qform(self.get_qform(), code=qform_code.value)
        self.__save_header(hdr, verbose=True)

    def get_origin(self) -> np.array:
#        hdr = self.get_header()
#        x = hdr['srow_x'][3]
#        y = hdr['srow_y'][3]
#        z = hdr['srow_z'][3]
        sform = self.get_sform()
        origin = np.array([sform[0,3], sform[1,3], sform[2,3]], dtype=np.float64)
        return origin

    def get_dims(self) -> np.array:
        hdr = self.get_header()
        dim_x = hdr['pixdim'][1]
        dim_y = hdr['pixdim'][2]
        dim_z = hdr['pixdim'][3]
        return np.array([dim_x, dim_y, dim_z])
    
    def get_affine(self) -> np.array:
        hdr = self.get_header()
        return hdr.get_best_affine()
    
    def set_sform(self, sform) -> None:
        hdr = self.get_header()
        hdr.set_sform(affine=sform)
        self.__save_header(hdr, verbose=True)
        
    def set_qform(self, qform) -> None:
        hdr = self.get_header()
        hdr.set_qform(affine=qform)
        self.__save_header(hdr, verbose=True)
    
    def toRAS(self) -> None:
        logger.info(f"Reorienting {self.get_filename()} to RAS")
        # Maybe only the qform is affected by flipping
        aff = self.get_qform()
        for i in range(3):
            if (aff[i][i] > 0):
                aff[i][i] = -aff[i][i]
        self.set_qform(aff)
   
#    nib_ct.set_qform(ct_aff) 
        # qform = self.get_qform()
        # if qform[0,0] > 0: logger.info("Flipping along x-axis"); qform[0,0] *= -1
        # if qform[1,1] > 0: logger.info("Flipping along y-axis"); qform[1,1] *= -1
        # if qform[2,2] > 0: logger.info("Flipping along z-axis"); qform[2,2] *= -1

    def is_matched_by_sform(self, other: Self) -> bool:
        return np.all(self.get_sform() == other.get_sform())

    def is_matched_by_qform(self, other: Self) -> bool:
        return np.all(self.get_qform() == other.get_sform())

    def is_matched_by_origin(self, other: Self) -> bool:
        return np.all(self.get_origin() == other.get_origin())

    def get_fdata(self) -> np.memmap | np.ndarray:
        return self.__img.get_fdata()

    def get_axcodes(self) -> tuple:
        return aff2axcodes(aff=self.get_affine(), labels=(('R', 'L'), ('A', 'P'), ('S', 'I')))

    def save(self, filename: str) -> None:
        if filename == self.get_filename(): # Overwrite 
            copy_filename = filename[:-4] + "_copy.nii"  # Create copy
            # Save copy with original filename
            nib.save(img=self.__img, filename=copy_filename)
            # Rename copy's name to original filename
            os.rename(src=copy_filename, dst=self.get_filename())
        else:
            nib.save(img=self.__img, filename=filename)
