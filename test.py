from utils.img_utils import flip_ct_or_mri
from utils.nifti_utils import mod_field, disp_field
import nibabel as nib
c = nib.load("imgs_copy_new/PIm0216/CT.nii")
m = nib.load("imgs_copy_new/PIm0216/CT_mask.nii")

fields_to_check = ["sform_code", "qform_code", "quatern_d", "pixdim"]

# Check fields
for f in fields_to_check:
    disp_field(c.get_filename(), f)
    
for f in fields_to_check:
    disp_field(m.get_filename(), f)

c.header['pixdim'][0] = -1

# Make both RAS
aff = c.get_qform()
for i in range(3):
    if (aff[i][i] > 0):  # The sign along the diagonal will not be flipped if it is already negative
        aff[i][i] = -aff[i][i]
c.set_qform(aff)

# Match
mod_field(c.get_filename(), field="sform_code", value=1)
c.set_sform(c.get_qform())

mod_field(m.get_filename(), field="sform_code", value=1)
m.set_qform(c.get_qform())
m.set_sform(c.get_qform())

mod_field(m.get_filename(), field="qform_code", value=1)
mod_field(m.get_filename(), field="quatern_d", value=1)

for f in fields_to_check:
    disp_field(m.get_filename(), f)

nib.save(img=m, filename=m.get_filename()[:-4] + "q.nii")
