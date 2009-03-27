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
index = 1
for e in envir_types:
    print 'n%d = %s' % (index, e)
    index += 1
print '\n\n\n'

for i in range(1, index):
    print r"""
\noindent
Here is environment %s:
\bn%d
v0 = 5
g = 9.81
t = 0.6
y = v0*t - 0.5*g*t**2
print y
\en%d
""" % (envir_types[i-1].replace('_', '\\_'), i, i)
