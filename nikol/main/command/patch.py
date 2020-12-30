"""patch: make, preview, and apply a patch 
"""
__epilog__ = """
example:
  $ cd /path/to/annotated-documents-split-20-min-tsv
  $ nikol patch --make-patch /path/to/work.prepatch.tsv > work.patch.tsv
  $ nikol patch --write /path/to/work.prepatch.tsv
"""

_setup_ = {
    'version' : '0.1.0',
    'description' : 'make, preview, and apply a patch'
}

import os
import sys
import datetime
import argparse
from nikol.main.command import SimpleCommand
import nikol.update 

def init(app):
    return PatchCommand(app)

class PatchCommand(SimpleCommand):
    def __init__(self, app = None, name = 'patch'):
        super().__init__(app, name, epilog=__epilog__)
        
        self.parser.add_argument('origin', type=str, nargs='?', default='.',
                                help='orignal directory (default: current directory)')
        self.parser.add_argument('--corpus-dir', type=str, default='unified_min_tsv',
                                 help='corpus directory (default: unified_min_tsv)')
        self.parser.add_argument('--log-dir', type=str, default='log',
                                 help='log directory (default: log)')
        self.parser.add_argument('--comment-dir', type=str, default='comment',
                                 help='comment directory (default: comment)')

        # prepatch or patch file
        filename_group = self.parser.add_mutually_exclusive_group()
        filename_group.add_argument('patchfile', type=str, nargs='?',
                                    help='prepatch or patch filename with extension .prepatch.tsv or .patch.tsv')
        filename_group.add_argument('--prepatch', type=str, dest='prepatch_filename',
                                    help='prepatch filename')
        filename_group.add_argument('--patch', type=str, dest='patch_filename',
                                    help='patch filename')
        

        # action
        action_group = self.parser.add_mutually_exclusive_group()
        action_group.add_argument('--make-patch', dest='action', action='store_const', const='make-patch',
                                  help='make a patch from a prepatch') 
        action_group.add_argument('--preview', dest='action', action='store_const', const='preview',
                                  help='preview') 
        action_group.add_argument('--write', dest='action', action='store_const', const='write',
                                  help='apply a patch to the origin') 
        
    def run(self, argv):
        args = self.parser.parse_args(argv)
        #print(args)

        #
        # if patch is missing
        #
        if args.patchfile is None and args.patch_filename is None and args.prepatch_filename is None:
            if args.origin is not None and os.path.isfile(args.origin):
                args.patchfile = args.origin
                args.origin = '.'
            else:
                sys.exit('{} patch: specify a patch file. Try -h for more information.'.format(self.app.name))


        #
        # infer patch type from extension
        #
        if args.patchfile is not None:
            filename, ext = os.path.splitext(args.patchfile)
            if ext == '.tsv' :
                filename, ext2 = os.path.splitext(filename)
                if ext2 == '.patch':
                    args.patch_filename = args.patchfile
                elif ext2 == '.prepatch':
                    args.prepatch_filename = args.patchfile
                else:
                    sys.exit('{} patch: cannot infer patch type from extension. Try -h for more information.'.format(self.app.name))
            else:
                sys.exit('{} patch: cannot infer patch type from extension. Try -h for more information.'.format(self.app.name))
                    
        if args.action is None:
            args.action = 'make-patch'

        if args.action == 'make-patch' and args.prepatch_filename is not None:
            self.print_patch(args)
        elif args.action == 'write' and args.prepatch_filename is not None:
            self.write_patch(args)
            
    def create_updater(self, args):
        workname = os.path.basename(args.prepatch_filename).split('.')[0]

        timestamp = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        patchname = workname + '_' + timestamp
        comment_filename = os.path.join(args.origin, args.comment_dir, patchname + '.comment.tsv')
        log_filename = os.path.join(args.origin, args.log_dir, patchname + '.log.tsv')

        self.updater = nikol.update.Updater()
        self.updater.Config(os.path.join(args.origin, args.corpus_dir),
                  comment=open(comment_filename, 'w', encoding='utf-8'),
                  log = open(log_filename, 'w', encoding='utf-8'))

        with open(args.prepatch_filename, encoding='utf-8') as file:
            self.updater.load_prepatch(file)
            self.updater.make_patch()

    def print_patch(self, args):
        self.create_updater(args)
        for p in self.updater.patch:
            print('\t'.join(p))

    def write_patch(self, args):
        self.create_updater(args)
        self.updater.write()
            

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = PatchCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
