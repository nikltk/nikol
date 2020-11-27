"""valid: validation
"""
import sys
from . import mp
from . import ls
from . import za
from . import word
from . import sentence
from . import dp
from . import ne
from . import cr



def table(object, corpus_type=None, spec='min', valid=False):
    """Converts JSON to table. 
    
    - takes as input a Document (koltk.corpus.nikl.annotated.object.Document)
    - validates annotations
    - and returns a table


    :param object: koltk.corpus.nikl.annotated.object.Document
    :param corpus_type: 'mp', 'ls', 'ne', 'dp', 'sr', 'za', 'cr'
    :param spec:  'min', 'full'
    :param valid:
    """
    if corpus_type is None:
        raise NotImplementedError('cannot guess corpus type. Please specify the corpus type.')
    else:
        module = getattr(sys.modules[__name__], corpus_type)
        return module.table(object, spec=spec, valid=valid)


