#!/usr/bin/env python

"""Distutils setup script for 'ptex2tex'."""

import sys, os, shutil, glob
from distutils.core import setup

name = "ptex2tex"
latex = os.path.join('latex', '*.*')
latex_files = glob.glob(latex)

# The next line should probably have a Windows alternative:
latex_dir = os.path.join('share', 'texmf', 'tex', 'latex', name)

data_files = [(latex_dir, latex_files)]

out = setup(name=name,
            version="0.2",
            description="A filter for converting from .p.tex to .tex format",
            author="Ilmar M. Wilbers",
            author_email="ilmarw@simula.no",
            url="http://ptex2tex.googlecode.com",
            license="BSD",
            platforms=["Linux", "Mac OS X", "Unix"],
            keywords=["ptex2tex", "latex"],
            data_files=data_files,
            scripts=[os.path.join("bin", "ptex2tex")],
            package_dir = {'': 'lib'},
            packages=['ptex2tex',
                      os.path.join('ptex2tex', 'envs'),
                      ],
            package_data = {'': ['ptex2tex.cfg']},
            )

try:
    install_data = out.get_command_obj('install').install_data
    if install_data:
        print '\n*** LaTeX style files are located in:'
        print '    %s' %(os.path.join(install_data, latex_dir))
        print '    Please make sure the latex command can'
        print '    locate them, see the README file.'
except:
    print '\n*** Please make sure the latex command can locate'
    print '    the LaTeX style files, see the README file.'
