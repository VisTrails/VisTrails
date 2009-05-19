all: example example2            

example:
	pdflatex -shell-escape example

example2:
	pdflatex -shell-escape example2
	bibtex example2
	pdflatex -shell-escape example2
	pdflatex -shell-escape example2

clean:
	\rm example.pdf example2.pdf *.aux *.bbl *.blg *.log *~ *.cmdline *.cmdline.* example.out example2.out
