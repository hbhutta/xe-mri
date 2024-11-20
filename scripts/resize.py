from scipy.ndimage import zoom
from scipy.misc import imresize
import numpy as np
from nibabel.nifti1 import Nifti1Image
import nibabel as nib 
import skimage.transform as skTrans

"""
Scales the given image's data matrix
"""
def adjust_scaling(data: np.memmap, factor: tuple[float]) -> np.memmap | np.ndarray:
    return zoom(data, factor)

"""
To account for fractional and negative pixel intensities caused by zooming
"""
def adjust_contrast(data: np.memmap) -> np.memmap | np.ndarray:
    process = np.where(data > 1, 1, data) # p >= 1 -> 1
    process = np.where(data < 0, 0, data) # p < 0 -> 0
    process = np.where(np.all(data) > 0 & np.all(data) < 1, 0, data) # 0 < p < 1 -> 0
    return process

def resize(img_path: str) -> None:
    img = nib.load(img_path) 
    data = img.get_fdata()
    scaled_data = adjust_scaling(data=data, factor=(2,2,2))
    contrast_adjusted_data = adjust_contrast(data=scaled_data)
    scaled_img = Nifti1Image(dataobj=contrast_adjusted_data, affine=img.affine) 
    nib.save(scaled_img, img_path[:-4] + "_scaled.nii")

def foo(path):
    im = nib.load(path)
    data = im.get_fdata()
    res = skTrans.resize(data, (512,512,368), order=1, preserve_range=True)
    nib.save(Nifti1Image(dataobj=res, affine=im.affine), path[:-4] + "_scaled.nii")
    
foo("imgs/PIm0216/mask_reg_edited.nii")
             