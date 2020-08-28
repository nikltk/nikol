import sys
import argparse

class Command(object):
    def __init__(self, app, name):
        self.app = app 
        self.name = name

    def __call__(self, argv):
        self.call(argv)
   
    def run(self, argv):
        self.__call__(argv)
        
class SimpleCommand(Command):
    def __init__(self, app = None, name : str = ''):
        super().__init__(app, name)
        self.parser = argparse.ArgumentParser()
        
    def __call__(self, argv):
        args = self.parser.parse_args(argv)
        self.call(args)

    
class ComplexCommand(Command):
    """ComplexCommand has its own argument parser to process subcommand and subarguments"""
    
    def __init__(self, app = None, name : str = ''):
        super().__init__(app, name)
        # self.parser = argparse.ArgumentParser(prog=self.app.program + ' ' + name)
        self.parser = argparse.ArgumentParser(prog='nikol' + ' ' + name)
        self.parser._positionals.title = 'subcommands'
        self.parser.set_defaults(command='help', func='help_command')
        self.subparsers = self.parser.add_subparsers()

    def add_parser(self, *args, **kwargs):
        return self.subparsers.add_parser(*args, **kwargs)
        
    def __call__(self, argv):
        args = self.parser.parse_args(argv)
        getattr(self, args.func)(args)
 
