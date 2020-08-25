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
   
class HelpCommand(SimpleCommand):
    def __call__(self, app):
        self.app.commander.parser.print_help()
        
class PleaseCommand(ComplexCommand):
    def __init__(self, app):
        super().__init__(app)

        help_parser = self.subparsers.add_parser('help', help='print help')
        help_parser.set_defaults(command='help', func='help_command')
        
        say_parser = self.subparsers.add_parser('say', help='say something')
        say_parser.add_argument('something', type=str, nargs='*', help='something')
        say_parser.add_argument('-f', '--format', type=str, default='text/plain', help='format')
        say_parser.set_defaults(command='say', func='say_command')

    def help_command(self, args):
        self.parser.print_help()

    def say_command(self, args):
        mod = __import__('nikol.misc.say', fromlist=[''])
        print(mod.say(args.something, args.format))

       

class Commander:
    """Commander: parse arguments and dispatch commands
    """
    def __init__(self, app):
        self.app = app
        
        # parser
        self.parser = argparse.ArgumentParser(prog=self.app.program)
        self.parser._positionals.title = 'commands'
        self.parser.set_defaults(command='help', commandClass='HelpCommand')
        self.parser.add_argument('--version', action='store_true')
        self._register_subparsers()
        
    def parse_args(self, argv):
        # -h|--help are dispatched by parse_args 
        # and exit the program immediately
        #
        # parses only known arguments.
        # 
        # unknown arguments (-x|--xargs) are exptected to be processed by the
        # ComplexCommand object
        args, argv = self.parser.parse_known_args(argv)
        return args

    def run(self, args):
        if args.version:
            self.print_version()
        else:
            getattr(sys.modules[__name__], args.commandClass)(self.app)(args)

    def print_version(self):
        print(self.app.program, 'version', self.app.version)

    def _register_subparsers(self):
        
        self.subparsers = self.parser.add_subparsers(help='')

        # help
        help_parser = self.subparsers.add_parser('help', help='print help')
        help_parser.set_defaults(command='help', commandClass='HelpCommand')
        
        # please
        please_parser = self.subparsers.add_parser('please', help='toy complex command for the test development')
        please_parser.add_argument('subargv', type=str, nargs=argparse.REMAINDER, help='subargument values')
        please_parser.set_defaults(command='please', commandClass='PleaseCommand')

