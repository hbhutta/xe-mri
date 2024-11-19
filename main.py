from absl import app, flags
from utils import get_common_files, get_subdirs, has_sub_dirs
import os 
import glob

from reorient import reorient

FLAGS = flags.FLAGS

flags.DEFINE_string(name="dir", default=None, help="""
                    Pass in a directory to this flag. 
                   
                    If this directory is a directory of patients 
                    where each patient is its own directory, then
                    the entire program will run for each patient.
                    
                    If the directory passed is for a single patient,
                    only that patient's file will be processed.
                    
                    This is for convenience and testing purposes.
                    
                    In some use cases, you may want to run the pipeline 
                    just for a single patient.
                    """, required=True)


def main(argv):
    dir = FLAGS.dir
    if has_sub_dirs(dir):
        print("Recieved a batch of directories, getting common files...")
        subdirs = get_subdirs(dir=dir)
        ct_files, mr_files, ve_files = [get_common_files(base_dir=dir, filename=fn) for fn in [
          "CT_mask.nii",
          "mask_reg_edited.nii",
          "gas_highreso.nii"
        ]]
        reorient(ct_files, mr_files, ve_files)
    else:
        print("Recieved a set of files for a single patient")
        ct_file, mr_file, ve_file = [glob.glob(os.path.join(dir, fn)) for fn in [
          "CT_mask.nii",
          "mask_reg_edited.nii",
          "gas_highreso.nii"
        ]]
        reorient(ct_file, mr_file, ve_file)

if __name__ == "__main__":
    app.run(main)