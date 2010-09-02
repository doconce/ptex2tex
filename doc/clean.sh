#!/bin/sh
files="*.aux *.dvi *.log *.out *.tmp* tmp* doc.tex *.ps doc.pdf"
echo "removing the following files:"
/bin/ls $files 2> /dev/null
rm -rf $files