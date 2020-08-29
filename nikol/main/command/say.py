""" say: a toy simple command
"""

__description__ = 'a toy simple command'
__version__ = '0.1.0'

import sys
import argparse
from nikol.main.command import SimpleCommand

def init(app):
    return SayCommand(app)

class SayCommand(SimpleCommand):
    def __init__(self, app = None, name = 'say'):
        super().__init__(app, name)
        
        self.parser.add_argument('something', type=str, help='something')
        self.parser.add_argument('-f', '--format', type=str, default='text/plain', help='format')
        
    def run(self, argv):
        args = self.parser.parse_args(argv)
        print(args.something)
 
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = SayCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
