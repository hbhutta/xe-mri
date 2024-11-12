import os
import glob
import numpy as np
import nibabel as nib
from nibabel.orientations import aff2axcodes
from nibabel.filebasedimages import FileBasedImage

"""
Given a directory, list the files common to all the first-level subdirectories
"""


def get_common_files(base_dir: str, filename: str | None) -> list[str]:
    file_sets_by_subdir = {}
    sample_subdir = None
    for subdir in os.listdir(base_dir):
        sample_subdir = subdir
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
            if (aff[i][i] > 0):
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
    print(aff2axcodes_RAS(img.affine))
