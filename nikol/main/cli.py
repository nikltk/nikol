"""Nikol command line tool."""

import sys
import os
import subprocess
import argparse
import optparse

import nikol

class App(object):
    def __init__(self, program: str = 'nikol', version = nikol.__version__):
        self.program = program
        self.version = version

        self.critical_failure = False 
        self.errors = []
        self.warnings = []

        self.parser = argparse.ArgumentParser(prog=program)
        
    def run(self, args):
       print(self.program, self.version, args) 
        
    def exit(self):
        """Exits the program. Checks errors and warnings.
        """
        pass


def main(args=None):
    """entry-point for console-script
    """
    if args is None:
        args = sys.argv[1:]

    app = App()
    app.run(args)
    app.exit()
       
if __name__ == '__main__':
    main()

