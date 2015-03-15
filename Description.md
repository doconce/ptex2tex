#### What is Ptex2tex? ####

Ptex2tex is a tool that allows you to replace LaTeX environment declarations
with simple keywords. In a way, Ptex2tex allows you to create LaTeX
packages without any sophisticated knowledge on how to write
LaTeX packages. The idea behind Ptex2tex is code generation: instead
of hiding complicated LaTeX constructions in complex LaTeX
packages, one simply generates the necessary LaTeX commands on the
fly, from a compact begin-end environment indication in the LaTeX
source. This implies that you have to preprocess your LaTeX source
to make an ordinary LaTeX file that can be compiled in the usual way.

The main application of Ptex2tex is for inserting verbatim-style
computer code in LaTeX documents. Code can be copied directly from the
source files of the software (complete files or just snippets), and
output from programs can be created and copied into the documentation
as a part of running Ptex2tex.  This guarantees that your LaTeX
document contains the most recent version of the program code and its
output!

With the default Ptex2tex configuration style, you can switch between
30+ styles for computer code within seconds and just recompile your
LaTeX files.  Even in a several-hundred pages book it takes seconds to
consistently change various styles for computer code, terminal
sessions, output from programs, etc. This means that you never have to
worry about choosing a proper style for computer/verbatim code in your
LaTeX document.  Just use Ptex2tex and leave the decision to the
future. It takes seconds to change your mind anyway.

Read the
[ptex2tex manual](https://ptex2tex.googlecode.com/svn/trunk/doc/ptex2tex_doc.pdf)
for further information and demos.

#### Required Software ####

Ptex2tex requires the following additional software:


  * [preprocess](http://code.google.com/p/preprocess)
  * LaTeX packages: fancyvrb, moreverb, pythonhighlights, minted   (see [styles](https://ptex2tex.googlecode.com/svn/trunk/latex/styles)    in the ptex2tex tree, which include a corrected version of `minted.sty`
  * [pygments](http://pygments.org)