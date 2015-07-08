#!/bin/bash
# Tests embedding vistrails results and graphs in latex
# This compiles the latex file and tests if the pdf has the expected size

if pdflatex -shell-escape -halt-on-error head.tex; then
  echo done generating pdf
else
  echo error generating pdf
  exit 1
 fi

pdfsize=$(wc -c < "head.pdf")
echo pdf size is $pdfsize
if [ $pdfsize -le 360000 ]; then
  echo Error: pdf size too small. One of the figures are probably missing.
  exit 2;
else
  echo pdf looks good!
fi

exit 0
