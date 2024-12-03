#!/bin/bash

function usage() {
    cat <<EOF
Usage: $0 [-s <int>] [-q <int>] -infile NII_FILE
This script modifies the sform and/or qform code of the the given NIFTI file.
OPTIONS:
    -f          Field to modify
    -v          Value of the field to modify
    -n          NIFTI file
    -h          Show this message
EOF
}

sflag=
pflag=
fflag=

# getopts usage: getopts optstring name [args]
OPTSTRING="f:v:n:h" # s, q, and f require arguments, but not h
while getopts ${OPTSTRING} opt; do
    case $opt in
    f)
        echo "Option -f was triggered with argument ${OPTARG}"
        field=${OPTARG}
        ;;
    v)
        echo "Option -v was triggered with argument ${OPTARG}"
        value=${OPTARG}
        ;;
    n)
        echo "Option -n was triggered with argument ${OPTARG}"
        file=${OPTARG}
        ;;
    h)
        usage
        ;;
    esac
done

nifti_tool -mod_hdr -mod_field "$field" "$value" -infiles "$file" -overwrite 
echo "Set value of field ${field} to value ${value} in file ${file}"