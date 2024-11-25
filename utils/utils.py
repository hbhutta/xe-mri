import os
import glob

from nibabel.fileholders import FileMap
from nibabel.filebasedimages import FileBasedHeader, FileBasedImage
from nibabel.orientations import aff2axcodes

import numpy as np

import nibabel as nib
from nibabel.nifti1 import Nifti1Image


class FileBasedImage_(FileBasedImage):
    def __init__(self, header: FileBasedHeader | os.Mapping | None = None, extra: os.Mapping | None = None, file_map: os.Mapping[str, nib.FileHolder] | None = None):
        super().__init__(header, extra, file_map)

    
    
class NIFTI(Nifti1Image):
    def __init__(self, dataobj, affine, header=None, extra=None, file_map=None, dtype=None):
        super().__init__(dataobj, affine, header, extra, file_map, dtype)
        self.dataobj = dataobj
        self.affine = affine
        
    def get_qfac(self) -> int:
        return self.header['pixdim'][0]
    
    


"""
Given a directory, list the files common to all the first-level subdirectories
"""


def get_common_files(base_dir: str, filename: str | None) -> list[str]:
    file_sets_by_subdir = {}
    sample_subdir = None
    for subdir in os.listdir(base_dir):
        sample_subdir = subdir
        print(sample_subdir)
        subdir_path = os.path.join(base_dir, subdir)
        files = [file for file in os.listdir(subdir_path)]
        file_sets_by_subdir[subdir] = set(files)

    common_files = file_sets_by_subdir[sample_subdir]
    for key in file_sets_by_subdir.keys():
        common_files &= file_sets_by_subdir[key]

    common_files = list(common_files)
    all_file_paths = glob.glob('**/*', root_dir=base_dir)
    common_file_paths = [file_path for file_path in all_file_paths if any(
        common_file in file_path for common_file in common_files)]

    ret = [os.path.join(base_dir, file_path)
           for file_path in common_file_paths]

    if filename:
        return list(filter(lambda x: filename in x, ret))
    return ret


"""
Using RAS coding instead of LPI coding to print axis codes
"""




"""
Return the paths to the subdirs of a given dir
"""


def get_subdirs(dir: str) -> list[str]:
    return [os.path.join(dir, subdir) for subdir in os.listdir(dir)]


"""
Gets the affine matrix of the given image
"""

"""
Sets the qform affine matrix of the given image;
if type is true, then set affine for 'ct_lobe' otherwise set affine for 'mr_vent'
"""

def flip_ct_or_mri(img: FileBasedImage, type: bool) -> None:
    aff = img.affine
    if type: # CT
        for i in range(3):
            if (aff[i][i] > 0):  # The sign along the diagonal will not be flipped if it is already negative
                aff[i][i] = -aff[i][i]
    else: # MRI or gas
        aff = np.array([[0, -1, 0, 0],
                        [0, 0, -1, 0],
                        [-1, 0, 0, 0],
                        [0, 0, 0, 1]])

    img.set_qform(aff)


"""
Helper function that calls nib.save() but
prints out more information such as:
1. RAS orientation 
"""




"""
Returns a mask
"""


def mask_(data: np.ndarray | np.memmap, target: np.float64 | np.int64 | list) -> list[bool]:
    if type(target) == list:
        mask = list(np.vectorize(lambda x: (x in target))(data))
    else:
        mask = (np.vectorize(lambda x: (x == target))(data))
    # if np.any(mask == True) == np.False_:
        # return mask


"""
Returns a count of the number of pixels in the data matrix 
which are in the target
"""


def count_(data: np.ndarray | np.memmap, target: np.float64 | np.int64 | list) -> int:
    return np.count_nonzero(mask_(data=data, target=target))


"""
Splits a mask into as many masks as there are unique pixel intensities
"""


def split_mask(mask_image_file_path: str, return_imgs: bool | None) -> list[np.memmap | np.ndarray] | list[tuple]:
    print("Loading nib object from mask file path")
    mask_image = nib.load(filename=mask_image_file_path)
    mask = mask_image.get_fdata()

    print("Splitting mask")
    splits = []
    vals = [val for val in np.unique(mask) if val != 0]
    print("Enumerated unique PIs")
    for val in vals:
        print(f"Creating split for PI {val}")
        splits.append(np.where(mask == val, mask, 0))
        print(f"Created split mask for unique PI {val} in mask")

    """
    Assert that the number of masks resulting from
    the split equals the number of unique values 
    in the mask.
    
    For example, if a lobar mask has five unique values
    (one for each lobe), then there should be five splits
    """

    '''
    assert len(splits) == len(vals)
    n = len(splits)

    for i in range(n):
        """
        Assert that the count of non-zero pixels other than 
        the pixel value associated to this split are zero
        """
        assert count_(data=splits[i], target=[
                      val for val in vals if val != vals[i]]) == 0

        """
        Assert that the count of pixels of value val[i]
        in splits[i] is the same as the count of pixels 
        of value val[i] in the original mask
        """
        assert count_(data=splits[i], target=vals[i]) == count_(mask, vals[i])
    '''

    if return_imgs:
        print("Making Nifti1Image objects out of splits data")
        # Will be the same for all splits, because these splits all original from one image
        affine = mask_image.affine
        basename = os.path.basename(mask_image_file_path)
        dirname = os.path.dirname(mask_image_file_path)
        splits_imgs = []

        for split_data, unique_val in zip(splits, vals):
            file_path = f"{dirname}/{basename[:-4]
                                     }_split_PI_{int(unique_val)}.nii"
            print(f"Creating image for file path: {file_path}")
            splits_imgs.append(
                tuple([
                    Nifti1Image(dataobj=split_data, affine=affine),
                    file_path
                ])
            )
        print(f"Returning: {splits_imgs}")
        return splits_imgs
    print(f"Returning: {splits}")
    return splits

def get_qfac(img: FileBasedImage) -> int:
        return img.header['pixdim'][0]

"""
Returns the element-wise (Hadamard) product between the mask and the data
"""


def apply_mask(mask: np.memmap | np.ndarray, data: np.memmap | np.ndarray) -> np.memmap | np.ndarray:
    if mask.shape == data.shape:
        print("Mask and data shapes match, applying mask...")
        return np.multiply(mask, data)
    return None


"""
Returns true if the given directory has any subdirectories
Used for distinguishing between a node directory and a parent directory.
A node directory is one that has no subdirectories.
A parent directory is one that has at least another level of subdirectories.
"""


def has_sub_dirs(dir: str) -> bool:
    return len(set([os.path.dirname(p) for p in glob.glob(dir + "/*/*")])) == True

"""
Get file paths in dir from list of files and path to dir
"""
def get_files(dir: str, files: list[str] | str) -> list[str] | str:
    if type(files) == str:
        return os.path.join(dir, files)
    return [os.path.join(dir, fn) for fn in files]
