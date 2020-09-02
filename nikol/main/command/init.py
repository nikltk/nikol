"""init
"""

_setup_ = {
    'version' : '0.0.1',
    'description' : 'Create an empty Nikol workspace'
}

import sys
from nikol.main.command import SimpleCommand
from nikol.core.init import Init

def init(app):
    return InitCommand(app)

class InitCommand(SimpleCommand):
    def __init__(self, app, name='init'):
        super().__init__(app, name)

    def run(self, argv):
        try:
            Init(self.app.name, self.app.cwd)
        except Exception as e:
            sys.exit(str(e))
