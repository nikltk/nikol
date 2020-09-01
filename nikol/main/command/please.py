"""please: a toy complex command
"""

_setup_ = {
    'description' : 'a toy complex command',
    'version' : '0.1.0'
}

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
        
        sum_parser = self.add_parser('sum', help='sum numbers')
        sum_parser.add_argument('numbers', type=float, nargs='+', help='numbers')
        sum_parser.set_defaults(func='sum')

        config_parser = self.add_parser('config', help='test config')
        config_parser.set_defaults(func='config_command')
        
    def say_command(self, args):
        mod = __import__('nikol.misc.say', fromlist=[''])
        print(mod.say(args.something, args.format))

    def sum(self, args):
        print(sum(args.numbers))

    def config_command(self, args):
        try:
            print(self.app.config)
        except Exception as e:
            sys.exit(str(e))

       
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = PleaseCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
