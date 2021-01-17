# dp.py
# from scripts/valid-2/valid-2-dp-koltk.py
#
# Author: jwk, yhj
#
# tagset checking not yet implemented!

"""
Validation Level 2 of DP corpus

Usage: valid-2-dp.py NXDP1902008051.json > nxdp_valid_2.tsv 

Or Unix command:  python valid-2-dp-koltk.py NXDP1902008051.json | grep "ErrorDPHead" | wc
>>>     122     951    8144

JSON
================

DP: {'word_id', 'word_form', 'head', 'label', 'dependent'}


OUTPUT
================
- PRINT: 
  - sentence_id, 
  - word_id, word_form, head, label, dependent
  - Error


Example

sentence_id	word_id	word_form	head	label	dependent
NWRW1800000021.24.7.1	1	한때	15	NP_AJT	[]	
NWRW1800000021.24.7.1	2	세상을	3	NP_OBJ	[]	
NWRW1800000021.24.7.1	3	내려다보긴	4	VP_SBJ	[2]	
NWRW1800000021.24.7.1	4	같지만	14	VP	[3]	
NWRW1800000021.24.7.1	5	스스로	7	AP	[]	
NWRW1800000021.24.7.1	6	몸을	7	NP_OBJ	[]	
NWRW1800000021.24.7.1	7	드러내는	8	VP_MOD	[5, 6]	
NWRW1800000021.24.7.1	8	해와	11	NP_CNJ	[7]	
NWRW1800000021.24.7.1	9	몸을	10	NP_OBJ	[]	
NWRW1800000021.24.7.1	10	감추는	11	VP_MOD	[9]	
NWRW1800000021.24.7.1	11	달은	14	NP_SBJ	[8, 10]	
NWRW1800000021.24.7.1	12	서로	13	AP	[]	
NWRW1800000021.24.7.1	13	다른	14	VP_MOD	[12]	
NWRW1800000021.24.7.1	14	족속이라고	15	VNP	[4, 11, 13]	
NWRW1800000021.24.7.1	15	일갈했던	16	VP_MOD	[1, 14]	
NWRW1800000021.24.7.1	16	공찬은	19	NP_SBJ	[15]	
NWRW1800000021.24.7.1	17	이	18	DP	[]	
NWRW1800000021.24.7.1	18	문답을	19	NP_OBJ	[17]	
NWRW1800000021.24.7.1	19	통해	22	VP	[16, 18]	
NWRW1800000021.24.7.1	20	권력의	21	NP_MOD	[]	
NWRW1800000021.24.7.1	21	본질을	22	NP_OBJ	[20]	
NWRW1800000021.24.7.1	22	깨닫고	28	VP	[19, 21]	
NWRW1800000021.24.7.1	23	이	24	DP	[]	
NWRW1800000021.24.7.1	24	몸	26	NP	[23]	
NWRW1800000021.24.7.1	25	저	26	DP	[]	
NWRW1800000021.24.7.1	26	몸으로	27	NP_AJT	[24, 25]	
NWRW1800000021.24.7.1	27	옮겨	28	VP	[26]	
NWRW1800000021.24.7.1	28	다니며	31	VP	[22, 27]	
NWRW1800000021.24.7.1	29	한바탕	31	AP	[]	ErrorDPDependent();
NWRW1800000021.24.7.1	30	놀이를	31	NP_OBJ	[29]	ErrorDPDependent();
NWRW1800000021.24.7.1	31	펼친다.	-1	VP	[28, 30]


Errors
================
- ErrorDPId(): check dp id i.e) 1, 2, 3, ..., n within sentence
- ErrorDPLabel(): check if DP label is in tagset 
- ErrorDPDependent(): check the coherence between head and dependent id
- ErrorDPHead(): check if head tagged only once
"""

from collections import deque


def find_crossing(head_list):
    heads = []
    for i, head in enumerate(head_list):
        if head == -1:
            heads.append(len(head_list) + 1)
        else:
            heads.append(head)

    found = []

    for i in range(len(heads)-1):
        for j in range(i+1, len(heads)):
            id1 = i + 1
            head1 = heads[i]

            id2 = j + 1
            head2 = heads[j]

            if max(id1, head1) <= min(id2, head2):
                continue

            if not (id1 <= id2 <= head1 and id1 <= head2 <= head1) and not (id2 <= id1 <= head2 and id2 <= head1 <= head2):
                found.append((id1, id2))
    return found


def table(document, spec='min', valid=False):
    rows = []
    for sent in document.sentence_list:

        # find root list
        root = [i.get('head') for i in sent.dp_list if i.get('head') == -1]
        id2dp = {j.get('word_id'): j.get('dependent')
                 for j in sent.dp_list if len(j.get('dependent')) > 0}
        id2head = {j.get('word_id'): j.get('head') for j in sent.dp_list}

        dp_err = set()
        for head_id, dependent in id2dp.items():  # let's find  out depenent's idx
            for dp_idx in dependent:
                if not id2head[dp_idx] == head_id:
                    dp_err.update([dp_idx, head_id])

        word_idx = 1
        for dp in sent.dp_list:
            if not hasattr(dp, '_error'):
                dp._error = []

            word = sent.word_list[dp.word_id - 1]
            if word.form != dp.word_form:
                dp._error.append('ErrorDPWordForm({})'.format(word.form))

            if not dp.word_id == word_idx:
                dp._error.append('ErrorDPId();')

            # error if head is not single
            if not len(root) == len(set(root)) and dp.head == -1:
                dp._error.append('ErrorDPHead();')

            if dp.word_id in dp_err:
                dp._error.append('ErrorDPDependent();')

            word_idx += 1

            if spec == 'full':
                fields = [
                    sent.fwid,
                    str(word.id),
                    dp.word_form,
                    dp.label,
                    str(dp.head),
                    str(dp.dependent)
                ]
            elif spec == 'min':
                fields = [
                    word.gid,
                    str(word.id),
                    dp.word_form,
                    dp.label,
                    str(dp.head),
                ]
            else:
                raise Exception('Not supported spec: {}', spec)

            if valid:
                fields.append(''.join(dp._error))

            rows.append('\t'.join(fields))

    return '\n'.join(rows)


def trigram(dp):
    sent = dp.parent
    trigram = ''
    if len(sent.dp_list) == 1:
        trigram = dp.word_form
    elif dp.word_id == 1:
        trigram = dp.word_form + ' ' + sent.dp_list[dp.word_id].word_form
    elif dp.word_id == len(sent.dp_list):
        trigram = sent.dp_list[dp.word_id - 2].word_form + ' ' + dp.word_form
    else:
        trigram = sent.dp_list[dp.word_id - 2].word_form + ' ' + \
            dp.word_form + ' ' + sent.dp_list[dp.word_id].word_form

    return trigram
