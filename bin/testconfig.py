#!/usr/bin/env python
"""
This script reads a .ptex2tex.cfg file, finds all the defined
environments, writes out a [names] section with all environments
and thereafter a LaTeX code testing all names. (The code must
be inserted in a document with proper heading and footer.)

The script is useful for testing everything that is defined in a
.ptex2tex.cfg config file.
"""
import sys

snippets = {
'smallpy': r'''
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
# Here is some short Python code

def height_and_velocity(t, v0):
    """Invoke some advanced math computations."""
    g = 9.81                  # acceleration of gravity
    y = v0*t - 0.5*g*t**2     # vertical position
    v = v0 - g*t              # vertical velocity
    return y, v

print height_and_velocity(initial_velocity=0.5, time=1)
\en%d

''',

'Python': r'''
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
# Here is some Python code

def height_and_velocity(t, v0):
    """Invoke some advanced math computations."""
    g = 9.81                  # acceleration of gravity
    y = v0*t - 0.5*g*t**2     # vertical position
    v = v0 - g*t              # vertical velocity
    return y, v

class Wrapper:
    def __init__(self, func, alternative_kwarg_names={}):
        self.func = func
        self.help = alternative_kwarg_names

    def __call__(self, *args, **kwargs):
        # Translate possible alternative keyword argument
        # names in kwargs to those accepted by self.func:
        func_kwargs = {}
        for name in kwargs:
            if name in self.help:
                func_kwargs[self.help[name]] = kwargs[name]
            else:
                func_kwargs[name] = kwargs[name]

        return self.func(*args, **func_kwargs)

height_and_velocity = Wrapper(height_and_velocity,
                              {'time': 't',
                               'velocity': 'v0',
                               'initial_velocity': 'v0'})

print height_and_velocity(initial_velocity=0.5, time=1)
\en%d

''',

'box': r"""
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
Some message can be written here as ordinary
text.
\en%d

""",

'Cpp': r"""
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
# Here is some C++ code

void height_and_velocity(double& y, double& v,
                         double t, double v0)
{
    /*
    Invoke some advanced math computations.
    */
    double g = 9.81;               // acceleration of gravity
    y = v0*t - 0.5*g*pow(t,2);     // vertical position
    v = v0 - g*t;                  // vertical velocity
}

double initial_velocity = 0.5;
double time = 0.6;
double velocity, height;

height_and_velocity(height, velocity, time, initial_velocity);
\en%d
""",

'C': r"""
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
# Here is some C code

double initial_velocity, time, velocity, height;

void height_and_velocity(double* y, double* v,
                         double t, double v0)
{
    /*
    Invoke some advanced math computations.
    */
    double g = 9.81;                /* acceleration of gravity */
    *y = v0*t - 0.5*g*pow(t,2);     /* vertical position */
    *v = v0 - g*t;                  /* vertical velocity */
}

height_and_velocity(&height, &velocity, 0.5, 0.143);
\en%d
""",

'Fortran': r"""
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
C Here is some Fortran 77 code

       program ball
       real*8 v0, time, v, h
       v0 = 0.5
       time = 0.6
       call hgtvel(h, v, time, v0)

       subroutine hgtvel(y, v, t, v0)
       real*8 y, v, t, v0
C      Invoke some advanced math computations
       real*8 g
       g = 9.81
C      height:
       y = v0*t - 0.5*g*t**2
C      velocity:
       v = v0 - g*t
\en%d
""",
'Cython': r'''
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
# Here is some Cython code

cpdef height_and_velocity(double t, double v0):
    """Invoke some advanced math computations."""
    cdef float g = 9.81                  # acceleration of gravity
    cdef float y = v0*t - 0.5*g*t**2     # vertical position
    cdef float v = v0 - g*t              # vertical velocity
    return y, v

class Wrapper:
    def __init__(self, func, alternative_kwarg_names={}):
        self.func = func
        self.help = alternative_kwarg_names

    def __call__(self, *args, **kwargs):
        # Translate possible alternative keyword argument
        # names in kwargs to those accepted by self.func:
        func_kwargs = {}
        for name in kwargs:
            if name in self.help:
                func_kwargs[self.help[name]] = kwargs[name]
            else:
                func_kwargs[name] = kwargs[name]

        return self.func(*args, **func_kwargs)

height_and_velocity = Wrapper(height_and_velocity,
      {'time': 't', 'velocity': 'v0', 'initial_velocity': 'v0'})

print height_and_velocity(initial_velocity=0.5, time=1)
\en%d
''',

'Bash': r'''
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
#!/bin/bash
files=$@

for file in $files; do
  echo $file
  cp $file subdir
done
\en%d
''',

'Matlab': r'''
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
function ball_volume_monte_carlo (dim_num, seed)
  n_log2_max = 24;

  timestamp();
  fprintf(1, '\n');
%%
%%  Get the spatial dimension:
%%
  for n_log2 = 0 : n_log2_max
    if (n_log2 == 0)
      quad = 0.0;
      n_more = 1;
      n = 0;
    elseif (n_log2 == 1)
      n_more = 1;
    else
      n_more = 2*n_more;
    end

    [ x, seed ] = mat_uniform_01(dim_num, n_more, seed);
  end
  return
end
\en%d
''',

'Swig': r'''
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
/* file: hw.i */
%%module hw
%%{
/* include C++ header files necessary to compile the interface */
#include "hw.h"
%%}

%%include "typemaps.i"
%%apply double *OUTPUT { double* s }
%%apply double *OUTPUT { double& s }
%%include "hw.h"
\en%d
''',

# Generated code
'gencode': r'''
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
static PyObject *_wrap_hw1(PyObject *self, PyObject *args) {
    double arg1, arg2, result;

    if (!PyArg_ParseTuple(args, "dd:hw1", &arg1, &arg2)) {
        return NULL;  /* wrong arguments provided */
    }
    result = hw1(arg1, arg2);
    return Py_BuildValue("d", result);
}
\en%d
''',

'UFL': r'''
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
V = FunctionSpace(mesh, 'Lagrange', 3)
u = TrialFunction(V)
v = TestFunction(V)
a = inner(nabla_grad(u), nabla_grad(v))*dx
f = Constant(1)
L = f*dx
\en%d
''',

'Output': r'''
\noindent
Here is a demo of the environment \code{%s}:
\bn%d
i= 1:  0.916752431  1.234526111
i= 2:  2.128967564  2.098176522
i= 3:  4.987856451  0.121212220
i= 4:  1.908716711  1.090896756
i= 5:  2.129872431  2.217826712
i= 6:  2.916777431  8.182726252
\en%d
''',

}

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
    envir = envir_types[i-1]
    if envir in ('Warnings', 'Tip', 'Note'):
        code = snippets['box']
    elif envir in ('CodeRule', 'CodeTerminal'):
        code = snippets['smallpy']
    elif envir.startswith('Minted_'):
        code = snippets[envir[7:]]
    elif envir.endswith('_ANS'):
        code = snippets[envir[:-4]]
    elif envir.endswith('_ANSt'):
        code = snippets[envir[:-5]]
    elif envir.endswith('Tiago'):
        code = snippets[envir[:-5]]
    else:
        code = snippets['Python']

    try:
        code = code % (envir, i, i)
        latex.write(code)
    except ValueError, e:
        print code
        print e
        sys.exit(1)

latex.close()
print """\
A LaTeX demo code of all environments defined in .ptex2tex.cfg
is written to the file tmp_latex and should be included
in some LaTeX document (usually the doc.p.tex documentation
of ptex2tex).
"""
