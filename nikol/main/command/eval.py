""" eval: python eval 
"""

_setup_ = {
    'version' : '0.1.0',
    'description' : 'python eval'
}

import sys
import argparse
from nikol.main.command import SimpleCommand

import math

def init(app):
    return EvalCommand(app)

class EvalCommand(SimpleCommand):
    def __init__(self, app = None, name = 'eval'):
        super().__init__(app, name)
        
        self.parser.add_argument('expression', type=str, nargs='*', help='python expression')
        self.parser.add_argument('--debug', action='store_true', help='print the parsed expression')
        
    def run(self, argv):
        args = self.parser.parse_args(argv)
        if args.debug : print(argv, args.expression)
        print(eval(' '.join(args.expression)))
 
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = EvalCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
