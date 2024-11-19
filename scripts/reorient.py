from scripts.utils import nib_save, set_qform
import nibabel as nib
from utils.enums import ReorientKey

def reorient(file: str, key: str) -> None:
    img = nib.load(file)
    if (key == ReorientKey.CT.value):
        filename = file[:-4] + '_neg_affine.nii'
        set_qform(img=img, type=True)
    elif (key == ReorientKey.VENT.value):
        filename = file[:-4] + '_mutated_affine.nii'
        set_qform(img=img, type=False)
    nib_save(img=img, filename=filename)



