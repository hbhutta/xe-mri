#!/bin/bash

function usage() {
    cat <<EOF
Usage: $0 [-s <int>] [-q <int>] -infile NII_FILE
This script modifies the sform and/or qform code of the the given NIFTI file.
OPTIONS:
    -s          Optional sform_code
    -q          Optional qform_code
    -f          The NIFTI file to modify
    -h          Show this message
EOF
}

function rename() {
    fname=$(basename "$1" .nii)
    dname=$(dirname -- "$1")
    new_fname="${dname}/${fname}_mod_${2}.nii"
    echo $new_fname
}

sflag=
pflag=
fflag=

# getopts usage: getopts optstring name [args]
OPTSTRING="s:q:f:h" # s, q, and f require arguments, but not h
while getopts ${OPTSTRING} opt; do
    case $opt in
    s)
        echo "Option -s was triggered with argument ${OPTARG}"
        sflag=${OPTARG}
        ;;
    q)
        echo "Option -q was triggered with argument ${OPTARG}"
        qflag=${OPTARG}
        ;;
    f)
        echo "Option -f was triggered with argument ${OPTARG}"
        fflag=${OPTARG}
        ;;
    h)
        usage
        ;;
    esac
done

if [[ -n "$sflag" && ! -n "$qflag" ]]; then
    new_file=$(rename $fflag "s")
    # Modify sform_code and overwrite file
    nifti_tool -mod_hdr -mod_field sform_code "$sflag" -infiles "$fflag" -prefix "$new_file"
fi

if [[ ! -n "$sflag" && -n "$qflag" ]]; then
    new_file=$(rename $fflag "q")
    # Modify sform_code and overwrite file
    nifti_tool -mod_hdr -mod_field sform_code "$sflag" -infiles "$fflag" -prefix "$new_file"
fi

if [[ -n "$sflag" && -n "$qflag" ]]; then
    new_file=$(rename $fflag "s_q")
    # Modify sform_code and overwrite file
    nifti_tool -mod_hdr -mod_field sform_code "$sflag" -infiles "$fflag" -prefix "$new_file"
fi

if [[ ! -n "$sflag" && ! -n "$qflag" ]]; then
    # Modify sform_code and overwrite file
    nifti_tool -mod_hdr -mod_field sform_code "$sflag" -infiles "$fflag" -prefix "$new_file"
fi




