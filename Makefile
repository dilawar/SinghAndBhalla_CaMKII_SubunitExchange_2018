CONVERT:=ln -f
all :  paper

paper : ./CaMKII_Paper_2018-elife.pdf images

./CaMKII_Paper_2018-elife.pdf : ./CaMKII_Paper_2018-elife.tex
	latexmk -pdf -pdflatex=lualatex -silent -latexoption="-shell-escape"  $<

images: elifeFigure1.pdf elifeFigure2.pdf elifeFigure3.pdf \
	elifeFigure4.pdf elifeFigure5.pdf elifeFigure6.pdf \
	elifeFigure7.pdf elifeFigure8.pdf  \
	elifeFigure4_supp1.pdf elifeFigure8_supp1.pdf \
	elifeFigureSI1.pdf elifeFigureSI2.pdf 

elifeFigure1.pdf:   ./PaperFigures/elifeFigure1/figure_validation_178mm.pdf
	$(CONVERT) $< $@

elifeFigure2.pdf:   ./PaperFigures/elifeFigure2/figure_effect_of_tolerace_140mm.pdf
	$(CONVERT) $< $@

elifeFigure3.pdf:   ./PaperFigures/elifeFigure3/figure_turnover_tolerance_114.pdf
	$(CONVERT) $< $@

elifeFigure4.pdf:   ./PaperFigures/elifeFigure4/figure_camkii_activation_114mm.pdf
	$(CONVERT) $< $@

elifeFigure5.pdf:   ./PaperFigures/elifeFigure5/figure_sync_150mm.pdf
	$(CONVERT) $< $@

elifeFigure6.pdf:   ./PaperFigures/elifeFigure6/figure_two_timecourses_114mm.pdf
	$(CONVERT) $< $@

elifeFigure7.pdf:   ./PaperFigures/elifeFigure7/figure_exchange_rate.pdf
	$(CONVERT) $< $@

elifeFigure8.pdf:   ./PaperFigures/elifeFigure8/figure_su_long_term_effect.pdf
	$(CONVERT) $< $@

elifeFigure4_supp1.pdf : ./PaperFigures/suppl/figure_camkii_activations_trajs.pdf 
	$(CONVERT) $< $@

elifeFigure8_supp1.pdf : ./PaperFigures/suppl/figure_pp1_profile.pdf 
	$(CONVERT) $< $@

elifeFigureSI1.pdf: ./PaperFigures/suppl/figure_diff.pdf
	$(CONVERT) $< $@

elifeFigureSI2.pdf: ./PaperFigures/suppl/figure_bimolecular_reac_rdme.pdf
	$(CONVERT) $< $@

