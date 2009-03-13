import glob, os, sys, re, shutil
import ConfigParser

def doc():
    return """
Short description of use for envs/__init__.py, part of the ptex2tex package
==================================================================

New environments are added by creating an instance of
class Env and replacing the attributes.

The following variables are inharited:
self.fontsize
self.bstretch
self.margin

fontsize and margin are defined by commandline arguments at runtime.
bstretch is set depending on fontsize. 
Commandline arguments for new classes are automaticaly available,
run 'ptex2tex -h' to view them.

The commandline arguments result in the following strings:
# fontsize :
#            tiny   = fontsize{7pt}{7pt}\selectfont
#            small  = fontsize{9pt}{9pt}\selectfont
#            normal = footnotesize
# bstretch :
#            tiny   = 0.6
#            small  = 0.85
#            normal = 0.85
# margin is not used for the time being

The functions breplace(self) and ereplace(self) return the
LaTeX code we want to replace the keywords with.

If the file '.ptex2tex' exists in the directory where the .p.tex file
resides, additional environments can be defined in that file.
Also, existing environments can be overwritten by defining them again.
If the file does not exist, it is copied.
"""

__doc__ = doc()

class Env(object):
    """Class for the different environments. All environments are instances
    of this class with the attributes replaced."""
    # fontsize :
    #            tiny   = fontsize{7pt}{7pt}\selectfont
    #            small  = fontsize{9pt}{9pt}\selectfont
    #            normal = footnotesize
    # bstretch :
    #            tiny   = 0.6
    #            small  = 0.85
    #            normal = 0.85
    # define   :
    #            True   = Define environment once every file
    #            False  = Assumes environment defined externally
    def __init__(self):
        """Sets default values for attributes."""
        self.fontsize = "footnotesize"
        self.bstretch = "0.85"
        self.name = ""
	self.env = r'{Verbatim}'
        self.newenv = ""
        self.breplace = ""
        self.ereplace = ""
        self.define = True
        
def envs(dirname):
    """Function for finding all valid environments, defined in the users
    home directory (.ptex2tex.cfg). If this file doesn't exist, it is copied
    there when ptex2tex is invoked. If a local .ptex2tex.cfg exists 
    (in the directory where the .p.tex file resides), any options here will be 
    added. Existing options will be overridden. Returns a dict where the keys are the
    codes for the classes, and the values are a tuple consisting of an instance
    of the class, as well as the begin and end codes. All files follow the
    ConfigParser (.cfg) style."""

    cfgfile = os.path.join(os.path.join(dirname, '.ptex2tex.cfg'))
    if os.path.isfile(cfgfile):
        print 'found local config file'

    homecfgfile = os.path.join(os.path.expanduser('~'), '.ptex2tex.cfg')
    if not os.path.isfile(homecfgfile):
        print 'copying .ptex2tex.cfg to %s' %(os.path.expanduser('~'))
        shutil.copy(os.path.join(os.path.dirname(__file__), os.pardir, 'ptex2tex.cfg'),
                    homecfgfile)
    
    cfgfiles = [homecfgfile, cfgfile]
    config = ConfigParser.SafeConfigParser()
    config.read(cfgfiles)
    supported = {}
    sections = config.sections()
    if not 'names' in sections:
        print "section 'names' not found in config file"
        sys.exit(6)
    name = sections.pop(sections.index('names'))
    for option in config.options(name):
        key = option
        value = config.get(name, key)
        supported[key] = Env()
        supported[key].name = key
        if not value in config.sections():
            print "unknown environment '%s'" %(value)
            sys.exit(7)
        for option in config.options(value):
            curdict = supported[key].__dict__                    
            if not hasattr(supported[key], option):
                print "***warning: unknown option '%s'" %(option)
            if option == 'define':
                curdict.update({option: config.getboolean(value, option)})
            else:
                curdict.update({option: config.get(value, option)})
            
    for key, value in supported.items():
        code = value.name
        try:
            supported[key] = (value, '\\' + 'b' + code, '\\' + 'e' + code)
        except:
            print "error in environment " + key
            sys.exit(4)
    return supported
