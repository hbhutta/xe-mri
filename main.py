import os
from time import sleep
from absl import app, flags

from classes.Image import NII
from utils.os_utils import contains_subdir, get_files, get_subdirs
from utils.nifti_utils import mod_field, disp_field
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
        logger.info(f"Checking sform codes for {img.get_filename()}")
        out = None
       
        # Ensure that sform_code = 1
        if img.get_sform_code() == 0:
            out = subprocess.run(["bash", "scripts/mod_nii.sh", 
                                  "-f", "sform_code",                   # Field to modify
                                  "-v", "1",                            # New value
                                  "-n", f"{img.get_filename()}"])       # NIFTI file
            logger.info(out.stdout)
        else:
            logger.info(f"sform_code is already 1")
        sleep(2) 
        
        # Ensure that quatern_d = 1
        if img.get_quatern("d") == 0:
            out = subprocess.run(["bash", "scripts/mod_nii.sh", 
                                  "-f", "quatern_d",                    # Field to modify
                                  "-v", "1",                            # New value
                                  "-n", f"{img.get_filename()}"])       # NIFTI file
            logger.info(out.stdout)
            logger.info(f"The unit quaternion is now: {img.get_unit_quaternion()}")
        else:
            logger.info(f"quatern_d is already 1")
        sleep(2) 

        # Ensure that qform_code = 1
        if img.get_qform_code() == 0:
            out = subprocess.run(["bash", "scripts/mod_nii.sh", 
                                  "-f", "qform_code",                   # Field to modify
                                  "-v", "1",                            # New value
                                  "-n", f"{img.get_filename()}"])       # NIFTI file
            logger.info(out.stdout)
        else:
            logger.info(f"qform_code is already 1")
        sleep(2) 
  
        logger.info(f"Original sform affine:\n{img.get_sform()}")
        logger.info(f"Original qform affine:\n{img.get_qform()}")
          
        # Reload image because original data was changed by script 
        img = NII(filename=get_files(dir=patient_dir, files=os.path.basename(img.get_filename())))
        img.save(filename=img.get_filename()) 
       
        logger.info(f"New sform affine:\n{img.get_sform()}")
        logger.info(f"New qform affine:\n{img.get_qform()}")
        continue
        
        if out != None and out.returncode == 0:
            logger.info(f"{img.get_filename()} has sform code changed")
            logger.info(f"New sform_code of {img.get_filename()}: {img.get_sform_code()}")
    
        ax = ''.join(img.get_axcodes())
        logger.info(f"File {img.get_filename()} currently has RAS orientation: {ax}")
        
        if ax != "RAS":
            img.toRAS()
            print(img.get_sform())
            #assert img.get_axcodes() == tuple("RAS")
            logger.info(f"File {img.get_filename()} has axcodes {img.get_axcodes()} after reorientation.")
        else:
            logger.info(f"File {img.get_filename()} in proper orientation (RAS). Leaving unchanged...") 
    
    assert 0 == 1 
    logger.info(f"xform codes and orientation fixed, aligning CT image to mask...")
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
