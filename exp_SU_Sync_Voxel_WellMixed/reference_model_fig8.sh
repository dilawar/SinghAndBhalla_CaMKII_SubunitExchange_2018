#!/usr/bin/env bash

CAMKII=6
PP1=80
NVOXELS=1
CA=80e-6
L=180e-9
SIMTIME=10
D=1e-13

OUTFILE=test_CaM-${CAMKII}+PP-${PP1}+N-${NVOXELS}+L-${L}+SU-ON+D-${D}.dat
DIFFDICT="{ 'x' : $D, 'y' : $D, 'PP1' : $D}"
echo "Genrating $OUTFILE"
python3 ./camkii_pp1_scheme.py --camkii $CAMKII --pp1 $PP1 \
    --num-voxels $NVOXELS \
    --voxel-length ${L} \
    --simtime $SIMTIME \
    --enable-subunit-exchange \
    --diff-dict "${DIFFDICT}" \
    --ca-expr "(fmod(t,4)<2)?${CA}:($CA*(1+0.5*rand(-1)))" \
    --outfile ${OUTFILE}
./analyze.py -i ${OUTFILE}
