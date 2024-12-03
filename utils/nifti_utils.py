import subprocess

def mod_field(nii: str, field: str, value):
    out = subprocess.run(["nifti_tool",
                          "-mod_hdr", "-mod_field", field, str(value),
                          "-infiles",  nii,
                          "-overwrite"])

def disp_field(nii: str, field: str):
    out = subprocess.run(["nifti_tool",
                          "-disp_hdr1", "-field", field,
                          "-infiles",  nii])

# Example
# disp_field("imgs_copy_new/PIm0216/CT_copy.nii", "sform_code")
# mod_field("imgs_copy_new/PIm0216/CT_copy.nii", "sform_code", 1)
# disp_field("imgs_copy_new/PIm0216/CT_copy.nii", "sform_code")

