import os
import glob
import numpy as np

import nibabel as nib
from nibabel.filebasedimages import FileBasedImage
from nibabel.orientations import aff2axcodes
from nibabel.nifti1 import Nifti1Image


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


def aff2axcodes_RAS(aff):
    return aff2axcodes(aff=aff, labels=(('R', 'L'), ('A', 'S'), ('S', 'I')))


"""
Return the paths to the subdirs of a given dir
"""


def get_subdirs(dir: str) -> list[str]:
    return [os.path.join(dir, subdir) for subdir in os.listdir(dir)]


"""
Sets the qform affine matrix of the given image;
if type is true, then set affine for 'ct_lobe' otherwise set affine for 'mr_vent'
"""


def set_qform(img: FileBasedImage, type: bool) -> None:
    aff = img.affine
    if type:
        for i in range(3):
            if (aff[i][i] > 0):  # The sign along the diagonal will not be flipped if it is already negative
                aff[i][i] = -aff[i][i]
    else:
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


def nib_save(img: FileBasedImage, filename: str) -> None:
    nib.save(img=img, filename=filename)
    print(f"Saved image to {filename} having axcodes {aff2axcodes_RAS(img.affine)}")


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


"""
Returns the element-wise (Hadamard) product between the mask and the data
"""


def apply_mask(mask: np.memmap | np.ndarray, data: np.memmap | np.ndarray) -> np.memmap | np.ndarray:
    if mask.shape == data.shape:
        log.info("Mask and data shapes match, applying mask...")
        return np.multiply(mask, data)
    return None


"""
Get a nibabel FileBasedImage from a 3D data matrix
"""


def get_nib(fdata: np.ndarray):
    pass


"""
Return a list of file-based images
"""


def splits_to_imgs(original_mask: np.memmap | np.ndarray) -> list[FileBasedImage]:
    pass


"""
Returns true if the given directory has any subdirectories

Used for distinguishing between a node directory and a parent directory.

A node directory is one that has no subdirectories.

A parent directory is one that has at least another level of subdirectories.
"""


def has_sub_dirs(dir: str) -> bool:
    return len(set([os.path.dirname(p) for p in glob.glob(dir + "/*/*")])) == True
