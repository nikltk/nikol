# commander.py
#
# command center
#
import argparse
import sys
import pkgutil

class Commander:
    """Commander: parse arguments and dispatch commands
    """
    def __init__(self, app):
        self.app = app
        
        # parser
        self.parser = argparse.ArgumentParser(prog=self.app.name, add_help=False)
        self.parser._positionals.title = 'commands'
        self.parser.set_defaults(command='help')                     # nikol
        self.parser.add_argument('--help', action='store_true')      # nikol --help
        self.parser.add_argument('--version', action='store_true')   # nikol --version
        self.subparsers = self.parser.add_subparsers(title='commands', help='command help')
        
    def parse_args(self, argv):

        # check argv and register commands
        # nikol xxx ... => register nikol.main.command.xxx
        #
        if len(argv) > 0 and not argv[0].startswith('-'):
            command = argv[0]
            try: 
                mod = __import__('nikol.main.command.' + command, fromlist=[''])
                try:
                    self.add_command_parser(command, help=mod._setup_['description'])
                except AttributeError:
                    self.add_command_parser(command)
            except ModuleNotFoundError:
                sys.exit("nikol: '{}' is not a nikol command. See 'nikol --help'".format(command))
 
        # Use parse_known_args() to pass -h|--help option to the subparsers.
        # parse_args() takes -h|--help and immediately print help and exit the
        # program.
        args, argv = self.parser.parse_known_args(argv)   # pass -h|--help
        
        return args
            
    def run(self, argv):

        args = self.parse_args(argv)

        if args.help:
            self.print_help()
        elif args.version:
            self.print_version()
        elif args.command == 'help' and not hasattr(args, 'subargv'):
            self.print_help()
        else:
            mod = __import__('nikol.main.command.' + args.command, fromlist=[''])
            command = mod.init(self.app)
            command.run(argv[1:]) # args.subargv

    def add_command_parser(self, command: str, help: str = ''):
        """
        Add a subparser for `nikol <command>`. For example, `nikol please`
        ```
        commander.add_command_parser('please', help='please command')
        ```
        """
        subparser = self.subparsers.add_parser(command, help=help, add_help=False)

        # prevent parsing subarguments
        subparser.add_argument('subargv', type=str, nargs=argparse.REMAINDER)
        subparser.set_defaults(command=command)
        
        return subparser

    def print_version(self):
        print(self.app.name, 'version', self.app.version)

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
                try:
                    self.add_command_parser(module_info.name, help=mod._setup_['description'])
                except AttributeError:
                    self.add_command_parser(module_info.name)

       
        
        

