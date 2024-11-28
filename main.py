from absl import app, flags
import numpy as n
np.set_printoptions(precision=20)

from classes.Image import NII
from utils.utils import *
from utils.enums import ReorientKey, Direction, SFORM_CODE

import nibabel as nib
# from scripts.reorient import reorient
# from scripts.register import register
# from scripts.unpack import unpack
# from scripts.unzip import unzip
# from scripts.warp_vent import warp_vent

import os

import logging
logging.basicConfig(filename='log.log', encoding='utf-8',
                    format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")




FLAGS = flags.FLAGS
flags.DEFINE_string(name="dir", default=None, help="""
                    Pass in a directory to this flag.

                    If this directory is a directory of patients
                    where each patient is its own directory, then
                    the entire program will run for each patient.

                    If the directory passed is for a single patient,
                    only that patient's files will be processed.

                    This is for convenience and testing purposes.

                    In some use cases, you may want to run the pipeline
                    just for a single patient.
                    """, required=True)


def process(patient_dir: str) -> None:
    # Minimum set of files that must exist for any patient, with exactly these names

    original_files = get_files(dir=patient_dir, files=[
        "CT.nii",
        "CT_mask.nii",
        "mask_reg_edited.nii",
        "gas_highreso.nii",
        "rbc2gas.nii",
        "membrane2gas.nii"
    ])

    ct_img = NII(filename=original_files[0])
    ct_mask = NII(filename=original_files[1])

    if not (ct_img.get_axcodes() == tuple("RAS") and ct_mask.get_axcodes() == tuple("RAS")):
        for img in [ct_img, ct_mask]:
            logging.info(f"Detected {img.get_axcodes()} axcodes for NIFTI image {img.get_filename()}")
            # Ensure that the reference and mask both have pixdim[0] != 0
            if not img.get_qfac():
                logging.info(
                    f"{img.get_filename()} has pixdim[0] = 0. Setting to 1 (scanner).")
                img.set_qfac(1)

            # Ensure that the srow matrix will be used by setting the sform_code to 1
            if (img.get_sform_code() == 0):
                logging.info(
                    f"{img.get_filename()} has sform_code = 0. Setting to 1 (scanner).")
                img.set_sform_code(1)

        x, y, z = ct_img.get_origin()
        ct_mask.translate(-x, -y, -z)
    else:
        for img in [ct_img, ct_mask]:
            logging.info(f"Detected {img.get_axcodes()} axcodes for NIFTI image {img.get_filename()}")

        """In the case where both the reference and the mask are in RAS, 
        is sufficient to translate the mask to match the origin of the reference"""
        x, y, z = ct_img.get_origin()
        ct_mask.translate(-x, -y, -z)
        ct_mask.save()

    # for fn in original_files[1:]:  # Resize all files except for CT_mask.nii
    #     print(patient_dir)
    #     print(os.path.basename(fn))
    #     resize(img_path=fn)

    post_resize_files = get_files(dir=patient_dir, files=[
        "CT.nii",
        "CT_mask.nii",
        "mask_reg_edited_scaled.nii",
        "gas_highreso_scaled.nii",
        "rbc2gas_scaled.nii",
        "membrane2gas_scaled.nii"
    ])

#    for fn in post_resize_files:
#        if "CT_mask" in fn:
#            reorient(file=fn, key=ReorientKey.CT.value)
#        else:
#            reorient(file=fn, key=ReorientKey.VENT.value)
#
#    files = [  # After resizing and reorienting
#        "CT_nii",
#        "CT_mask_neg_affine.nii",
#        "mask_reg_edited_scaled_mutated_affine.nii",
#        "gas_highreso_scaled_mutated_affine.nii",
#        "rbc2gas_scaled_mutated_affine.nii",
#        "membrane2gas_scaled_mutated_affine.nii"
#    ]
#
#    ct_file, mr_file, gas, rbc, mem = [
#        os.path.join(patient_dir, fn) for fn in files]
#
#    # Assert files exist *after* reorienting and resizing
#    for fn_path in [os.path.join(patient_dir, fn) for fn in files]:
#        if not os.path.exists(fn_path):
#            raise Exception(f"""
#                  File {fn_path} does not exist for patient {patient_dir[5:]}
#                  but it is required for processing them in this pipeline.
#                  """)
#
#    print(f"ct {ct_file} | mr {mr_file} | gas {gas} | rbc {rbc} | mem {mem}")
#
#    register(ct_filename=ct_file, mri_filename=mr_file, dir=patient_dir)
#    unpack(ct_file=ct_file, dir=patient_dir)
#    unzip(os.path.join(patient_dir, "warped_mri.nii.gz"))
#
#    for ven in [gas, rbc, mem]:
#        warp_vent(ct=ct_file, dir=patient_dir, vent=ven)
#
#
 

def main(argv):
    dir_ = FLAGS.dir
    print(dir_)
    if contains_subdir(dir_):
        print("Recieved a batch directory of multiple patients.")
        for subdir in get_subdirs(dir_):
            print(f"Processing patient {subdir[5:]}")
            process(patient_dir=subdir)
    else:
        print("Recieved a directory of single patient.")
        print(f"Processing patient {dir_[5:]}")
        process(patient_dir=dir_)


if __name__ == "__main__":
    app.run(main)
