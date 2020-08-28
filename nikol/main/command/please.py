"""please: toy complex command for the test development
"""

import sys
import argparse
from nikol.main.command import ComplexCommand

_command = 'please'
_help = 'toy complex command for the test development'

def init(app):
    return PleaseCommand(app)

class PleaseCommand(ComplexCommand):
    def __init__(self, app = None, name = 'please'):
        super().__init__(app, name)

        help_parser = self.add_parser('help', help='print help')
        help_parser.set_defaults(command='help', func='help_command')
        
        say_parser = self.add_parser('say', help='say something')
        say_parser.add_argument('something', type=str, nargs='*', help='something')
        say_parser.add_argument('-f', '--format', type=str, default='text/plain', help='format')
        say_parser.set_defaults(command='say', func='say_command')

    def help_command(self, args):
        self.parser.print_help()

    def say_command(self, args):
        mod = __import__('nikol.misc.say', fromlist=[''])
        print(mod.say(args.something, args.format))

       
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = PleaseCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
