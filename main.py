from absl import app, flags

from classes.Image import NII
from utils.utils import *
from utils.enums import CODE

from nibabel.nifti1 import Nifti1Image

import subprocess

# from scripts.reorient import reorient
# from scripts.register import register
# from scripts.unpack import unpack
# from scripts.unzip import unzip
# from scripts.warp_vent import warp_vent

from logger import logger

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
    ct_img = NII(filename=get_files(dir=patient_dir, files="CT.nii"))
    ct_mask = NII(filename=get_files(dir=patient_dir, files="CT_mask.nii"))
    
    for img in [ct_img, ct_mask]:
        logger.info(f"Checking xform codes for {img.get_filename()}")
        out = None
        if img.get_qform_code() == 0:
            out = subprocess.run(["bash", "scripts/modify_xform.sh", "-s", "1", "-q", "1", "-f", f"{img.get_filename()}"])
        elif img.get_sform_code() == 0 and img.get_qform_code() == 1:
            out = subprocess.run(["bash", "scripts/modify_xform.sh", "-s", "1", "-f", f"{img.get_filename()}"])
        elif img.get_sform_code() == 1 and img.get_qform_code() == 1:
            logger.info(f"File {img.get_filename()} already has sform_code = 1 and qform_code = 1")

        # out = None in the case that xfrom codes were not modified        
        if out != None and out.returncode == 0:
            logger.info(f"{img.get_filename()} sform code and qform changed.")
            img_ = NII(filename=img.get_filename()) # Reload/reread image (the filename will not have changed)
            logger.info(f"New sform_code of {img.get_filename()}: {img_.get_sform_code()}")
        continue
    
        ax = ''.join(img.get_axcodes())
        logger.info(f"File {img.get_filename()} currently has RAS orientation: {ax}")
        if ax != "RAS":
            img.toRAS()
        else:
            logger.info(f"File {img.get_filename()} in proper orientation (RAS). Leaving unchanged...") 
     
    logger.info(f"xform codes and orientation fixed, aligning CT image to mask...")
    assert 0 == 1
    x, y, z = ct_img.get_origin()
    ct_mask.translate(x, y, z)
    
    try: 
        assert ct_mask.is_matched_by_origin(ct_img)
        ct_mask.save(ct_mask.get_filename()[:-4] + "_translated.nii")
        logger.info(f"Image {ct_mask.get_filename()} saved!")
    except AssertionError as e:
        logger.info(f"Unable to match origin of {ct_mask.get_filename()} to origin of {ct_img.get_filename()}!")
        return
       
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
