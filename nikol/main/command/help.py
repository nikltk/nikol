"""print help"""

import sys
import argparse
from nikol.main.command import SimpleCommand

_command = 'help'
_help = 'print help'

def init(app):
    return HelpCommand(app)

class HelpCommand(SimpleCommand):
    def __init__(self, app = None, name = 'help'):
        super().__init__(app, name)
        
    def call(self, args):
        print(args)
        self.app.commander.print_help()
 
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = HelpCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
