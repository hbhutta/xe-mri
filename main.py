from absl import app, flags
from utils import get_subdirs, has_sub_dirs
import os
import glob
from sh import gunzip

from reorient import reorient
from register import register
from unpack import unpack
from warp_vent import warp_vent

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


def process(dir):
    # Minimum set of files that must exist for any patient, with exactly these names
    files = [
        "CT_mask.nii",
        "mask_reg_edited.nii",
        "gas_highreso.nii",
        "rbc2gas.nii",
        "membrane2gas.nii"
    ]

    patient = dir[:-5]

    ct_file, mr_file, gas, rbc, mem = [os.path.join(dir, fn) for fn in files]

    for fn in files:
        if not os.path.exists(fn):
            raise (f"""
                  File {fn} does not exist for patient {patient}
                  but it is required for processing them in this pipeline.
                  """)

    print(f"ct {ct_file} | mr {mr_file} | gas {gas} | rbc {rbc} | mem {mem}")

    vens = [gas, rbc, mem]
    for ven in vens:
        reorient(ct_file, mr_file, ven)

    register(ct_filename=ct_file, mri_filename=mr_file, patient=patient)

    gz = glob.glob(os.path.join(dir, "warped_mri.nii.gz"))[0]
    gunzip(gz, "--keep", "--force")

    for ven in vens:
        warp_vent(ct=ct_file, patient=patient, vent=ven)


def main(argv):
    dir = FLAGS.dir
    print(dir)
    if has_sub_dirs(dir):
        print("Recieved a batch directory of multiple patients.")
        for subdir in get_subdirs(dir):
            print(f"Processing patient {subdir[:-5]}")
            process(dir=subdir)
    else:
        print("Recieved a directory of single patient.")
        print(f"Processing patient {dir[:-5]}")
        process(dir=dir)


if __name__ == "__main__":
    app.run(main)
