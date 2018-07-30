#!/usr/bin/env bash

set -e
set -x

DIFFDICT="{ 'x' : 1e-13, 'y' : 1e-13 }"

python ./camkii_pp1_scheme.py --record-dt 20 --num-voxels 2 \
    --enable-subunit-exchange
python ./analyze.py -i ./camkii_pp1_scheme.py.dat
