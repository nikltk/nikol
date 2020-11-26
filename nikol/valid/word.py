# word.py
# from scripts/valid-1/valid-1-word.py
#
# Usage: python make-word-table.py NXLS00000.json > nxls_word.txt
#
#
# Level 1 Validation:
#
# - ErrorWordFormWhiteSpace: check if word form contains whitespaces: CR, LF, Tab, Space 
# - ErrorWordBeginEnd: check if word_form == sentence_form[begin:end]
# - ErrorWordId: check if word ids are consecutive natural numbers, i.e. [1, 2, 3, ... n] in a sentence.
# - ErrorWordIdForm: check if i-th word form == i-th token of sentence form
import re




def table(document, spec='min', valid=False):
    rows = []
    for sentence in document.sentence_list:
        toks = sentence.form.split()
        
        #if sentence['word'] is None:
        #    continue
        
        prev_word_id = 0
        for word in sentence.word_list:

            word._error = []
            if word.id == prev_word_id + 1:
                prev_word_id = word.id
                if toks[word.id-1] != word.form:
                    word._error.append('ErrorWordIdForm({}:{});'.format(word['id'], toks[word['id']-1]))
            else:
                word._error.append('ErrorWordId({}->{});'.format(word['id'], prev_word_id + 1))

            if len(re.findall('[\t\n\r ]', word.form)) > 0 :
                word._error.append('ErrorWordFormWhiteSpace();')
            if word.form != sentence.form[word.slice] :
                word._error.append('ErrorWordBeginEnd({});'.format(sentence.form[word.slice]))
           
            fields = [sentence.fwid,
                  word.slice_str,
                  str(word.id),
                  word.form,
            ]
            if valid: fields.append(''.join(word._error))

            rows.append('\t'.join(fields))


    return '\n'.join(rows)

