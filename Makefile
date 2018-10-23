all :  ./CaMKII_Paper_2018-elife.pdf ./CaMKII_Paper_2018.pandoc.pdf

%.pdf : %.tex
	latexmk -lualatex -shell-escape $<

%.pandoc.pdf : %.pandoc
	~/Scripts/md2pdf.sh $<


