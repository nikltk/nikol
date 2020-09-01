import sys
import argparse

class Command(object):
    def __init__(self, app, name):
        self.app = app 
        self.name = name
        if self.app is not None:
            progname = self.app.name + ' ' + name
        else:
            progname = name
            
        self.parser = argparse.ArgumentParser(prog=progname)
        
    def run(self, argv):
        pass
        
class SimpleCommand(Command):
    def __init__(self, app = None, name : str = ''):
        super().__init__(app, name)
        
class ComplexCommand(Command):
    """ComplexCommand has its own argument parser to process subcommand and subarguments"""
    
    def __init__(self, app = None, name : str = ''):
        super().__init__(app, name)
        self.subparsers = self.parser.add_subparsers(title='subcommands', help='command help')

    def add_parser(self, *args, **kwargs):
        return self.subparsers.add_parser(*args, **kwargs)
        
    def run(self, argv):
        if len(argv) == 0:
            self.parser.print_help()
        else:
            args = self.parser.parse_args(argv)
            getattr(self, args.func)(args)

    def print_help(self, args):
        self.parser.print_help()
