# sentence.py
#
# from scripts/valid-1/valid-1-sentence.py
#
# Usage: python make-sentence-table.py NXLS00000.json > nxls_sentence.txt
#
# 
#
# Level 0 Validation:
#
# - ErrorSentenceId: sentence id starts with document id
# - ErrorSentenceFormStrip: sentence form does not starts with whitespaces 
# - ErrorSentenceFormStrip: sentence form does not ends with whitespaces
# - ErrorSentenceFormTab: sentence form does not contain TAB
# - ErrorSentenceFormNewline: sentence from does not conatin newline
# - ErrorSentenceFormMultiSpace: sentence form does not contain more than two consecutive spaces
# - ErrorSentenceFormEmpty: sentence form == ""


def table(document, spec='min', valid=False):
    rows = []
    for sentence in document.sentence_list:
        sentence._error = [] 
        if not sentence['id'].startswith(document['id']):
            sentence._error.append('ErrorSentenceId({});'.format(document['id']))
        if sentence['form'].strip() != sentence['form']:
            sentence._error.append('ErrorSentenceFormStrip();')
        if sentence['form'].find('\t') > -1:
            sentence._error.append('ErrorSentenceFormTab();')     # TAB (0x09)
        if sentence['form'].find('\n') > -1:
            sentence._error.append('ErrorSentenceFormNewline();')  # LF (0x0a)
        if sentence['form'].find('\r') > -1:
            sentence._error.append('ErrorSentenceFormNewline();')  # CR (0x0d)
        if sentence['form'].find('  ') > -1:
            sentence._error.append('ErrorSentenceFormMultiSpace();')
        if sentence['form'].strip() == '':
            sentence._error.append('ErrorSentenceFormEmpty();')

        if spec == 'full':
            fields = [sentence.fwid, sentence.id, sentence.form]
        elif spec == 'min':
            fields = [sentence.fwid, sentence.snum, sentence.form]
        else:
            raise Exception('Not supported spec: {}'.format(spec))
    
        if valid: fields.append(''.join(sentence._error))

        rows.append('\t'.join(fields))

    return '\n'.join(rows)
    




        
