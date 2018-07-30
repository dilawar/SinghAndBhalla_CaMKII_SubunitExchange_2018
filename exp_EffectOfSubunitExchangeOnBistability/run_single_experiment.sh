#!/usr/bin/env bash

# CaMKII and PP1 are distributed among NUMVOXELS.
RECORD_DT=10
DIFFDICT="{ 'x' : 5e-13, 'y' : 5e-13, 'PP1' : 1e-13 }"
SIMTIME=30

CAMKII=12
NUMVOXELS=1

n=0
MAXJOBS=8
for FRAC in $(seq 1 1 30); do
    PP1=$((FRAC*CAMKII))
    outfile="CaM${CAMKII}_PP${PP1}_voxels${NUMVOXELS}_suOFF.dat"
    python ../camkii_pp1_scheme.py --camkii $CAMKII --pp1 $PP1 \
        --simtime $SIMTIME \
        --record-dt $RECORD_DT \
        --num-voxels $NUMVOXELS \
        -o ${outfile} && python ../analyze.py -i ${outfile} &

    outfile="CaM${CAMKII}_PP${PP1}_voxels${NUMVOXELS}_suON.dat"
    python ../camkii_pp1_scheme.py --camkii $CAMKII --pp1 $PP1 \
        --simtime $SIMTIME \
        --record-dt $RECORD_DT \
        --diff-dict "$DIFFDICT" \
        --num-voxels $NUMVOXELS --enable-subunit-exchange  \
        -o ${outfile} && python ../analyze.py -i ${outfile} &

    # limit jobs
    if (( $(($((++n)) % $MAXJOBS)) == 0 )) ; then
        wait 
        echo $n wait
    fi
done

echo "Generating distributions of mid-states"
python ./generate_figure.py 'CaM${CAMKII}*_processed.dat'
