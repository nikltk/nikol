"""conv: convert between corpus formats
"""

_setup_ = {
    'version' : '0.1.0',
    'description' : 'convert between corpus formats'
}

import os
import sys
import argparse
from nikol.main.command import SimpleCommand
import nikol.valid  

from koltk.corpus.nikl.annotated import NiklansonReader

def init(app):
    return ConvCommand(app)

class ConvCommand(SimpleCommand):
    def __init__(self, app = None, name = 'conv'):
        super().__init__(app, name)
        
        self.parser.add_argument('filenames', type=str, nargs='*', help='input filenames or a directory')
        self.parser.add_argument('-f', '--from', type=str, dest='input_format', help='input format')
        self.parser.add_argument('-t', '--to', type=str, dest='output_format', help='output format')
        self.parser.add_argument('-o', '--output', type=str, dest='output_filename', help='output filename')
        self.parser.add_argument('-v', '--valid', '--verbose', dest='valid', action='store_true', help='Give verbose validation output')

        # annotation: sentence, word, morpheme, WSD, NE, DP, SRL, ZA, CR
        annotation_group = self.parser.add_mutually_exclusive_group()
        annotation_group.add_argument('-a', '--annotation', type=str, dest='annotation',
                                      help='annotation: sentence, word, morpheme, WSD, NE, ZA, DP, SR, CR')
        annotation_group.add_argument('-c', '--corpus-type', type=str, dest='corpus_type',
                                      help='corpus: sentence, word, mp, ls, ne, za, dp, sr, cr')
        annotation_group.add_argument('--sentence', action='store_const', const='sentence', dest='corpus_type', help='raw corpus sentence')
        annotation_group.add_argument('--word', action='store_const', const='word', dest='corpus_type', help='raw corpus word')
        annotation_group.add_argument('--mp', action='store_const', const='mp', dest='corpus_type', help='MP corpus')
        annotation_group.add_argument('--ls', action='store_const', const='ls', dest='corpus_type', help='LS corpus')
        annotation_group.add_argument('--ne', action='store_const', const='ne', dest='corpus_type', help='NE corpus')
        annotation_group.add_argument('--za', action='store_const', const='za', dest='corpus_type', help='ZA corpus')
        annotation_group.add_argument('--cr', action='store_const', const='cr', dest='corpus_type', help='CR corpus')
        annotation_group.add_argument('--dp', action='store_const', const='dp', dest='corpus_type', help='DP corpus')
        annotation_group.add_argument('--sr', action='store_const', const='sr', dest='corpus_type', help='SR corpus')

        spec_group = self.parser.add_mutually_exclusive_group()
        spec_group.add_argument('-s', '--spec', type=str, dest='spec', default='min', help='table type: min, full')
        spec_group.add_argument('--min', action='store_const', dest='spec', const='min', help='minimal spec table')
        spec_group.add_argument('--full', action='store_const', dest='spec', const='full', help='full spec table')

    def run(self, argv):
        args = self.parser.parse_args(argv)
        
        #
        # input files
        #
        if args.filenames == []:
            sys.exit('Specify filename(s) or a directory. Trye -h form more information.')
        elif len(args.filenames) == 1:
            if os.path.isfile(args.filenames[0]):
                pass
            else:
                path = args.filenames[0]
                args.filenames = []
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        args.filenames.append(os.path.join(dirpath, filename))
        else:
            for filename in args.filenames:
                if not os.path.isfile(filename):
                    sys.exit('Specify filenames or a directory. Do not specify directories.') 
        #
        # guess input format from filenames[0]
        #
        if args.input_format is None:
            if args.filenames is None:
                sys.exit('{} conv: specify input format! Try -h for more information.'.format(self.app.name))
            else:
                _, ext = os.path.splitext(args.filenames[0])
                args.input_format = ext[1:]
            
        #
        # guess output format
        #
        if args.output_format is None:
            if args.output_filename is None:
                args.output_format = 'tsv'
            else:
                _, ext = os.path.splitext(args.output_filename)
                args.output_format = ext[1:]
        

        #
        # dispatch 
        #
        if args.corpus_type is not None:
            pass
        elif args.annotation is not None:
            pass
        else:
            pass

        if args.input_format == 'json' and args.output_format == 'tsv':
            self.json2tsv(args)
        else:
            sys.exit('Not yet support conversion between formats: {} -> {}'.format(args.input_format, args.output_format))

    def json2tsv(self, args):
        for filename in args.filenames:
            with open(filename, encoding='utf-8') as file:
                reader = NiklansonReader(file)
                for document in reader.document_list:
                    try:
                        print(nikol.valid.table(document, corpus_type=args.corpus_type, spec=args.spec, valid=args.valid))
                    except NotImplementedError as e:
                        sys.exit('NotImpementedError: {}'.format(e))


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = ConvCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
