#!/usr/bin/env bash
CAMKII=15
PP1=270
SIMTIME=30
DATFILE="data_camkii${CAMKII}_pp1${PP1}.dat"
python ./camkii_pp1_scheme.py --camkii $CAMKII --pp1 $PP1 \
    --simtime $SIMTIME -o $DATFILE --enable-subunit-exchange --record-dt 500
python ./analyze.py -i $DATFILE
