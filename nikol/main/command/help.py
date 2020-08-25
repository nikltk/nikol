from nikol.main.command import SimpleCommand

def run(app, args):
    HelpCommand(app)(args)
    

class HelpCommand(SimpleCommand):
    def __call__(self, app):
        self.app.commander.parser.print_help()
 
