#!/usr/bin/env bash
#git archive \
#    --format=zip -9 --prefix=elife-$(date +"%Y%m%d") \
#    HEAD \
#    -o elife.zip
# git clean -fx .
OUTFILE=elife$(date +"%Y%m%d").zip
zip -r $OUTFILE \
    ./CaMKII_Paper_2018-elife.tex \
    ./elife.cls \
    ./glossaries.tex \
    ./bibliography.bib \
    ./elifeFigure*.pdf \
    ./PaperFigures/Makefile
    
ls -lh $OUTFILE
