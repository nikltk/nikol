"""config
"""

_setup_ = {
    'version' : '0.0.1',
    'description' : 'Get and set local (workspace) or global (user) options'
}

import sys
from nikol.main.command import SimpleCommand
from nikol.core.config import Config

def init(app):
    return ConfigCommand(app)

class ConfigCommand(SimpleCommand):
    def __init__(self, app, name='config'):
        super().__init__(app, name)

        self.parser.add_argument('-l', '--list', action='store_true', help='list all options')
        self.parser.add_argument('name', type=str, nargs='?')
        self.parser.add_argument('value', type=str, nargs='?')

    def run(self, argv):
        args = self.parser.parse_args(argv)
        
        try:
            config = self.app.config
        except Exception as e:
            sys.exit(str(e))

        if args.list :
            for secname in config.sections():
                for name in config[secname]:
                    print(secname + '.' + name + '=' + config[secname][name])
        elif args.name is not None:
            section, name = args.name.split('.')
            if args.value is None:    
                print(config[section][name])
            else:
                config.set_local(section, name, args.value)
