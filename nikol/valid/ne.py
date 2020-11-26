# ne.py
#
# from scripts/valid-2/valid-2-ne.py
#
# Author: yhj
#
# tagset checking not yet implemented! 
# 

"""
Validation Level 2 of NE corpus

Usage: valid-2-ls NXNE19000.json > nxne_valid_2.tsv 



JSON
================

word: { id, form, begin, end }
ne: { begin, end, id, form, label }


OUTPUT
================

Example

sentence_id	word_be	word_id	word_form	m_p	m_id	m_form	m_label  ERROR
SARW18..1.1	0:4	1	요즘처럼	1	1	요즘	NNG	0:2	요즘	1	NNG
SARW18..1.1	0:4	1	요즘처럼	2	2	처럼	JKB
SARW18..1.1	5:7	2	추운	1	3	춥	VA
SARW18..1.1	5:7	2	추운	2	4	ㄴ	ETM
SARW18..1.1	8:12	3	날씨에는	1	5	날씨	NNG	8:10	날씨	1	NNG
SARW18..1.1	8:12	3	날씨에는	2	6	에	JKB
SARW18..1.1	8:12	3	날씨에는	3	7	는	JX



Errors
================

- ErrorNEId: 
- ErrorNEFormBeginEnd: sentence form != ne form
- ErrorNELabel:



"""

def decompose(han) : 
    num = ord(han) - 0xac00
    lead = num // 588
    vt = num % 588
    vowel = vt // 28
    trail = vt % 28

    return [lead, vowel, trail]


def table_sentence_full(sentence, valid=False):
    rows = []
    for word in sentence.word_list:
        if len(word._ne) == 0: word._ne = [None]
        for ne in word._ne:
            if ne == '&' or ne is None : 
                ne_slice_str = ''
                ne_id = ''
                ne_str = ''
                ne_error = ''
            else:
                ne_slice_str = ne.slice_str
                ne_id = str(ne.id)
                ne_str = ne.str
                ne_error = ''.join(ne._error)

            fields = [sentence.fwid, word.slice_str, str(word.id), word.form,
                        ne_slice_str, ne_id, ne_str]
            if valid : fields.append(ne_error)
            rows.append('\t'.join(fields))

    return '\n'.join(rows)

                    
def table_sentence_min(sentence, valid=False):
    rows = []
    for word in sentence.word_list:

        ne_str = []
        for ne in word._ne:
            if ne == '&': ne_str.append('&')
            else: ne_str.append(ne.str)


        fields = [word.gid,
                  word.form,
                  ' + '.join(ne_str)
        ]

        rows.append('\t'.join(fields))

    return '\n'.join(rows)


def table(document, spec='min', valid=False):
    rows = []
    for sentence in document.sentence_list:
        if sentence.form == '':
            continue
        
        for word in sentence.word_list:
            if not hasattr(word, '_ne'):  word._ne = []

        for i, ne in enumerate(sentence.ne_list):
            if not hasattr(ne, '_error'): ne._error = []
            
            if ne.id != i + 1:
                ne._error.append('ErrorNEId({}->{});'.format(ne.id, i+1))
                
            if sentence.form[ne.slice] != ne.form:
                last_char = sentence.form[ne.slice][-1]
                if decompose(last_char)[0:2] != decompose(ne.form[-1])[0:2]:
                    ne._error.append('ErrorNEFormBeginEnd({});'.format(sentence.form[ne.slice]))

            # map ne to word
            found = False
            for word in sentence.word_list:
                if word.begin <= ne.begin < word.end :
                    if word.form.count(ne.form) > 1:
                        ne._position = '@' + str(ne.begin - word.begin)
                    else:
                        ne._position = ''
                    word._ne.append(ne)
                    found = True
                    #break
                if ne.begin < word.begin < ne.end:
                    word._ne.append('&')

            if not found:
                # if unexpected error happens (we don't know yet what)
                print("ERROR", ne)


        if spec == 'full' :
            rows.append(table_sentence_full(sentence, valid))
        elif spec == 'min' :
            rows.append(table_sentence_min(sentence, valid))

    return '\n'.join(rows)
