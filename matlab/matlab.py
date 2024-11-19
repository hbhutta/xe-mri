from oct2py import octave
octave.addpath("matlab")
input_dir = "imgs/PIm0216"
file_pattern = "mask_reg_edited.nii"
octave.feval("matlab/resize_nifti", input_dir, file_pattern)

# def resize(input_dir: str, file_pattern: str) -> None:
    # octave.resize(input_dir, file_pattern)
