from utils import get_common_files, aff2axcodes_RAS, get_subdirs
import os
import nibabel as nib
from time import time, sleep
from sys import argv
import numpy as np

prep_start_time = time()

BASE_DIR = argv[1]
NUM_THREADS = os.cpu_count()
subdir_paths = get_subdirs(dir=BASE_DIR)

# Assuming each patient has these files
ct_file_paths = get_common_files(base_dir=BASE_DIR, filename='CT_mask.nii')
mri_file_paths = get_common_files(base_dir=BASE_DIR, filename='mask_reg_edited_scaled.nii')
ventilation_file_paths = get_common_files(base_dir=BASE_DIR, filename='gas_highreso_scaled.nii')
lobe_file_paths= get_common_files(base_dir=BASE_DIR, filename='CT_lobes_mask.nii')


# ct_files = read_ANTS(as_type='ct', dir=BASE_DIR,
                    #  ret_ants=False, ct_filename="CT_mask.nii")
# proton_files = read_ANTS(as_type='proton', dir=BASE_DIR,
                        #  ret_ants=False, mr_filename="mask_reg_edited_scaled.nii")
# vent_files = read_ANTS(as_type='vent', dir=BASE_DIR,
                    #    ret_ants=False, vent_filename="gas_highreso_scaled.nii")

# print(proton_files)
# print(vent_files)

for ct_file, mri_file, vent_file, lobe_file, patient in zip(ct_file_paths, mri_file_paths, ventilation_file_paths, lobe_file_paths, subdir_paths):
    print(f"Patient {patient}")
    print(f"CT mask file path: {ct_file} |\
            MRI mask file path: {mri_file} |\
            Ventilation image file path: {vent_file} |\
            Lobes mask file path: {lobe_file}")
   
    # ct and lo should have same orientation 
    nib_ct = nib.load(ct_file)
    nib_lo = nib.load(lobe_file)

    # mr and ve should have same orientation 
    nib_mr = nib.load(mri_file)
    nib_ve = nib.load(vent_file)
    
    ct_aff = nib_ct.affine
    lo_aff = nib_lo.affine
    ct_lo_affs = [ct_aff, lo_aff] 
    for aff in ct_lo_affs:
        for i in range(3):
            if (aff[i][i] > 0):
                aff[i][i] = -aff[i][i]
    
    nib_ct.set_qform(ct_aff)
    nib_lo.set_qform(lo_aff)

    ct_path = ct_file[:-4] + '_neg_affine.nii'
    lo_path = lobe_file[:-4] + '_neg_affine.nii'

    if not os.path.exists(ct_path):
        nib.save(img=nib_ct, filename=ct_path)
        print(f"Saved reoriented CT to {ct_path}!")
        print(aff2axcodes_RAS(nib_ct.affine))
    else:
        print(f"File {ct_path} already exists.")

    if not os.path.exists(lo_path):
        nib.save(img=nib_lo, filename=lo_path)
        print(f"Saved reoriented Lobe to {lo_path}!")
        print(aff2axcodes_RAS(nib_lo.affine))
    else:
        print(f"File {lo_path} already exists.")
   
    

"""
Reorient CT mask (CT_mask.nii) and lobe mask (CT_lobes_mask.nii)
"""
for ct_file, lobe_file, subdir in zip(ct_files, lobe_files, subdir_paths):
    print(ct_file)

    nib_ct = nib.load(ct_file)
    # print(f"CT NIFTI header before reorienting affine matrix\n: {nib_ct.header}")

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
        # print(f"CT NIFTI header after reorienting affine matrix\n: {nib_ct.header}")

    else:
        print(f"File {path} already exists.")

"""
Reorient MRI (mask_reg_edited_scaled.nii) and Ventilation (gas_highreso_scaled.nii)
"""
for mri_file, vent_file, subdir in zip(proton_files, vent_files, subdir_paths):
    print(mri_file)
    print(vent_file)

    nib_mr = nib.load(mri_file)
    nib_vent = nib.load(vent_file)

    aff = nib_mr.affine
    new_aff = np.array([[0, -1, 0, 0],
                        [0, 0, -1, 0],
                        [-1, 0, 0, 0],
                        [0, 0, 0, 1]])

    nib_mr.set_qform(new_aff)
    nib_vent.set_qform(new_aff)

    mr_path = mri_file[:-4] + '_mutated_affine.nii'
    vent_path = vent_file[:-4] + '_mutated_affine.nii'

    # MRI
    if not os.path.exists(mr_path):
        nib.save(img=nib_mr, filename=mr_path)
        print(f"Saved to {mr_path}!")
        print(aff2axcodes_RAS(nib_mr.affine))
    else:
        print(f"File {mr_path} already exists.")

    # Ventilation
    if not os.path.exists(vent_path):
        nib.save(img=nib_vent, filename=vent_path)
        print(f"Saved to {vent_path}!")
        print(aff2axcodes_RAS(nib_vent.affine))
    else:
        print(f"File {vent_path} already exists.")

prep_end_time = time()
print(f"That took: {prep_end_time - prep_start_time} min/sec")
