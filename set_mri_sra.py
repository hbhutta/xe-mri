import nibabel as nib
import numpy as np
from utils import aff2axcodes_RAS
import os

mri_file = 'imgs/PIm0028/warped_mri_scaled.nii'

nib_ = nib.load(mri_file)
print(aff2axcodes_RAS(nib_.affine))

aff = nib_.affine
new_aff = np.array([[-1, 0, 0, 0],
                    [0, -1, 0, 0],
                    [0, 0, -1, 0],
                    [0, 0, 0, 1]])

nib_.set_qform(new_aff)
path = mri_file[:-4] + '_mutated_affine.nii'
if not os.path.exists(path):
    print(nib_.header)
    print(nib_.affine)
    nib.save(img=nib_, filename=path)
    print(f"Saved to {path}!")
    print(aff2axcodes_RAS(nib_.affine))
else:
    print(f"File {path} already exists.")
