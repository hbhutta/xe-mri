import nibabel as nib
from nibabel.nifti1 import Nifti1Header, Nifti1Image
from nibabel.orientations import aff2axcodes
import ants
import numpy as np


class NII():
    def __init__(self, nii_filename: str):
        self.filename = nii_filename
        self.header = self.orientation_info()
        self.ants_image = ants.image_read(filename=nii_filename)

    def get_affine(self):
        return nib.load(self.filename).affine

    def get_axcodes(self) -> tuple:
        return aff2axcodes(self.get_affine())

    def get_shape(self):
        return nib.load(self.filename).get_fdata().shape

    def get_matrix(self):
        #        return nib.load(self.filename).get_fdata()
        # To make sure data matrix is not double?
        return np.array(nib.load(self.filename).dataobj).astype(np.int16, casting='safe')

    def orientation_info(self) -> dict:
        nib_header = nib.load(filename=self.filename).header
        ORIENTATION_INFO = [
            'quatern_b',
            'quatern_c',
            'quatern_d',
            'qoffset_x',
            'qoffset_y',
            'qoffset_z',
            'srow_x',
            'srow_y',
            'srow_z'
        ]
        axcodes = {
            'axcodes': None
        }
        axcodes['axcodes'] = self.get_axcodes()
        # merged dicts
        header = axcodes | {
            key: (nib_header[key]) for key in ORIENTATION_INFO}
        return header
