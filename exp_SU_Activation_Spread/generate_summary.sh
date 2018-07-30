#!/usr/bin/env bash
set -e
set -x

# NOTE: Run cmake with various values of resting ca concentration. Moves the
# data file to subdirectory e.g. ./DATA_CA_BASAL_100NM etc. After that run this
# script to generate the summary data in each directory.

DIRS=$(find . -name "*DATA_CA_BASAL_*NM" -type d)
for _dir in $DIRS; do
    echo "Analyze $_dir"
    ( 
        cd $_dir
        python ../analyze_exp.py 
        cp summary.png ../${_dir}_summary.png
    )
done
python ./rise_time_vs_ca_level.py
