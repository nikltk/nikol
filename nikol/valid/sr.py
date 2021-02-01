# sr.py
#
# from scripts/valid-2/valid-2-sr.py
#
# document
#  sentence
#    word : []
#    SRL : [ {
#              predicate : { form, begin, end, lemma, sense_id },
#              argument : { form, label, begin, end }
#           } ]
#
#
#
# ErrorSRLArgumentForm : argument.form != sentence.form[argument.slice]
# ErrorSRLPredicateForm : predicate.form != sentence.form[predicate.slice]


import re
from . import util

def check_srl_predicate_lemma(predicate):
    error = []
    if re.findall('[^가-힣]', predicate.lemma) != []:
        error.append('ErrorSRLPredicateLemma();')
    elif predicate.sense_id < 1000000 and not predicate.lemma.endswith('다'):
        error.append('ErrorSRLPredicateLemma();')
    elif predicate.sense_id >= 6000000 and not predicate.lemma.endswith('다'):
        error.append('ErrorSRLPredicateLemma();')
    elif 4000000 <= predicate.sense_id < 6000000 and predicate.lemma.endswith('다') :
        error.append('ErrorSRLPredicateLemma();')

    predicate._error.append(''.join(error))

   



def table_sentence_full(sentence, valid=False):
    rows = []
    
    rows.append('\t'.join([sentence.fwid, 'sentence', sentence.form]))

    for srl in sentence.srl_list:
        predicate = srl.predicate
        predicate._error = []
        word = sentence.wordAt(predicate.begin)
        word._srl = srl
        word._predicate = predicate
        predicate._word_id = word.id
        predicate._dependent = []


        if predicate.form != sentence.form[predicate.slice]:
            predicate._error.append('ErrorSRLPredicateForm();')

        #
        # check predicate lemma
        # 
        check_srl_predicate_lemma(predicate)
        
        rows.append('')
        rows.append('\t'.join([
            sentence.fwid,
            str(word.id),
            word.form,
            predicate.slice_str, 'predicate',
            predicate.form, predicate.str,
            ''.join(predicate._error)
        ]))

        for argument in srl.argument_list:

            argument._error = []
            
            word_1 = sentence.wordAt(argument.begin)
            argument._word_id = word_1.id
            arg_form_toks = argument.form.split()

            if len(arg_form_toks) == 0:
                argument._error.append('ErrorSRLArgumentFormNull();')
            elif word_1.form.find(arg_form_toks[0][0]) == -1:
                argument._error.append('ErrorSRLArgumentFormBegin({});'.format(word_1.form))
                
            word = sentence.word_list[argument._word_id - 1]

            
            if hasattr(word, '_argument'):
                word._argument.append(argument)
            else:
                word._argument = [argument]

            predicate._dependent.append(word.id)
            argument.head = predicate._word_id
            if argument.form.strip() != argument.form:
                argument._error.append('ErrorSRLArgumentForm(strip);')
            elif sentence.form[argument.slice] != argument.form:
                if util.form_match(argument.form, sentence.form[argument.slice]): continue
                argument._error.append('ErrorSRLArgumentForm({});'.format(sentence.form[argument.slice]))

            rows.append('\t'.join([
                sentence.fwid,
                str(word.id),
                word.form,
                  argument.slice_str, 'argument',
                  argument.label,
                  argument.form,
                  ''.join(argument._error)
            ]))

    return '\n'.join(rows)


def table_sentence_min(sentence, valid=False):
    rows = []
    for word in sentence.word_list:
        if hasattr(word, '_srl'):
            srl = word._srl

            argstrs = []
            for arg in srl.argument_list:
                w1 = sentence.wordAt(arg.begin)
                wn = sentence.wordAt(arg.end - len(arg.form.split()[-1]))

                if w1.id != wn.id:
                    arg_form_range = '{}-{}'.format(w1.id, wn.id)
                else:
                    arg_form_range = '{}'.format(w1.id)

                argstrs.append('{}__@{}'.format(arg.str, arg_form_range))

            srl_pred = srl.predicate.str
            srl_args = ' '.join(argstrs)
            srl_errors = '' 
        else:
            srl_pred = ''
            srl_args = ''
            srl_errors = ''

        fields = [
            word.gid, word.swid, word.form, srl_pred, srl_args
        ]
        if valid : fields.append(srl_errors)

        rows.append('\t'.join(fields))

    return '\n'.join(rows)

def table(document, spec='min', valid=False):
    rows = []
    for sentence in document.sentence_list:
        for srl in sentence.srl_list:
            predicate = srl.predicate
            predicate._error = []
            word = sentence.wordAt(predicate.begin)
            word._srl = srl
            word._predicate = predicate
            predicate._word_id = word.id
            predicate._dependent = []

        if spec == 'full':    
            rows.append('--------')
            rows.append(table_sentence_full(sentence, valid))
        elif spec == 'min' :
            rows.append(table_sentence_min(sentence, valid))

    return '\n'.join(rows)
