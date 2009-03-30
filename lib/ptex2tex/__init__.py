#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['__doc__']

import sys, os, re, shutil, string, glob, commands
from optparse import OptionParser
import ptex2tex.envs as envs

code_statement = "@@@CODE"
data_statement = "@@@DATA"
cmd_statement = "@@@CMD"

def doc():
    return """
Main class for converting from the ptex to the tex format.
A little bit about the statements above starting with '@@@':

code_statement: A line _starting_ with this statement indicates that a file is
to be included in the .tex file. If there is only one arguments after the
statement, the whole file is included. If a second argument is included, it is
splitted with respect to character '@'. If only an expression in front of this
character is given (the character can be skipped, so that only the expression
is given), only the part of the file starting with that argument and ending
with the end of the file is included. If an expression after the character is
given as well, the part of the file starting with the first expression and
ending at the beginning of the second expression is included. This means that
the include part ends before the text in the second expression, hence that text
is NOT included. When searching the file, the first occurence of the start
expression is used, and the first occurence of the stop expression AFTER the
start expression. This allows for usage of a text that exists in the file
before the start expression as well as after, without using the first
one. Whitespaces in front of and at the end of the expressions before and
after '@' are stripped.

If the whole file is included, the environment 'Program' is used. Otherwise,
the environment 'Snippet' is used. An exception here is in the case that a
second '@' is used after stop expression. This indicates that the 'Program'
environment is to be used, instead of 'Snippet'.

It is important to differ between this include statement and the include
statement provided with the preprocessor package. The latter allows us to
include a file by '% #include FILE', but does not set any environment
variables for us, ie. the whole is included as is.

Examples:
@@@CODE IntegrateSine.py
    -> includes the whole file
@@@CODE IntegrateSine.py # Test
    -> includes everything from the first instance of the string '# Test'
@@@CODE IntegrateSine.py # Test @
    -> includes everything from the first instance of the string '# Test'
@@@CODE IntegrateSine.py for i in@sys.exit(1)
    -> includes everything from the first instance of the string 'for i in'
       _up to_ the first instance of 'sys.exit(1)' _after_ 'for i in'.

data_statement:
Exactly the same as code_statement, but a different environment is
used. code_statement is meant to be used with program code, while
data_statement is meant to be used with data files that are not code.

cmd_statement:
A line _starting_ with this statement indicates that we want to include
the output from a shell command with commandline arguments. All text after
the statement is included in the execution, except any statements after
'#'. The character after '#' should be a number indicating whether the
command to be called itself is to be included. '0' omits the commands, all
other values will include it. If not present, the default choice is that
the command _is_ included.

A simple regex is used to allow statements like:
python code/SineEval.py
to be printed as
python SineEval.py
In order to avoid this, the argument after '#' must be set to 2.

Examples:
@@@CMD python code/SineEval.py 'sqrt(2)' 5 # 1
@@@CMD python code/SineEval.py 'sqrt(2)' 5 #1
@@@CMD python code/SineEval.py 'sqrt(2)' 5
    -> the command itself is included with the output without 'code/'
@@@CMD python code/SineEval.py 'sqrt(2)' 5 # 2
@@@CMD python code/SineEval.py 'sqrt(2)' 5 #2
    -> the command itself is included with the output as is
@@@CMD python SineEval.py 'sqrt(2)' 5 #0
@@@CMD python code/SineEval.py 'sqrt(2)' 5 # 0
    -> the command itself is omitted, only the ouput is included.

For now, the environment 'Verb' is used.
"""

class _Ptex2tex:
    __doc__ = doc()
    
    def __init__(self, argv=sys.argv):
        """Reads and sets the commandline arguments."""
        parser = OptionParser()

        # Define temporary files:
        self.file = argv[-1]
        filetype = os.path.splitext(self.file)
        if (filetype[1] == ".tex") and (filetype[0].split('.')[-1] == 'p'):
            self.file = os.path.splitext(filetype[0])[0]
        elif len(os.path.splitext(self.file)[1]) > 0:
            print "extension %s is illegal," %os.path.splitext(self.file)[1],
            print "this script should only be called for .p.tex files"
            sys.exit(1) 
        self.ptexfile = self.file+".p.tex"
        self.preoutfile = self.file+".tmp1"
        self.transfile = self.file+".tmp2"
        self.texfile = self.file+".tex"
        
        parser.add_option('-v', action="store_true", dest="verbose", help='enable debug output')
        
        self.options, self.args = parser.parse_args(argv[1:])
        self.verbose = self.options.verbose
                
        # Returns a dict where the keys are the names of the classes,
        # and the values are a tuple consisting of an instance of the class,
        # as well as the begin and end codes:
        self.supported = envs.envs(os.path.dirname(self.ptexfile))

        # [preprocess] section contains defines/undefines
        # (a list of macro names)
        # and includes, a list of paths. The defines/undefines
        # are translated to a dict with names as keys and True/False values:
        #print 'self.supported:\n'
        #import pprint; pprint.pprint(self.supported)
        self.preprocess = self.supported.pop('preprocess')
        self.preprocess_defines = {}
        if 'defines' in self.preprocess:
            s = self.preprocess['defines']
            for define in s.split(','):
                if define:  # non-empty string
                    self.preprocess_defines[define] = True
        if 'undefines' in self.preprocess:
            s = self.preprocess['undefines']
            for define in s.split(','):
                if define:  # non-empty string
                    # this is not right:
                    #self.preprocess_defines[define] = False
                    # this is the right way to do it (values in
                    # the defines dict are always treated as True :-(
                    if define in self.preprocess_defines:
                        del self.preprocess_defines[define]
        if 'includes' in self.preprocess:
            s = self.preprocess['includes']
            self.preprocess_includes = eval(s)
        else:
            self.preprocess_includes = []
            
        # [inline_code] section has the font item for \code and \emp commands:
        self.inline_code = self.supported.pop('inline_code')
        if not 'font' in self.inline_code:
            print "missing option 'font' in inline code"
            sys.exit(5)

#        # Define some global choices:
#        v = False
#        parser.add_option('-f', default="normal",
#                          choices=["normal","small","tiny"],
#                          help="fontsize, overridden by configuration file")
#        parser.add_option('-m', default=1, choices=['0','1'],
#                          help="margin, overridden by configuration file")
#
#        self.verbose = 0 #Verbosity for debugging
#        if v:
#            print self.options
#
#        self.font = self.options.f
#        self.bstretch, self.fontsize = self.attr(self.font)
#        self.margin = self.options.m
#       
#        # Based on the available environments in the dict, create
#        # commandline argument flags:
#         for key, value in self.supported.items():
#             name = value[0].name
#             fullname = key
#             parser.add_option('--'+name+'f', default=None,
#                               choices=["normal","small","tiny"],
#                               help=key+" fontsize")
#             parser.add_option('--'+name+'m', default=None,
#                                choices=['0','1'], help=key+" margin")
#
#        # Set the correct attributes for all environments,
#        # global attributes overridden if defined for a
#        # specific environment (from commandline argument):
#         for value in self.supported.values():
#             value[0].fontsize = self.fontsize
#             value[0].bstretch = self.attr(self.font)[0]
#             value[0].margin = self.margin
#             font = eval("self.options." + value[0].name + "f")
#             if font is not None:
#                 value[0].fontsize = self.attr(font)[1]
#                 value[0].bstretch = self.attr(font)[0]
#             margin = eval("self.options." + value[0].name + "m")
#             if margin is not None:
#                 value[0].margin = margin
#
#    def attr(self, font):
#        """Defines the fontsize and baselinestretch based on the font input."""
#        if font == "small":
#            return (0.85, r"fontsize{9pt}{9pt}\selectfont")
#        elif font == "tiny":
#            return (0.6, r"fontsize{7pt}{7pt}\selectfont")
#        return (0.85, r"footnotesize")

    def strip(self, text):
        """Remove empty lines, but not single white-spaces.
        But only at the beginning and at the end."""
        lines = text.split('\n')
        startline = 0; stopline = len(lines)
        for i in range(len(lines)):
            if lines[i].strip() > 0:
                startline = i
                break
        lines.reverse()
        for i in range(len(lines)):
            if lines[i].strip() > 0:
                stopline = i
                break
        lines.reverse()
        stopline = len(lines) - stopline
        return '\n'.join(lines[startline:stopline]).strip('\n')
        
    def preprocessor(self):
        """Run the preprocessor command on the file (if available)."""
        if not os.path.isfile(self.ptexfile):
            print "file not found"
            sys.exit(2)
        try:
            import preprocess
        except:
            print 'could not find the preprocess program, skipping preprocessing...'
            open(self.preoutfile, 'w').write(open(self.ptexfile).read())
            return
        print "running preprocessor... ",
        preprocess.preprocess(self.ptexfile, self.preoutfile,
                              defines=self.preprocess_defines,
                              includePath=self.preprocess_includes,
                              force=1)
        print "done"

    def inline_tt(self):
        """Replace the \emp and \code environments with raw latex code."""
        lines = open(self.preoutfile).read()

        # \emp{} commands: replace with \texttt{} and font adjustment
        pattern = re.compile(r'\\emp\{(.*?)\}') #, re.DOTALL)
        if self.inline_code['font'] == 'smaller':
            lines = re.sub(pattern, r'{\smaller\\texttt{\1}\larger{}}', lines)
        else:
            fontsize = int(self.inline_code['font'])
            lines = re.sub(pattern, r'{\\fontsize{%spt}{%spt}\\texttt{\1}}' % (fontsize, fontsize), lines)

        # \code{} commands: replace with \verb!..! and font adjustment
        pattern = re.compile(r'\\code\{(.*?)\\_\\_(.*?)\\_\\_(.*?)\}')#, re.DOTALL)
        lines = re.sub(pattern, r'\code{\1__\2__\3}', lines)
        no_of_backslashes = 5
        for i in range(no_of_backslashes):
            # Handle up to no_of_backslashes in backslash constructions           
            pattern = re.compile(r'\\code\{(.*?)\\([_#%$@])(.*?)\}')#, re.DOTALL)
            lines = re.sub(pattern, r'\code{\1\2\3}', lines)
        pattern = re.compile(r'\\code\{(.*?)\}')  #, re.DOTALL)
        if self.inline_code['font'] == 'smaller':
            lines = re.sub(pattern, r'{\smaller\\verb!\1!\larger{}}', lines)
        else:
            fontsize = int(self.inline_code['font'])
            lines = re.sub(pattern, r'{\\fontsize{%spt}{%spt}\\verb!\1!}' % (fontsize, fontsize), lines)
        
        open(self.preoutfile, 'w').write(lines)

    def include_file(self):
        """Read from preoutfile file and write to transfile. If no include
        statements (statement variable) are found, copy directly to transfile."""
        self.code_statement = code_statement
        self.data_statement = data_statement
        infile = open(self.preoutfile)
        lines = infile.read()
        if lines.find(self.code_statement) < 0 and lines.find(self.data_statement) < 0:
            shutil.copy(self.preoutfile, self.transfile)
            return
        outfile = open(self.transfile, 'w')
        if self.verbose: print self.transfile
        lines = lines.splitlines()
        if self.verbose: print lines
        for line in lines:
            code_found = line.startswith(self.code_statement)
            data_found = line.startswith(self.data_statement)
            if code_found or data_found:
                codefilename = line.split()[1]
                if self.verbose: print codefilename
                try: codefile = open(codefilename)
                except:
                     print "include file %s could not be found" %codefilename
                     sys.exit(2)
                code = codefile.read()
                codeline = string.join(line.split()[2:])
                if self.verbose: print codeline
                if codeline.find('@') < 0:
                    codeline += '@'
                regex = codeline.split('@')
                for i in range(len(regex)):
                    regex[i] = regex[i].strip()
                if self.verbose: print regex
                startexp = None
                whole = False
                if len(regex[0]) > 0:
                    if len(regex) > 2:
                        whole = True
                    startexp = regex[0].strip();
                    startexp = startexp.replace('~', ' ')
                    if len(regex[1].strip()) > 1:
                        stopexp = regex[1]
                        stopexp = stopexp.replace('~', ' ')
		    else:
			stopexp = ""
                    if self.verbose: print startexp, stopexp
                    start = code.find(startexp)
                    while code[start-1] == ' ':
                        start -= 1
                    if start < 0:
                        print "start expression not found for %s" %codefilename
                        print 'will start from the beginning of the file'
                        start = 0
		    if startexp and stopexp:
                        stop = start + code[start:].find(stopexp)
		    else:
			stop = len(code)
                    if stop < 0:
                        print "stop expression not found for %s" %codefilename
                        sys.exit(3)
                    if self.verbose: print start, stop
                    code = code[start:stop].rstrip()
                if self.verbose:
                    print "inserting the following text:"
                    print code
                if startexp and stopexp:
                    if start == 0:
                        regex[0] = 'BOF'
                    insstr = 'from "%s" to "%s"' %(regex[0], regex[1])
                elif startexp:
                    insstr = "from %s to EOF" %regex[0]
                else:
                    insstr = "(everything)"
                print "copying in file %s %s..." %(codefilename, insstr),
                
                if startexp and not whole:
                    if code_found:
                        outfile.write(self.supported['sni'][1]+"\n")
                    elif data_found:
                        outfile.write(self.supported['dsni'][1]+"\n")
                else:
                    if code_found:
                        outfile.write(self.supported['pro'][1]+"\n")
                    elif data_found:
                        outfile.write(self.supported['dat'][1]+"\n")
                outfile.write(self.strip(code))
                if code:
                    if code[-1] is not "\n":
                        outfile.write("\n")
                if startexp and not whole:
                    if code_found:
                        outfile.write(self.supported['sni'][2]+"\n")
                    elif data_found:
                        outfile.write(self.supported['dsni'][2]+"\n")
                else:
                    if code_found:
                        outfile.write(self.supported['pro'][2]+"\n")
                    elif data_found:
                        outfile.write(self.supported['dat'][2]+"\n")
                print "done"
                    
            else:
                outfile.write(line+"\n")
            code_found = False; data_found = False; whole = False
        outfile.close()

    def include_command(self):
        """Function for including output from shell commands."""
        self.statement = cmd_statement
        infile = open(self.transfile)
        lines = infile.read()
        if lines.find(self.statement) < 0:
            return
        outfile = open(self.transfile, 'w')
        lines = lines.splitlines()
        for line in lines:
            if line.startswith(self.statement):
                command = string.join(line.split()[1:])
                if self.verbose: print command
                if len(command.split('#')) > 1:
                    command, include_cmd = command.split('#')
                    include_cmd = include_cmd.strip()
                    # Options:
                    #  0: Command not included
                    #  1: Command included, path stripped
                    #  2: Command included, path not stripped
                    #  3: Command included except for programname, path
                    #     stripped
                    #  4: Command included except for programname, path not
                    #     stripped
                    # Default: 3
                    try:
                        include_cmd = int(include_cmd)
                    except:
                        print "argument after '#' in @@@CMD must be integer"
                    if self.verbose: print include_cmd
                else:
                    include_cmd = 3
                failure, output = commands.getstatusoutput(command)
                if failure:
                    print 'failed to run command', command
                    print output
                    sys.exit(4)
                print "copying in output from %s..." %command.strip(),
                outfile.write(self.supported['sys'][1] + "\n")
                if bool(int(include_cmd)):
                    if include_cmd == 1 or include_cmd == 3:
                        pattern = re.compile(r'\s+.*/')
                        command = re.sub(pattern, ' ', command)
                    if include_cmd == 3 or include_cmd == 4:
                        index = command.strip().find(' ')
                        command = command[index:].strip()
                    outfile.write(command + '\n')
                outfile.write(output + '\n')
                outfile.write(self.supported['sys'][2] + "\n")
                print "done"
            else:
                outfile.write(line + '\n')
        outfile.close()

    def convert(self):
        """Function for converting from ptex to tex."""
        infile = open(self.transfile)
        outfile = open(self.texfile, 'w')
        block = infile.read()
        lines = block.splitlines()
        # Use the instances of the environments:
        sorted_keys = self.supported.keys()
        sorted_keys.sort()
        sorted_keys.reverse()
        for key in sorted_keys:
            value = self.supported[key]
            obj = value[0]
            for i in range(len(lines)):
                if lines[i].startswith(value[1]):
                    if obj.define:
                        lines[i] = lines[i].replace(value[1], obj.newenv + value[1])
                        obj.define = False
                    lines[i] = lines[i].replace(value[1], obj.breplace)
                elif lines[i].startswith(value[2]):
                    lines[i] = lines[i].replace(value[2], obj.ereplace)
                elif lines[i].strip().startswith(value[1]) or lines[i].strip().startswith(value[2]):
                    self.cleanup = False
                    print '***warning: extra white-space detected, check line %d in %s' %(i, self.transfile)
        block = '\n'.join(lines)
        outfile.write(block)

    def cleanup(self):
        """Function for deleting temporary files."""
        os.remove(self.preoutfile)
        os.remove(self.transfile)

    def run(self):
        """Runs through the different functions necessary to complete the conversion."""
        self.cleanup = True
        self.preprocessor()
        self.inline_tt()
        self.include_file()
        self.include_command()
        self.convert()
        if self.cleanup:
            self.cleanup()

def init(argv=sys.argv):
    instance = _Ptex2tex(argv)
    instance.run()
    print "done\n"

__doc__ = doc()
