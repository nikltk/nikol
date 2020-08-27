import argparse
import sys
import pkgutil

class Commander:
    """Commander: parse arguments and dispatch commands
    """
    def __init__(self, app):
        self.app = app
        
        # parser
        self.parser = argparse.ArgumentParser(prog=self.app.program, add_help=False)
        self.parser._positionals.title = 'commands'
        self.parser.set_defaults(command='help')                     # nikol
        self.parser.add_argument('--help', action='store_true')      # nikol --help
        self.parser.add_argument('--version', action='store_true')   # nikol --version
        self.subparsers = self.parser.add_subparsers(help='')
        
    def parse_args(self, argv):

        # check argv and register commands
        # nikol xxx ... => register nikol.main.command.xxx
        #
        if len(argv) > 0 and not argv[0].startswith('-'):
            command = argv[0]
            try: 
                mod = __import__('nikol.main.command.' + command, fromlist=[''])
                mod.register(self)
            except ModuleNotFoundError:
                sys.exit("nikol: '{}' is not a nikol command. See 'nikol --help'".format(command))
 
        # parses only known arguments.
        # 
        # unknown arguments (-x|--xargs) are exptected to be processed by the
        # ComplexCommand object
        
        args, argv = self.parser.parse_known_args(argv)
            
        return args

    def run(self, argv):

        args = self.parse_args(argv)

        if args.help:
            self.print_help()
        elif args.version:
            self.print_version()
        else:
            mod = __import__('nikol.main.command.' + args.command, fromlist=[''])
            mod.run(self.app, args)

    def add_command_parser(self, command, help):
        subparser = self.subparsers.add_parser(command, help=help)
        return subparser

    def print_version(self):
        print(self.app.program, 'version', self.app.version)

    def print_help(self):
        self._register_commands()
        self.parser.print_help()

    def _register_commands(self):
        """registers all modules from nikol.main.command to self.subparsers
        """
        pkg = __import__('nikol.main.command', fromlist=[''])
        for module_info in pkgutil.iter_modules(pkg.__path__):
            if module_info.name not in self.subparsers.choices :
                mod = __import__('nikol.main.command.' + module_info.name, fromlist=[''])
                mod.register(self)

       
        
        

