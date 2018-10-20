all : ./figure_validation_178mm.pdf 

./figure_validation_178mm.pdf : ./model_sbgn_pd.pdf ./camkii_pp1_switch_level1_detail.pdf \
	./camkii_subunit_exchange.pdf 
	@echo "Built all dependencies"

%.pdf : %.tex
	lualatex --shell-escape $<
