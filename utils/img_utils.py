import os
import glob
import numpy as np
import nibabel as nib
from nibabel.filebasedimages import FileBasedImage
from nibabel.nifti1 import Nifti1Image


def flip_ct_or_mri(img, type: bool) -> None:
    aff = img.affine
    if type:  # CT
        for i in range(3):
            if (aff[i][i] > 0):  # The sign along the diagonal will not be flipped if it is already negative
                aff[i][i] = -aff[i][i]
    else:  # MRI or gas
        aff = np.array([[0, -1, 0, 0],
                        [0, 0, -1, 0],
                        [-1, 0, 0, 0],
                        [0, 0, 0, 1]])

    img.set_qform(aff)


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
        print("Mask and data shapes match, applying mask...")
        return np.multiply(mask, data)
    return None
