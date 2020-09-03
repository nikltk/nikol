"""Config handling"""

import configparser
import os.path
import sys

class ConfigFinder(object):
    def __init__(self, program_name: str, cwd: str, config_basename='config'):
        self.program_name = program_name
        self.config_basename = config_basename
        self.cwd = cwd
        self.__global_config_dirname = None
        self.__local_config_dirname = None
        
    @property 
    def global_config_filename(self):
        return os.path.join(self.global_config_dirname, self.config_basename)

    @property
    def global_config_dirname(self):
        if self.__global_config_dirname is None:
            self.__global_config_dirname = self.__find_global_config_dir()
            if not os.path.exists(self.global_config_filename):
                self.__init_global_config_file()
            
        return self.__global_config_dirname
    
    @global_config_dirname.setter
    def global_config_dirname(self, dirname):
        self.__global_config_dirname = dirname
        
    def __find_global_config_dir(self):
        """Finds global (i.e. user) config file.
        
              - `~/program_name/config` if Windows
              - `~/.config/program_name/config` if other system

        If not exists, initialize one. 
        """
        if sys.platform.startswith("win") or (sys.platform == "cli" and os.name == "nt"):
            config_home_dirname = os.path.expanduser("~")
        else:
            config_home_dirname = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            if not os.path.exists(config_home_dirname):
                os.makedirs(config_home_dirname)
            
        config_dirname = os.path.join(config_home_dirname, self.program_name)
        if not os.path.exists(config_dirname):
            os.makedirs(config_dirname)
    
        return config_dirname

    def __init_global_config_file(self):
        """Initialize the global (i.e. user) config file.
        """
        config = Config()
        with open(self.global_config_filename, 'w') as configfile:
            config.write(configfile)
        
    @property
    def local_config_filename(self):
        filename = os.path.join(self.local_config_dirname, self.config_basename)
        if os.path.exists(filename):
            return filename
        else:
            raise OSError
    
    @property
    def local_config_dirname(self):
        if self.__local_config_dirname is None:
            self.__local_config_dirname = self.__find_local_config_dir()

        return self.__local_config_dirname

    @local_config_dirname.setter
    def local_config_dirname(self, dirname):
        self.__local_config_dirname = dirname
        
    def __find_local_config_dir(self):
        """Find `.program_name` directory. Iterate recursively the parents of the
        current working directory up to the root.

        """
        config_dirname = '.' + self.program_name
        curdir = self.cwd
        while True:
            dotdirpath = os.path.join(curdir, config_dirname)
            
            ## if .program_name found
            if os.path.exists(dotdirpath):
                break
            
            pardir = os.path.realpath(os.path.join(curdir, os.pardir))
    
            ## if .program_name not found
            if pardir == curdir:
                raise OSError
            else:
                curdir = pardir
    
        return dotdirpath
    
class Config(configparser.ConfigParser):
    def __init__(self,
                 program_name: str = None,
                 cwd: str = None,
                 config_basename: str = 'config',
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        if program_name is not None and cwd is not None:
            self.finder = ConfigFinder(program_name, cwd, config_basename)
            self.read(self.finder.global_config_filename)
            self.read(self.finder.local_config_filename)
            
        self.__local_config = None
        self.__global_config = None
        
    @property
    def local_config(self):
        if self.__local_config is None:
            self.__local_config = configparser.ConfigParser()
            self.__local_config.read(self.finder.local_config_filename)

        return self.__local_config

    @property
    def global_config(self):
        if self.__global_config is None:
            self.__global_config = configparser.ConfigParser()
            self.__global_config.read(self.finder.global_config_filename)

        return self.__global_config
        
    def set_local(self, section, option, value): 
        try:
            self.__update_local_config_file('set', section, option, value)
        except configparser.NoSectionError:
            self.__update_local_config_file('add_section', section)
            self.__update_local_config_file('set', section, option, value)
            
    def set_global(self, section, option, value):
        try:
            self.__update_global_config_file('set', section, option, value)
        except configparser.NoSectionError:
            self.__update_global_config_file('add_section', section)
            self.__update_global_config_file('set', section, option, value)
        
    def __update_local_config_file(self, func: str, *args):
        self.__update_config_file(self.finder.local_config_filename, func, *args)
        
    def __update_global_config_file(self, func: str, *args):
        self.__update_config_file(self.finder.global_config_filename, func, *args)
        
    def __update_config_file(self, config_filename, func: str, *args):
        getattr(self, func)(*args)

        # read target config file 
        config = configparser.ConfigParser()
        config.read(config_filename)

        # update
        getattr(config, func)(*args)
            

        # write target config file
        with open(config_filename, 'w') as configfile:
            config.write(configfile)

       


            
