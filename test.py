import nibabel as nib
from nibabel.nifti1 import Nifti1Image
import numpy as np

ct_filepath = 'imgs/PIm0028/CT_mask_neg_affine.nii'
mri_filepath = 'imgs/PIm0028/warped_mri.nii.gz'
vent_filepath = 'imgs/PIm0028/gas_highreso.nii'

nib_mri = nib.load(mri_filepath)
nib_ct = nib.load(ct_filepath)
old_aff = nib_mri.affine
print(nib_ct.affine)
print(nib_mri.affine)

s = 0.437
new_mri_affine = np.dot(nib_mri.affine, np.array([
    [s, 0, 0, 0],
    [0, s, 0, 0],
    [0, 0, s, 0],
    [0, 0, 0, 1]
]))

new_mri = Nifti1Image(dataobj=nib_mri.get_fdata(), affine=new_mri_affine)

new_mri.header['srow_x'] = new_mri_affine[0, :]
new_mri.header['srow_y'] = new_mri_affine[1, :]
new_mri.header['srow_z'] = new_mri_affine[2, :]

print(new_mri.affine)
fn = 'imgs/PIm0028/warped_mri_new.nii.gz'

nib.save(img=new_mri, filename='imgs/PIm0028/warped_mri_new.nii.gz')

foo = nib.load(fn)
print(foo.header)
