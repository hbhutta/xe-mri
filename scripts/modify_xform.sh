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

if [[ -n "$sflag" ]]; then
    nifti_tool -mod_hdr -mod_field sform_code "$sflag" -infiles "$fflag"
fi

if [[ -n "$qflag" ]]; then
    nifti_tool -mod_hdr -mod_field qform_code "$qflag" -infiles "$fflag"
fi
