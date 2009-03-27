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
        self.envir_type = ""

    def __str__(self):
        s = ''
        #for attr in self.__dict__:
        #    s += '\n%s:\n%s\n' % (attr, self.__dict__[attr])
        s += '\nname: %s\n' % self.name
        s += '\n    newenv: %s\n' % self.newenv
        return s

    def __repr__(self):
        return self.__str__()
        
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
    supported0 = {}

    sections = config.sections()

    if not 'inline_code' in sections:
        print "section 'inline_code' not found in config file"
        sys.exit(8)
    supported0['inline_code'] = {}
    for option in config.options('inline_code'):
        supported0['inline_code'][option] = config.get('inline_code', option)

    supported0['preprocess'] = {}
    for option in config.options('preprocess'):
        supported0['preprocess'][option] = config.get('preprocess', option)

    # Find all entries in names section:
    if not 'names' in sections:
        print "section 'names' not found in config file"
        sys.exit(6)
        
    names = sections.pop(sections.index('names'))

    # Run through all environment names in the [names] section,
    # find the corresponding environment type and fill in the
    # supported0[envir_name] dict with an Env object with the
    # attributes containing the information in the environment type.
    
    for envir_name in config.options(names):
        key = envir_name
        envir_type = config.get(names, envir_name)
        supported0[envir_name] = Env()
        supported0[envir_name].name = envir_name
        supported0[envir_name].envir_type = envir_type
        if not envir_type in sections:
            print "the environment type '%s' is not defined in the configuration file" % (envir_type)
            sys.exit(7)
        for option in config.options(envir_type):
            curdict = supported0[envir_name].__dict__                    
            if not hasattr(supported0[envir_name], option):
                print "***warning: unknown option '%s' in environment '%s' " % \
                      (option, envir_type)
            if option == 'define':
                curdict.update({option: config.getboolean(envir_type, option)})
            else:
                curdict.update({option: config.get(envir_type, option)})

    supported = {}
    for key in supported0:
        Env_instance = supported0[key]
        if key == 'inline_code' or key == 'preprocess':
            supported[key] = supported0[key]
            continue

        envir_name = Env_instance.name
        try:
            supported[key] = (Env_instance,
                              '\\' + 'b' + envir_name,
                              '\\' + 'e' + envir_name)
        except:
            print "error in environment " + key
            sys.exit(4)

    # check that newenvironment names are different:
    newenvir_names = []
    newenvir_types = []
    exceptions = ('shadedwbar',)
    import re
    c = re.compile(r'renewenvironment\{(.+?)\}', re.DOTALL)
    for key in supported:
        if key == 'inline_code' or key == 'preprocess':
            continue

        #print 'envir "%s" points to [%s]' % (key, supported[key][0].envir_type)
        newenv = supported[key][0].newenv
        if newenv:
            all = c.findall(newenv)
            if all:
                for e in exceptions:
                    if e in all:
                        all.remove(e)
                for name in all:
                    #print 'Found', name
                    # is this environment name defined before?
                    if name in newenvir_names:
                        envir_type = supported[key][0].envir_type
                        #print 'Found %s in [%s]' % (name, envir_type)
                        other_envir_type = newenvir_types[newenvir_names.index(name)]
                        #xoprint 'Found %s in [%s] too' % (name, other_envir_type)
                        if other_envir_type != envir_type:
                            print """
    Error: new latex environment "%s" defined in [%s] in
    configuration file, but this environment is alread defined in [%s].
    Construct another name for "%s" in [%s].""" % \
                            (name, envir_type, other_envir_type, name, envir_type)
                            sys.exit(8)
                    else:
                        newenvir_names.append(name)
                        newenvir_types.append(supported[key][0].envir_type)
            
    
    return supported
