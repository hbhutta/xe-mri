from utils import read_ANTS, aff2axcodes_RAS, get_subdirs
import os
import nibabel as nib
from nibabel.nifti1 import Nifti1Image
from time import time, sleep
from sys import argv
import numpy as np

prep_start_time = time()

BASE_DIR = argv[1]
NUM_THREADS = os.cpu_count()
subdir_paths = get_subdirs(dir=BASE_DIR)[0:1]

ct_files = read_ANTS(as_type='ct', dir=BASE_DIR, ret_ants=False, ct_filename="CT_mask.nii",
                     mr_filename="mask_reg_edited.nii", vent_filename="gas_highreso.nii")[0:1]
mri_files = read_ANTS(as_type='proton', dir=BASE_DIR, ret_ants=False, ct_filename="CT_mask.nii",
                      mr_filename="mask_reg_edited.nii", vent_filename="gas_highreso.nii")[0:1]


def dim_info(hdr):
    return {
        'dim': hdr['dim'][1:4],
        'pixdim': hdr['pixdim'][1:5],
        'sform_code': hdr['sform_code'],  # Should not be 0 ???
        'qform_code': hdr['qform_code'],  # Should not be 0 ???
    }


def set_pixdim(img: Nifti1Image, pixdims: tuple) -> Nifti1Image:
    hdr_copy = img.header.copy()
    hdr_copy['pixdim'][1] = pixdims[0]
    hdr_copy['pixdim'][2] = pixdims[1]
    hdr_copy['pixdim'][3] = pixdims[2]

    return Nifti1Image(dataobj=img.get_fdata(), affine=img.affine, header=hdr_copy)


def set_all_mri(img: Nifti1Image, pixdims: tuple) -> Nifti1Image:
    img_ = set_pixdim(img, pixdims=pixdims)

    img_.set_qform(np.array([[0, -1, 0, 0],
                            [0, 0, -1, 0],
                            [-1, 0, 0, 0],
                            [0, 0, 0, 1]]))

    return img_
#    return Nifti1Image(dataobj=img_.get_fdata(), affine=img_.affine, header=img_.header)


def set_all_ct(img: Nifti1Image) -> Nifti1Image:
    new_ct_aff = img.affine
    for i in range(3):
        if (new_ct_aff[i][i] > 0):
            new_ct_aff[i][i] = -new_ct_aff[i][i]
    img.set_qform(new_ct_aff)
    return img
#    hdr_copy = img.header.copy()
#    return Nifti1Image(dataobj=img.get_fdata(), affine=img.affine, header=hdr_copy)


"""
Reorient ct
"""
for ct_file, mri_file, patient_path in zip(ct_files, mri_files, subdir_paths):
    print(patient_path)

    # 0. Confirm that nib objects are of type Nifti1Image
    nib_ct = nib.load(ct_file)
    print(type(nib_ct))
    nib_mr = nib.load(mri_file)
    print(type(nib_mr))

    # 1. Check header files (voxel size and number of voxels in xyz, before reorienting):
    print(f"CT NIFTI dim_info before reorienting affine matrix\n: {
          dim_info(nib_ct.header)}\n\n\n")

    print(f"MRI NIFTI dim_info before reorienting affine matrix\n: {
          dim_info(nib_mr.header)}\n\n\n")
    sleep(3)

    CT_mask_neg_affine = set_all_ct(img=nib_ct)
    mask_reg_edited_mutated_affine = set_all_mri(img=nib_mr, pixdims=tuple(
        [nib_ct.header['pixdim'][1], nib_ct.header['pixdim'][2], nib_ct.header['pixdim'][3]]))

    # 3. ct and mr paths
    ct_path = ct_file[:-4] + '_neg_affine.nii'
    mr_path = mri_file[:-4] + '_mutated_affine.nii'

    if not os.path.exists(ct_path):
        nib.save(img=CT_mask_neg_affine, filename=ct_path)
        print(f"Reoriented CT saved to {ct_path}!")
        # Load in the saved image to check if changes were saved
        changed_ct = nib.load(filename=ct_path)
        print(f"Axis codes for CT after reorienting: {
              aff2axcodes_RAS(changed_ct.affine)}")
        print(f"CT NIFTI dim_info after reorienting affine matrix\n: {
            dim_info(changed_ct.header)}")
        sleep(3)
    else:
        print(f"Reoriented CT file already exists at {ct_path}")

    if not os.path.exists(mr_path):
        nib.save(img=mask_reg_edited_mutated_affine, filename=mr_path)
        print(f"Reoriented MRI saved to {mr_path}!")
        # Load in the saved image to check if changes were saved
        changed_mr = nib.load(filename=mr_path)
        print(f"Axis codes for MRI after reorienting: {
              aff2axcodes_RAS(changed_mr.affine)}")

        print(f"MRI NIFTI dim_info after reorienting affine matrix\n: {
            dim_info(changed_mr.header)}")
        sleep(3)

    else:
        print(f"Reoriented MRI file already exists at {mr_path}")
