all :  ./CaMKII_Paper_2018-elife.pdf

%.pdf : %.tex
	latexmk -lualatex -shell-escape $<


