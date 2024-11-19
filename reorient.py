from utils import nib_save, set_qform
import nibabel as nib

def reorient(ct_file_paths: str | list , mr_file_paths: str | list, ve_file_paths: str | list) -> None:
    for paths in [ct_file_paths, mr_file_paths, ve_file_paths]:
        if type(paths) != list:
            paths = [paths]
            assert type(paths) == list
            
    for ct_file, mr_file, ve_file in zip(ct_file_paths, mr_file_paths, ve_file_paths):
        print(f"CT mask file path: {ct_file} |\
                MRI mask file path: {mr_file} |\
                Ventilation image file path: {ve_file}")

        nib_ct = {'ct': [nib.load(ct_file), ct_file[:-4] + '_neg_affine.nii']}

        nib_mr_vent = {'mr': [nib.load(mr_file), mr_file[:-4] + '_mutated_affine.nii'],
                       've': [nib.load(ve_file), ve_file[:-4] + '_mutated_affine.nii']}

        for key in nib_ct.keys():
            img = nib_ct[key][0]
            filename = nib_ct[key][1]
            set_qform(img=img, type=True)
            nib_save(img=img, filename=filename)

        for key in nib_mr_vent.keys():
            img = nib_mr_vent[key][0]
            filename = nib_mr_vent[key][1]
            set_qform(img=img, type=False)
            nib_save(img=img, filename=filename)

    