from utils import read_ANTS, aff2axcodes_RAS, get_subdirs
import os
import nibabel as nib
from nibabel.nifti1 import Nifti1Image
from nilearn.image.resampling import resample_to_img, resample_img
from time import time, sleep
from sys import argv
import numpy as np

prep_start_time = time()

BASE_DIR = argv[1]
NUM_THREADS = os.cpu_count()
subdir_paths = get_subdirs(dir=BASE_DIR)[0:1]

ct_files = read_ANTS(as_type='ct', dir=BASE_DIR, ret_ants=False, ct_filename="CT_mask.nii",
                     mr_filename="mask_reg_edited.nii", vent_filename="gas_highreso.nii")[0:1]
proton_files = read_ANTS(as_type='proton', dir=BASE_DIR, ret_ants=False, ct_filename="CT_mask.nii",
                         mr_filename="mask_reg_edited.nii", vent_filename="gas_highreso.nii")[0:1]

"""
Reorient ct
"""
for ct_file, subdir in zip(ct_files, subdir_paths):
    print(ct_file)

    nib_ct = nib.load(ct_file)
    print(nib_ct.shape)
    print(f"CT NIFTI header before reorienting affine matrix\n: {
          nib_ct.header}")

    aff = nib_ct.affine
    for i in range(3):
        if (aff[i][i] > 0):
            aff[i][i] = -aff[i][i]

    nib_ct.set_qform(aff)
    path = ct_file[:-4] + '_neg_affine.nii'
    if not os.path.exists(path):
        nib.save(img=nib_ct, filename=path)
        print(f"Saved to {path}!")
        print(aff2axcodes_RAS(nib_ct.affine))
        print(f"CT NIFTI header after reorienting affine matrix\n: {
            nib_ct.header}")
        sleep(3)

    else:
        print(f"File {path} already exists.")

"""
# Reorient mri
"""
for mri_file, ct_file, subdir in zip(proton_files, ct_files, subdir_paths):
    print(mri_file)

    nib_mr = nib.load(mri_file)
    nib_ct = nib.load(ct_file)
    print(f"MR NIFTI header before reorienting affine matrix\n: {
          nib_mr.header}")

    aff = nib_mr.affine
    new_aff = np.array([[0, -1, 0, 0],
                        [0, 0, -1, 0],
                        [-1, 0, 0, 0],
                        [0, 0, 0, 1]])

    nib_mr.set_qform(new_aff)
   # new_mr = resample_to_img(source_img=nib_mr, target_img=nib.load(ct_file))
    new_mr = resample_img(
        # nearest interpolation or binary images
        img=nib_mr, target_affine=nib_ct.affine, target_shape=nib_ct.shape, interpolation="nearest")
    assert type(new_mr) == Nifti1Image
    print(new_mr.header['dim'])
    hdr_copy = new_mr.header.copy()
    hdr_copy['dim'][1] *= 2
    hdr_copy['dim'][2] *= 2
    hdr_copy['dim'][3] *= 2

    new_mr = Nifti1Image(new_mr.get_fdata(), new_mr.affine, header=hdr_copy)

    path = mri_file[:-4] + '_mutated_affine.nii'
    if not os.path.exists(path):
        nib.save(img=new_mr, filename=path)
        print(f"Saved to {path}!")
        print(aff2axcodes_RAS(new_mr.affine))
        print(f"MRI NIFTI header after reorienting affine matrix\n: {
            new_mr.header}")
        sleep(3)
    else:
        print(f"File {path} already exists.")

prep_end_time = time()
print(f"That took: {prep_end_time - prep_start_time} min/sec")
