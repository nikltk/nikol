"""conv: convert between corpus formats
"""
__epilog__ = """
example:
  # convert json to min.tsv (default) or full.tsv (with --full)
  $ nikol conv --ls NWRW1800000021-0003.json       # a single LS JSON corpus
  $ nikol conv --ls nxls/document                  # a directory containing JSON files
  $ nikol conv --ls --full --valid nxls/document   # 


  # convert unified.min.tsv to single annotation level json 
  nikol conv --ls NWRW1800000021-0003.unified.min.tsv
  nikol conv --ls --valid NWRW1800000021-0003.unified.min.tsv  # print only errors
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
import nikol.table

from koltk.corpus.nikl.annotated import NiklansonReader, NiklansonDocumentReader

def init(app):
    return ConvCommand(app)

class ConvCommand(SimpleCommand):
    def __init__(self, app = None, name = 'conv'):
        super().__init__(app, name, epilog = __epilog__)
        
        self.parser.add_argument('filenames', type=str, nargs='*',
                                 help='input filenames or a directory')
        self.parser.add_argument('-f', '--from', type=str, dest='input_format',
                                 help='input format: json, tsv')
        self.parser.add_argument('-t', '--to', type=str, dest='output_format',
                                 help='output format: json, tsv')
        self.parser.add_argument('-o', '--output', type=str, dest='output_filename',
                                 help='output filename')
        self.parser.add_argument('-v', '--valid', '--verbose', dest='valid', action='store_true',
                                 help='validation (TSV)')

        # annotation: sentence, word, morpheme, WSD, NE, DP, SRL, ZA, CR
        annotation_group = self.parser.add_mutually_exclusive_group()
        annotation_group.add_argument('-a', '--annotation', type=str, dest='annotation',
                                      help='annotation (JSON): sentence, word, morpheme, WSD, NE, ZA, DP, SR, CR')
        annotation_group.add_argument('-c', '--corpus-type', type=str, dest='corpus_type',
                                      help='corpus (JSON): sentence, word, mp, ls, ne, za, dp, sr, cr')
        annotation_group.add_argument('--sentence', action='store_const', const='sentence', dest='corpus_type',
                                      help='raw corpus sentence (JSON)')
        annotation_group.add_argument('--word', action='store_const', const='word', dest='corpus_type',
                                      help='raw corpus word (JSON)')
        annotation_group.add_argument('--mp', action='store_const', const='mp', dest='corpus_type',
                                      help='MP corpus (JSON)')
        annotation_group.add_argument('--ls', action='store_const', const='ls', dest='corpus_type',
                                      help='LS corpus (JSON)')
        annotation_group.add_argument('--ne', action='store_const', const='ne', dest='corpus_type',
                                      help='NE corpus (JSON)')
        annotation_group.add_argument('--za', action='store_const', const='za', dest='corpus_type',
                                      help='ZA corpus (JSON)')
        annotation_group.add_argument('--cr', action='store_const', const='cr', dest='corpus_type',
                                      help='CR corpus (JSON)')
        annotation_group.add_argument('--dp', action='store_const', const='dp', dest='corpus_type',
                                      help='DP corpus (JSON)')
        annotation_group.add_argument('--sr', action='store_const', const='sr', dest='corpus_type',
                                      help='SR corpus (JSON)')

        spec_group = self.parser.add_mutually_exclusive_group()
        spec_group.add_argument('-s', '--spec', type=str, dest='spec', #default='min',
                                help='spec (TSV): (for output) min, full; (for input) unified.min')
        spec_group.add_argument('--min', action='store_const', dest='spec', const='min',
                                help='minimal spec table (TSV)')
        spec_group.add_argument('--full', action='store_const', dest='spec', const='full',
                                help='full spec table (TSV)')


        # json options
        self.parser.add_argument('--json-indent', type=int, dest='json_indent',
                                 help='json dump indent')


        # metadata
        self.parser.add_argument('--json-template', type=str, dest='json_template',
                                 help='JSON template')

    def run(self, argv):
        args = self.parser.parse_args(argv)
        
        #
        # input files: args.filenames
        #
        # (1) a file 
        # (2) files (wildcard)
        # (3) a directory => list files
        #
        if args.filenames == []:
            sys.exit('Specify filename(s) or a directory. Trye -h form more information.')
        elif len(args.filenames) == 1:
            if os.path.isfile(args.filenames[0]):
                pass
            else:
                # if len(args.filenames) == 1 and args.filenames[0] is a directory:
                # reassign args.filenames = list of filenames
                path = args.filenames[0]
                args.filenames = []
                for dirpath, dirnames, filenames in os.walk(path):
                    dirnames.sort()
                    filenames.sort()
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
                if args.input_format == 'json':
                    args.output_format = 'tsv'
                elif args.input_format == 'tsv':
                    args.output_format = 'json'
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
        elif args.input_format.endswith('tsv') and args.output_format == 'json':
            self.tsv2json(args)
        else:
            sys.exit('Not yet support conversion between formats: {} -> {}'.format(args.input_format, args.output_format))

    def json2tsv(self, args):
        if args.spec is None: args.spec = 'min'
        
        for filename in args.filenames:
            with open(filename, encoding='utf-8') as file:
                reader = NiklansonReader(file)
                for document in reader.document_list:
                    try:
                        print(nikol.valid.table(document, corpus_type=args.corpus_type, spec=args.spec, valid=args.valid))
                    except NotImplementedError as e:
                        sys.exit('NotImpementedError: {}'.format(e))

    def tsv2json(self, args, ):
        # args.input_format: 'tsv'
        # args.output_format: 'json'
        # args.corpus_type (use this for output json): 'mp', 'ls', 'ne', ...
        # args.filenames : ['*.tsv']
        # args.spec (usually None) : 'unified.min'
        if len(args.filenames) > 1:
            sys.exit('Not yet support conversion from multiple tsv files to a single valid json.')
        
        if args.spec is None:
            filename = args.filenames[0]
            toks = filename.split('.')[:-1]  # toks[-1] == 'tsv'
        else:
           toks = args.spec.split('.')
       
        try:
            tsv_spec = toks[-1]
            tsv_annotation_level = toks[-2]
        except IndexError:
            sys.exit('Specify input tsv format, for example, --spec unified.min')


        if tsv_annotation_level == 'unified' and tsv_spec == 'min':
            self.unified_min_tsv2json(args)
 
    def unified_min_tsv2json(self, args):
        """convert a single unified.min.tsv to single json
        """
        # args.corpus_type (use this for output json): 'mp', 'ls', 'ne', ...
        # args.filenames : ['*.tsv']

        if args.json_template is not None:
            with open(args.json_template) as file:
                reader = NiklansonDocumentReader(file)
                document_metadata = reader.document.metadata
                document_id = reader.document.id

        filename = args.filenames[0]

        with open(filename, encoding = 'utf-8') as file:
            reader = nikol.table.reader(file, format='unified.min.tsv')
            for document in reader:
                try:
                    getattr(document, 'make_{}_corpus'.format(args.corpus_type))(valid = args.valid)
                except Exception as e:
                    if args.valid:
                        print(e)
                    else:
                        print(e)
                        #pass
                    #sys.exit(e)
                    
                if not args.valid:
                    if args.json_template is not None:
                        if document.id == document_id:
                            document.metadata = document_metadata
                            print(document.json(indent = args.json_indent))
                        else:
                            sys.exit('document metadata error: document id does not match')
                    else:
                        print(document.json(indent = args.json_indent))
        

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    command = ConvCommand()
    command.run(argv)

if __name__ == '__main__' :
    main()
