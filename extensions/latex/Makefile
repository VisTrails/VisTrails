all: example example2 head           

example:
	pdflatex -shell-escape example

example2:
	pdflatex -shell-escape example2
	bibtex example2
	pdflatex -shell-escape example2
	pdflatex -shell-escape example2

head: 
	pdflatex -shell-escape head

clean:
	\rm example.pdf example2.pdf head.pdf *.aux *.bbl *.blg *.log *~ *.cmdline *.cmdline.* example.out example2.out head.out
