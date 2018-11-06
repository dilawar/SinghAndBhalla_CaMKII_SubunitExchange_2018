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
    ./PaperFigures/elifeFigure1/figure_validation_178mm.pdf \
    ./PaperFigures/elifeFigure2/figure_effect_of_tolerace_140mm.pdf \
    ./PaperFigures/elifeFigure3/figure_turnover_tolerance_114.pdf \
    ./PaperFigures/elifeFigure4/figure_camkii_activation_130mm.pdf \
    ./PaperFigures/elifeFigure5/figure_sync_114mm.pdf \
    ./PaperFigures/elifeFigure6/figure_two_timecourses_114mm.pdf \
    ./PaperFigures/elifeFigure7/figure_exchange_rate.pdf \
    ./PaperFigures/elifeFigure8/figure_su_long_term_effect.pdf \
    ./PaperFigures/suppl/*.pdf 
    
ls -lh $OUTFILE
