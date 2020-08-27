import argparse
from nikol.main.command import ComplexCommand

def register(commander):

    parser = commander.add_command_parser('please', help='toy complex command for the test development')
    parser.add_argument('subargv', type=str, nargs=argparse.REMAINDER, help='subargument values')
    parser.set_defaults(command='please')

def run(app, args):
    PleaseCommand(app)(args)

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

       

