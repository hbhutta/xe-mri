from utils import get_common_files, aff2axcodes_RAS, get_subdirs, nib_save, set_qform
import nibabel as nib
from sys import argv

BASE_DIR = 'imgs'

subdir_paths = get_subdirs(dir=BASE_DIR)
ct_file_paths = get_common_files(base_dir=BASE_DIR, filename='CT_mask.nii')
mr_file_paths = get_common_files(base_dir=BASE_DIR, filename='mask_reg_edited_scaled.nii')
ve_file_paths = get_common_files(base_dir=BASE_DIR, filename='gas_highreso_scaled.nii')
#lo_file_paths = get_common_files(base_dir=BASE_DIR, filename='CT_lobes_mask.nii')

# print(ct_file_paths)
# print(mr_file_paths)
# print(ve_file_paths)
#print(lo_file_paths)
# assert 0 == 1
#for ct_file, mr_file, ve_file, lo_file, patient in zip(ct_file_paths, mr_file_paths, ve_file_paths, lo_file_paths, subdir_paths):
for ct_file, mr_file, ve_file, patient in zip(ct_file_paths, mr_file_paths, ve_file_paths, subdir_paths):
    print(f"Patient {patient}")
    # print(f"CT mask file path: {ct_file} |\
            # MRI mask file path: {mr_file} |\
            # Ventilation image file path: {ve_file} |\
            # Lobes mask file path: {lo_file}")

    nib_ct_lobe = {'ct': [nib.load(ct_file), ct_file[:-4] + '_neg_affine.nii']}
#                   'lo': [nib.load(lo_file), lo_file[:-4] + '_neg_affine.nii']}

    nib_mr_vent = {'mr': [nib.load(mr_file), mr_file[:-4] + '_mutated_affine.nii'],
                   've': [nib.load(ve_file), ve_file[:-4] + '_mutated_affine.nii']}

    for key in nib_ct_lobe.keys():
        print(key)
        img = nib_ct_lobe[key][0]
        filename = nib_ct_lobe[key][1]
        set_qform(img=img, type=True)
        nib_save(img=img, filename=filename)

    for key in nib_mr_vent.keys():
        print(key)
        img = nib_mr_vent[key][0]
        filename = nib_mr_vent[key][1]
        set_qform(img=img, type=False)
        nib_save(img=img, filename=filename)