import argparse
import sys

class Commander:
    """Commander: parse arguments and dispatch commands
    """
    def __init__(self, app):
        self.app = app
        
        # parser
        self.parser = argparse.ArgumentParser(prog=self.app.program)
        self.parser._positionals.title = 'commands'
        self.parser.set_defaults(command='help')
        self.parser.add_argument('--version', action='store_true')
        self._register_commands()
        
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
            mod = __import__('nikol.main.command.' + args.command, fromlist=[''])
            mod.run(self.app, args)

    def print_version(self):
        print(self.app.program, 'version', self.app.version)

    def _register_commands(self):
        
        self.subparsers = self.parser.add_subparsers(help='')

        # help
        help_parser = self.subparsers.add_parser('help', help='print help')
        help_parser.set_defaults(command='help')
        
        # please
        please_parser = self.subparsers.add_parser('please', help='toy complex command for the test development')
        please_parser.add_argument('subargv', type=str, nargs=argparse.REMAINDER, help='subargument values')
        please_parser.set_defaults(command='please')


