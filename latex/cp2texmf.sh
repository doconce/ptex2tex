#!/bin/sh

# Copies latex style files and other required files to
# ~/texmf/tex/latex/misc on a Linux machine

dir=$HOME/texmf/tex/latex/misc
if [ ! -d $dir ]; then
    mkdir -p $dir
fi

cp ptex2tex.sty styles/*.sty styles/with_license/*.sty note.eps note.fig warning.eps warning.fig tip.eps tip.fig $dir

# Update tex style files
cd $HOME/texmf
mktexlsr .

# More styles are needed (e.g., moreverb.sty)
#sudo apt-get install texlive-latex-extra
