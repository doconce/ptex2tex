#!/bin/sh -x
# produce ptex2tex documentation

file=doc

# first make all environments for demo:
cp ../lib/ptex2tex/ptex2tex.cfg .ptex2tex.cfg  # latest config file
python ../bin/testconfig.py
mv -f tmp_latex envir_demo.tex
cat tmp_names >> .ptex2tex.cfg
rm tmp_names

ptex2tex $file
latex -shell-escape $file
latex -shell-escape $file
dvipdf $file
mv -f doc.pdf ptex2tex_doc.pdf
echo
echo "Documentation in ptex2tex_$file.pdf"

# googlecode wiki:
doconce format gwiki brief.do.txt



