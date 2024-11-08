#!/bin/bash

shopt -s extglob

echo "This script unzips the warped_mri.nii.gz files into the proper patient directories."

for img_dir in imgs/*; do
    if [[ -d $img_dir ]]; then
        for file in "$img_dir"/*; do
            if [[ -f $file && "$file" == @(*"translate.nii.gz"*) ]]; then
                gunzip "$file" -k # -k flag to keep original .gz file
                echo "Unzipped $file into $img_dir"
            fi
        done
    fi
done
