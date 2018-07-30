#!/usr/bin/env bash

CAMKII=18
PP1=1000
NVOXELS=12
CA=80e-6
L=15e-9
SIMTIME=0.2
D=1e-16

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
../analyze.py -i ${OUTFILE}
