import argparse
import sys
import pkgutil


import nikol.main.commander

class Commander:
    """Commander: parse arguments and dispatch commands
    """
    def __init__(self, app):
        self.app = app
        
        # parser
        self.parser = argparse.ArgumentParser(prog=self.app.program)
        self.parser._positionals.title = 'commands'
        self.parser.set_defaults(command='help')
        #self.parser.add_argument('command', type=str)
        self.parser.add_argument('--version', action='store_true')
        self.subparsers = self.parser.add_subparsers(help='')
        
    def parse_args(self, argv):
        # -h|--help are dispatched by parse_args 
        # and exit the program immediately
        #
        # parses only known arguments.
        # 
        # unknown arguments (-x|--xargs) are exptected to be processed by the
        # ComplexCommand object

        self._check_argv_and_register_commands(argv)

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

        
    def _check_argv_and_register_commands(self, argv):
 
        # nikol xxx ... => register nikol.main.command.xxx
        #
        if len(argv) > 0 and not argv[0].startswith('-'):
            command = argv[0]
            try: 
                mod = __import__('nikol.main.command.' + command, fromlist=[''])
                mod.register(self)
            except ModuleNotFoundError:
                self.print_help()
        
    def print_help(self):

        modules = pkgutil.iter_modules(nikol.main.command.__path__)
        for module_info in modules:
            mod = __import__('nikol.main.command.' + module_info.name, fromlist=[''])
            mod.register(self)

        self.parser.print_help()
            

        
        

