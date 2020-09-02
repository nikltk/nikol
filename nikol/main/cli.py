"""Nikol command line tool.


Variables:

- argv : list of string (from sys.argv[1:])
- args : Namespace object returned (from argparser.ArgumentParser.parse_args())

"""

import sys
import os
import subprocess
import argparse

import nikol
from nikol.main import commander
from nikol.core.config import Config, ConfigFinder


class App(object):
    def __init__(self, name: str = 'nikol', version = nikol.__version__):
        self.name = name
        self.version = version

        self.critical_failure = False 
        self.errors = []
        self.warnings = []

        self.cwd = os.getcwd()
        
        self.commander = commander.Commander(self)

        self.__config = None

    @property
    def config(self):
        if self.__config is None:
            try:
                self.__config = Config(self.name, self.cwd)
            except:
                raise Exception('fatal: not a nikol workspace (or any of the parent directories): .nikol')
            
        return self.__config
        
    def run(self, argv=[]):
        self.commander.run(argv)

    def exit(self):
        """Exits the program. Checks errors and warnings.
        """
        pass


def main(argv=None):
    """entry-point for console-script
    """
    if argv is None:
        argv = sys.argv[1:]

    app = App()
    app.run(argv)
    app.exit()
       
if __name__ == '__main__':
    main()

