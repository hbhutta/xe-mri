from utils import nib_save, set_qform
import nibabel as nib


def reorient(ct_file: str, mr_file: str, ve_file: str) -> None:

    print(f"ct: {ct_file} |  mr : {mr_file} | ve : {ve_file}")

    ct_img = nib.load(ct_file)
    ct_filename = ct_file[:-4] + '_neg_affine.nii'
    set_qform(img=ct_img, type=True)
    nib_save(img=ct_img, filename=ct_filename)

    mr_img = nib.load(mr_file)
    mr_filename = mr_file[:-4] + '_mutated_affine.nii'
    set_qform(img=mr_img, type=False)
    nib_save(img=mr_img, filename=mr_filename)

    ve_img = nib.load(ve_file)
    ve_filename = ve_file[:-4] + '_mutated_affine.nii'
    set_qform(img=ve_img, type=False)
    nib_save(img=ve_img, filename=ve_filename)
