from scipy.ndimage import zoom
import numpy as np
from nibabel.filebasedimages import FileBasedImage
from nibabel.nifti1 import Nifti1Image
import nibabel as nib 
from scripts.utils import nib_save, get_common_files, get_subdirs
import logging

BASE_DIR = 'imgs'

"""
def calculate_scale_factors(fixed: FileBasedImage, moving: FileBasedImage):
    fixed_img_shape = fixed.get_fdata().shape
    moving_img_shape = moving.get_fdata().shape
    return tuple([f/m for f, m in zip(fixed_img_shape, moving_img_shape)])
"""

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

def resize(img: FileBasedImage) -> FileBasedImage:
    data = img.get_fdata()
    scaled_data = adjust_scaling(data=data, factor=(2,2,2))
    contrast_adjusted_data = adjust_contrast(data=scaled_data)
    return Nifti1Image(dataobj=contrast_adjusted_data, affine=img.affine) 

mr_file_paths = get_common_files(base_dir=BASE_DIR, filename='mask_reg_edited.nii')
subdir_paths = get_subdirs(dir=BASE_DIR)

for mr_file, patient in zip(mr_file_paths, subdir_paths):
    logging.info(f"Processing MRI file {mr_file} for patient directory {patient}")
    mr_img = nib.load(mr_file)
    processed_mr_img = resize(img=mr_img)
    nib_save(img=processed_mr_img, filename=patient+"/mask_reg_edited_scaled.nii")
    
    
