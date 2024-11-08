#!/bin/bash

shopt -s extglob

echo "This script removes files created in the registration process when starting over."

for img_dir in imgs/*; do
    if [[ -d $img_dir ]]; then
        for file in "$img_dir"/*; do
            #if [[ -f $file && "$file" != @(*"CT_mask.nii"*|*"mask_reg_edited.nii"*|*"gas_highreso.nii"*|*"proton_reg.nii"*|*"warped_mri.nii.gz"*) ]]; then
            if [[ -f $file && "$file" != @(*"CT_mask.nii"*|*"mask_reg_edited.nii"*|*"gas_highreso.nii"*|*"proton_reg.nii"*|*"mask_reg_edited_scaled.nii"*|*"gas_highreso_scaled.nii"*) ]]; then
                rm -rf "$file"
                echo "Removed $file from $img_dir"
            fi
        done
    fi
done
