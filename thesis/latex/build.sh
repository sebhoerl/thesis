cd build
cp ../../../papers/library.bib .
cp -r ../chapters .
cp ../*.tex .
pdflatex thesis.tex
bibtex thesis
pdflatex thesis.tex
pdflatex thesis.tex
cp thesis.pdf ..
