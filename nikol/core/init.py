import os

from .config import Config

class Init:
    def __init__(self, program_name, dirname, config_basename='config'):
        self.program_name = program_name
        self.dirname = dirname
        self.config_basename = config_basename

        #finder = ConfigFinder(program_name, dirname, config_basename)

        self.config_dirname = os.path.join(dirname, '.' + program_name)
        if os.path.exists(self.config_dirname):
            self.__reinitialize()
        else:
            self.__initialize()

    def __reinitialize(self):
        # TODO: implement
        raise Exception('Nikol workspace already exists in ' + self.config_dirname)
       
    def __initialize(self):
       config = Config()
       os.makedirs(self.config_dirname)
       config_filename = os.path.join(self.config_dirname, self.config_basename)
       with open(config_filename, 'w') as configfile:
           config.write(configfile)
       
