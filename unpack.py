from utils import get_subdirs, read_ANTS
import os
import nibabel as nib
from sys import argv
import pickle
import ants

BASE_DIR = argv[1]
NUM_PATIENTS = 25
subdir_paths = get_subdirs(dir=BASE_DIR)[0:NUM_PATIENTS]
print(subdir_paths)

ct_files = read_ANTS(as_type='ct', dir=BASE_DIR,
                     ret_ants=False, ct_filename='CT_mask_neg_affine.nii')[0:NUM_PATIENTS]
print(ct_files)

for ct_file, patient in zip(ct_files, subdir_paths):
    print(patient)
    with open(f"{patient}/{os.path.basename(patient)}_reg.pkl", "rb") as file:
        reg = pickle.load(file)
        print(reg)

        warped_proton = reg['warpedmovout']

        dst = f"{patient}/warped_mri.nii.gz"

        ants_ct = ants.image_read(ct_file)

        try:
            # Check shape
            if ants_ct.shape != warped_proton.shape:
                raise AssertionError(f"Shape mismatch: ants_ct.shape={
                                     ants_ct.shape}, warped_proton.shape={warped_proton.shape}")

            # Check dimensions
            if ants_ct.dimension != warped_proton.dimension:
                raise AssertionError(f"Dimension mismatch: ants_ct.dimension={
                                     ants_ct.dimension}, warped_proton.dimension={warped_proton.dimension}")

            # Check spacing
            if ants_ct.spacing != warped_proton.spacing:
                raise AssertionError(f"Spacing mismatch: ants_ct.spacing={
                                     ants_ct.spacing}, warped_proton.spacing={warped_proton.spacing}")

            # Check origin
            if ants_ct.origin != warped_proton.origin:
                raise AssertionError(f"Origin mismatch: ants_ct.origin={
                    ants_ct.origin}, warped_proton.origin={warped_proton.origin}")

        except AssertionError as e:
            print(f"Assertion failed: {e}")
            break

    ants.image_write(image=warped_proton, filename=dst)
    print(f"Wrote ANTsImage to: {dst}")

    # Print and inspect the forward transforms from the registration
    print(ants.read_transform(reg['fwdtransforms'][1]).parameters)
