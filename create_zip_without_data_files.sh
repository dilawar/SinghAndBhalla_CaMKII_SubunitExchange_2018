#!/usr/bin/env bash
#git archive \
#    --format=zip -9 --prefix=elife-$(date +"%Y%m%d") \
#    HEAD \
#    -o elife.zip
# git clean -fx .
OUTFILE=elife$(date +"%Y%m%d").zip
zip -r $OUTFILE ./ -x ".git/*" -x "*.dat" -x "*.csv" -x ".git*" -x "\.*" \
    -i "*.pdf" -i "*.tex" -i "*.cls" -i "*.sty" -i "*.bst" -i "*.cls" \
    -i "*.bib"
ls -lh $OUTFILE
