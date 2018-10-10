all : ./figure_validation_178mm.tex ./model_sbgn_pd.pdf \
    ./camkii_pp1_switch_level1_detail.pdf ./camkii_subunit_exchange.pdf
	lualatex --shell-escape $<

%.pdf : %.tex
	lualatex --shell-escape $<
