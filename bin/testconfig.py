#!/usr/bin/env python
"""
This script reads a .ptex2tex.cfg file, finds all the defined
environments, writes out a [names] section with all environments
and thereafter a LaTeX code testing all names. (The code must
be inserted in a document with proper heading and footer.)

The script is useful for testing everything that is defined in a
.ptex2tex.cfg config file.
"""

f = open('.ptex2tex.cfg')
envir_types = []
for line in f:
    if line.startswith('['):
        envir_type = line.strip()[1:-1]
        if envir_type not in ('preprocess', 'inline_code', 'names'):
            envir_types.append(envir_type)
f.close()
names = open('tmp_names', 'w')
index = 1
for e in envir_types:
    names.write('n%d = %s\n' % (index, e))
    index += 1
names.close()
print """
A [names] section is written to the file tmp_names and should
be appended to the .ptex2tex.cfg file in the current directory.
"""

latex = open('tmp_latex', 'w')
for i in range(1, index):
    if envir_types[i-1] in ('Warnings', 'Tip', 'Note'):
        
        latex.write(r"""
\noindent
Here is a demo of the environment '%s':
\bn%d
Some message can be written here as ordinary
text.
\en%d

""" % (envir_types[i-1].replace('_', '\\_'), i, i))
    else:
        latex.write(r"""
\noindent
Here is a demo of the environment '%s':
\bn%d
v0 = 5                    # velocity
g = 9.81                  # acceleration of gravity
t = 0.6                   # time
y = v0*t - 0.5*g*t**2     # vertical position
print y
\en%d

""" % (envir_types[i-1].replace('_', '\\_'), i, i))
latex.close()
print """\
A LaTeX demo code of all environments defined in .ptex2tex.cfg
is written to the file tmp_latex and should be included
in some LaTeX document.
"""
