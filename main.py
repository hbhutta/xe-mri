from scripts.utils.utils import get_subdirs, has_sub_dirs, get_files
from scripts.utils.enums import ReorientKey

from scripts.reorient import reorient
from scripts.register import register
from scripts.unpack import unpack
from scripts.unzip import unzip
from scripts.warp_vent import warp_vent

import os

from matlab.matlab import resize

from absl import app, flags

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


def process(dir: str) -> None:
    # Minimum set of files that must exist for any patient, with exactly these names
    original_files = get_files(dir=dir, files=[
        "CT_mask.nii",
        "mask_reg_edited.nii",
        "gas_highreso.nii",
        "rbc2gas.nii",
        "membrane2gas.nii"
    ])

    for fn in original_files[1:]:  # Resize all files except for CT_mask.nii
        resize(dir, fn)

    resized_files = get_files(dir=dir, files=[
        "mask_reg_edited_scaled.nii"
        "gas_highreso_scaled.nii",
        "rbc2gas_scaled.nii",
        "membrane2gas_scaled.nii"
    ])

    for fn in ["CT_mask.nii"] + resized_files:
        if "CT_mask" in fn:
            reorient(file=fn, key=ReorientKey.CT.value)
        else:
            reorient(file=fn, key=ReorientKey.VENT.value)

    files = [  # After resizing and reorienting
        "CT_mask_neg_affine.nii",
        "mask_reg_edited_scaled_mutated_affine.nii",
        "gas_highreso_scaled_mutated_affine.nii",
        "rbc2gas_scaled_mutated_affine.nii",
        "membrane2gas_scaled_mutated_affine.nii"
    ]

    ct_file, mr_file, gas, rbc, mem = [os.path.join(dir, fn) for fn in files]

    # Assert files exist *after* reorienting and resizing
    for fn_path in [os.path.join(dir, fn) for fn in files]:
        if not os.path.exists(fn_path):
            raise Exception(f"""
                  File {fn_path} does not exist for patient {dir[5:]}
                  but it is required for processing them in this pipeline.
                  """)

    print(f"ct {ct_file} | mr {mr_file} | gas {gas} | rbc {rbc} | mem {mem}")

    register(ct_filename=ct_file, mri_filename=mr_file, dir=dir)

    unpack(ct_file=ct_file, dir=dir)
    warped_mri_path = os.path.join(dir, "warped_mri.nii.gz")

    unzip(warped_mri_path)

    for ven in [gas, rbc, mem]:
        warp_vent(ct=ct_file, dir=dir, vent=ven)


def main(argv):
    dir = FLAGS.dir
    print(dir)
    if has_sub_dirs(dir):
        print("Recieved a batch directory of multiple patients.")
        for subdir in get_subdirs(dir):
            print(f"Processing patient {subdir[5:]}")
            process(dir=subdir)
    else:
        print("Recieved a directory of single patient.")
        print(f"Processing patient {dir[5:]}")
        process(dir=dir)


if __name__ == "__main__":
    app.run(main)
