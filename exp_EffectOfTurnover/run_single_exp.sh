#!/usr/bin/env bash

set -e -x

SIMTIME=30

CAMKII=10
PP_SU_ON=140
PP_SU_OFF=90

for tr in 30 25 20 15 10 8 5 3 1 0.5 0.1; do
    echo "With turnover rate 1 per $tr hour."
    TURNOVER_RATE=$(echo "1/($tr*3600)" | bc -l)
    DATAFIILE="./data_(camkii=$CAMKII,turnover=${tr},SU=ON).dat"
    python ./camkii_pp1_scheme.py --camkii $CAMKII --pp1 $PP_SU_ON --num-voxels 1  \
        --diff-dict "{ 'x' : 1e-13, 'y' : 1e-13 }" --enable-subunit-exchange \
        --turnover-rate ${TURNOVER_RATE}  \
        --simtime ${SIMTIME} -o $DATAFIILE
    python ../analyze.py -i $DATAFIILE -o $DATAFIILE.png

    DATAFIILE="./data_(camkii=$CAMKII,turnover=${tr},SU=OFF).dat"
    python ./camkii_pp1_scheme.py --camkii $CAMKII --pp1 $PP_SU_OFF \
        --turnover-rate ${TURNOVER_RATE}  \
        --simtime ${SIMTIME} -o $DATAFIILE
    python ../analyze.py -i $DATAFIILE -o $DATAFIILE.png
done
./analyze_exp.py
