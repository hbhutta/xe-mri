# Script order
- Many of the `.py` files use helper functions defined in `utils.py`
- Most of these helper functions just print out useful information, or they help in retrieving common files across the different patient directories (e.g. `readANTS` and `get_common_files`)

---
1. [`resize.py`](resize.py)
- This is a Python script that resizes the MRI mask to *approximately* match the size of the CT mask.
  - An approximate match is enough to enable a more accurate deformable registration in [`register.py`](register.py)
- ~~The `dim` (number of voxels in the xyz directions) and the `pixdim` (voxel spacing; size of voxel in the xyz directions), 
are matched to what values they have in the CT mask's header file. This is done as
a consequence of the `imresize3` function in Matlab.~~
- After resizing, transfer the local `imgs/` directory into the server
- One can check the header file in ITK-SNAP through `Tools > Image Information`, to confirm that the resize changes were applied.
2. `register.sh`
- Runs all these scripts:
  1. [`cleanup.sh`](cleanup.sh)
  - This is an optional script that cleans up any files generated from previous
    registration attempts.
  - Used primarily when testing registration.
  2. `reorient.py`
  - At this stage, the MRI masks closely match the size of the CT masks, but they
    just need to be reoriented (and translated, and deformed using the subsequent
  scripts).
  - This script will modify the affine matrices of the CT masks to have RAS
    axis codes, and the affine matrices of the MRI masks to have SRA axis codes.
  3. `register.py`
  - This is the first phase of registration. The resized and reoriented MR masks 
    are aligned to match the CT masks by translation.
  - The `type_of_transform` parameter was set to `Similarity`.
  - In the second and final phase of registration, the resized, reoriented and translated MR masks undergoes a deformation so that the boundary 
  of the MR mask closely matches the boundary in the CT mask.
  - The `type_of_transform` parameter in the second stage was set to `SynAggro`.
  4. `unpack.py`
  - This script loads the warped MRI images from the serialized output of the similarity registration 
  in the previous step. 
  - The warped MRI images are saved in the patient directories (e.g. PIm0028)
  that they originally came from.
  5. `unzip.sh`
  - This script just unzips the warped MRI images generated in the registration process.
  - The file extension of the warped MRI images changes from `.nii.gz` to `.nii`
  6. `warp_vent.py`
  - Applies the forward transformations from the registration (of the MRI mask onto the CT mask) 
  to the ventilation image as well

First registration phase finished on 11/5/2024


# git stuff
1. `git init` makes this a master branch by default
2. `gite remote add origin <repo>`
3. `git checkout main`
4. `git status` to ensure that the current branch is main
5. `git pull origin main --allow-unrelated-histories` to pull stuff in main that is not in master because the default branch is master
6. `git push origin main` this puts all the stuff in master into main
7. `git push origin --delete master` deletes master; now we just have main`

# Current problems
- [ ] ???

# Current tasks
- [ ] Figure out how VDP is calculated in duke pipeline

# Masking a ventilation image with lobar mask (example)
```python
mask.shape
vent_mask_volm.shape
masked = apply_mask(mask=mask, data=vent_mask_volm)
nib.save(img=nib.nifti1.Nifti1Image(masked, vent_mask_imag.affine), filename="___.nii")
```


# Todo:
- See if imresize3 in matlab has a python equivalent, if not implement it in Python,
or use matlab api/wrapper in python
- rewriting imresize3 process in python