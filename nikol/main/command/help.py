import argparse
from nikol.main.command import SimpleCommand


def register(commander):
    help_parser = commander.add_command_parser('help', help='print help')
    help_parser.set_defaults(command='help')
   

def run(app, args):
    HelpCommand(app)(args)
    

class HelpCommand(SimpleCommand):
    def __call__(self, app):
        self.app.commander.print_help()
 
