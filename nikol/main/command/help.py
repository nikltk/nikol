"""help.py
"""

_setup_ = {
    'description' : 'print help',
    'version' : '0.1.0'
}

import sys
import argparse
from nikol.main.command import SimpleCommand

def init(app):
    return HelpCommand(app)

class HelpCommand(SimpleCommand):
    def __init__(self, app = None, name = 'help'):
        super().__init__(app, name)
        
    def run(self, argv):
        self.app.commander.print_help()
 
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = HelpCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
