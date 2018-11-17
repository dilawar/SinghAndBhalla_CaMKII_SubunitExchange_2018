all : figure_summary.pdf ./brain_switches.pdf

%.pdf : %.tex
	lualatex --shell-escape $<
