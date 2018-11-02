all :  ./CaMKII_Paper_2018-elife.pdf

%.pdf : %.tex
	latexmk -pdf -pdflatex=lualatex -latexoption="-shell-escape" $<

paper :  ./CaMKII_Paper_2018-elife.pdf

