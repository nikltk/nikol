#
#
#
__doc__ = """please: a toy complex command"""

import sys
import argparse
from nikol.main.command import ComplexCommand

def init(app):
    return PleaseCommand(app)

class PleaseCommand(ComplexCommand):
    def __init__(self, app = None, name = 'please'):
        super().__init__(app, name)

        say_parser = self.add_parser('say', help='say something')
        say_parser.add_argument('something', type=str, help='something')
        say_parser.add_argument('-f', '--format', type=str, default='text/plain', help='format')
        say_parser.set_defaults(func='say_command')
        
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
