import sys
import argparse

class Command(object):
    def __init__(self, app, name, **kwargs):
        self.app = app 
        self.name = name
        if self.app is not None:
            progname = self.app.name + ' ' + name
        else:
            progname = name

        if 'formatter_class' not in kwargs:
            kwargs['formatter_class'] = argparse.RawDescriptionHelpFormatter
            
        self.parser = argparse.ArgumentParser(prog=progname, **kwargs)
        
    def run(self, argv):
        pass
        
class SimpleCommand(Command):
    def __init__(self, app = None, name : str = '', **kwargs):
        super().__init__(app, name, **kwargs)
        
class ComplexCommand(Command):
    """ComplexCommand has its own argument parser to process subcommand and subarguments"""
    
    def __init__(self, app = None, name : str = '', **kwargs):
        super().__init__(app, name, **kwargs)
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
