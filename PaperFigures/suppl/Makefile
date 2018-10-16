all :  figure_pp1_profile.pdf  ./figure_diff.pdf ./ExperimentalDataStrattonELife2016/figure_exchange_rate.pdf

DATFILES := analyze_pp1_detailed.py_summary.dat analyze_pp1_detailed.py_1e-14_summary.dat

$(DATFILES) :  diff_of_pp1_reduces_its_potency_gen_data.sh
	bash $<

plots: $(DATFILES) figure_pp1_profile.pdf

figures : ./figure_pp1_profile.pdf ./figure_bimolecular_reac_rdme.pdf

figure_pp1_profile.pdf : figure_pp1_profile.tex 
	lualatex --shell-escape $<

%.pdf : %.tex
	lualatex --shell-escape $<
