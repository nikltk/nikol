import sys
import argparse

class Command(object):
    def __init__(self, app):
        self.app = app 

    def __call__(self, args):
        self.call(args)
   
class SimpleCommand(Command):
    pass

class ComplexCommand(Command):
    """ComplexCommand has its own argument parser to process subcommand and subarguments"""
    
    def __init__(self, app):
        super().__init__(app)
        self.parser = argparse.ArgumentParser()
        self.parser._positionals.title = 'subcommands'
        self.parser.set_defaults(command='help', func='help_command')
        self.subparsers = self.parser.add_subparsers()
        
    def __call__(self, superargs):
        self.parser.prog = self.app.program + ' ' + superargs.command 
        args = self.parser.parse_args(superargs.subargv)
        getattr(self, args.func)(args)
 
