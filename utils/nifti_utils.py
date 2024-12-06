import subprocess

def mod_field(nii: str, field: str, value):
    if type(value) != str:
        value = str(value)
    subprocess.run(["nifti_tool",
                    "-mod_hdr", "-mod_field", field, value,
                    "-infiles",  nii,
                    "-overwrite"])


def disp_field(nii: str, field: str):
    subprocess.run(["nifti_tool",
                    "-disp_hdr1", "-field", field,
                    "-infiles",  nii])
    
def diff_hdr(nii_1: str, nii_2: str):
    subprocess.run(["nifti_tool",
                    "-diff_hdr", 
                    "-infiles",  nii_1, nii_2])
 
"""
Example:

disp_field("imgs_copy_new/PIm0216/CT_copy.nii", "sform_code")
mod_field("imgs_copy_new/PIm0216/CT_copy.nii", "sform_code", 1)
disp_field("imgs_copy_new/PIm0216/CT_copy.nii", "sform_code")
"""
