"""Nikol command line tool.


Variables:

- argv : list of string (from sys.argv[1:])
- args : Namespace object returned (from argparser.ArgumentParser.parse_args())

"""

import sys
import os
import subprocess
import argparse
import configparser

import nikol
from nikol.main import commander

class App(object):
    def __init__(self, program: str = 'nikol', version = nikol.__version__):
        self.program = program
        self.version = version

        self.critical_failure = False 
        self.errors = []
        self.warnings = []

        self.commander = commander.Commander(self)
        
        
    def run(self, argv):
        self.cwd = os.getcwd()
        args = self.commander.parse_args(argv)


        # some commands does not require initialization of the workspace
        # if args.command == 'init_command' or args.command == 'help_command':
        #    pass
        # else:
        #    pass

        self.commander.run(args)

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

