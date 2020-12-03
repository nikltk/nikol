# ls.py
#
# from scripts/valid-2-ls.py
#
# Author: yhj
#
# tagset checking not yet implemented! 
# 

"""
Validation Level 2 of LS corpus

Usage: valid-2-ls NXLS1902008050.json > nxls_valid_2.tsv 

JSON:

```
word: { begin, end, id, form }
morpheme: { word_id, position, id, form, label }
WSD: { begin, end, word, sense_id, pos }
```

Table: 

- 1: `sentence.fwid` (fixed width id)
- 2: `word.slice_str` (`word.begin`:`word.end`)
- 3: `word.id`
- 4: `word.form`
- 5: `morpheme.position`
- 6: `morpheme.id`
- 7: `morpheme.str` or `WSD.str`
- 8: `:` or `WSD.slice_str`
- 9: error


```
SARW1800001311-0001-00001-01732	0:2	1	어~	1	1	어/IC	:	### 
SARW1800001311-0001-00001-01732	3:7	2	구백미터	1	2	구백__888/NR	3:5	### 
SARW1800001311-0001-00001-01732	3:7	2	구백미터	2	3	미터__002/NNB	5:7	### 
SARW1800001311-0001-00001-01732	8:9	3	즉	1	4	즉/MAG	:	### 
SARW1800001311-0001-00001-01732	10:16	4	일점일키로를	1	5	일__018/NR	10:11	### 
SARW1800001311-0001-00001-01732	10:16	4	일점일키로를	2	6	점__019/NNG	11:12	### 
SARW1800001311-0001-00001-01732	10:16	4	일점일키로를	3	7	일__018/NR	10:11	### ErrorWSDBeginEnd(prev=11:12);ErrorWSDMorphemeMapping([1, 3]);
SARW1800001311-0001-00001-01732	10:16	4	일점일키로를	4	8	키로__001/NNB	13:15	### 
SARW1800001311-0001-00001-01732	10:16	4	일점일키로를	5	9	를/JKO	:	### 
SARW1800001311-0001-00001-01732	17:20	5	앞으로	1	10	앞__001/NNG	17:18	### 
SARW1800001311-0001-00001-01732	17:20	5	앞으로	2	11	으로/JKB	:	### 
SARW1800001311-0001-00001-01732	21:25	6	전진해서	1	12	전진__004/NNG	21:23	### 
SARW1800001311-0001-00001-01732	21:25	6	전진해서	2	13	하/XSV	:	### 
SARW1800001311-0001-00001-01732	21:25	6	전진해서	3	14	아서/EC	:	### 
```


Errors
================

- ErrorWSDMorphemeMapping(): check if wsd maps to morpheme 
- ErrorMorphemeId(): check morpheme. id 1, 2, 3, ..., n within sentence
- ErrorMorphemeForm() : check morpheme.form == word.form (if word has only one morpheme)
- ErrorMorphemeLabel(): check if morpheme label in tagset 
- ErrorMorphemePosition(): check morpheme position. 1, 2, 3, ..., m within word
- ErrorWSDBeginEnd(): 
- ErrorWSDBeginEndOutOfRange(): check if wsd begin:end within word begin:end
- ErrorWSDPos(): check if wsd pos in tagset
- ErrorWSDSenseID(): check wsd sense id. 1, 2, 3, ...; 777, 888, 999 



"""

import sys
import os
import re

from koltk.corpus.nikl.annotated import NiklansonReader 

def valid_ls(document):
    for sentence in document.sentence_list:
        if sentence.form == '':
            raise Exception('empty sentence')
        
        for word in sentence.word_list:
            if not hasattr(word, '_morphs') : word._morphs = []
            if not hasattr(word, '_wsd') : word._wsd = []
            if not hasattr(word, '_error') : word._error = []
            
        prev_m = None
        for count, m in enumerate(sentence.morpheme_list):
            if not hasattr(m, '_error'): m._error = []
            
            # check morpheme position
            #
            # if 1st morpheme in the sentence: check m.position == 1
            # elif 1st morpheme in the word: check m.position == 1
            # else: check m.position == prev_m.position + 1
            if prev_m is None:
                if m.position != 1:
                    m._error.append('ErrorMorphemePositon({}->1);'.format(m.position))
            elif m.word_id != prev_m.word_id:
                if m.position != 1:
                    m._error.append('ErrorMorphemePositon({}->1);'.format(m.position))
            else: 
                if m.position != prev_m.position + 1:
                    m._error.append('ErrorMorphemePositon(current={},prev={});'.format(m.position, prev_m.position))
               
            word = sentence.word_list[m.word_id - 1]
            word._morphs.append(m)

            prev_m = m
            word._wsd.append(None)
            
            if m.id != count + 1:
                m._error('ErrorMorphemeId();')

            #if m.label not in tagset: # ['NNG', 'NNP', 'NNB']
            #    err += 'ErrorMorphemeLabel();'
            
        for word in sentence.word_list:
            if len(word._morphs) == 1 and word.form != word._morphs[0].form:
                if sentence.id.startswith('S') and word.form.endswith('~') and word._morphs[0].label == 'IC':
                    pass
                else:
                    word._error.append('ErrorMorphemeForm({});'.format(word._morphs[0].form))
        
        prev_wsd = None
        for wsd in sentence.wsd_list:
            if not hasattr(wsd, '_error'): wsd._error = []
            
            if not (0 < wsd.sense_id < 90 or wsd.sense_id in [777, 888, 999]):
                wsd._error.append('ErrorWSDSenseID({});'.format(wsd.sense_id))
                
            #if wsd.pos not in tagset:
            #    err += 'WSDPosError({});'.format(wsd.pos)

            if prev_wsd is not None:
                if wsd.begin < prev_wsd.end:
                    wsd._error.append('ErrorWSDBeginEnd(prev={});'.format(prev_wsd.slice_str))

            prev_wsd = wsd

            if wsd.word_id == -1:
                for word in sentence.word_list:
                    if wsd.begin == word.begin:
                        break
                for morpheme in sentence.morpheme_list:
                    if morpheme.word_id == word.id and morpheme.form == wsd.word:
                        break
                wsd_position = morpheme.position
                wsd._error.append('ErrorWSDWordId({});'.format(wsd.word_id))

            else:
                word = sentence.word_list[wsd.word_id - 1]
            
                if not (word.begin <= wsd.begin < wsd.end <= word.end):
                    wsd._error.append('ErrorWSDBeginEndOutOfRange();')

                # map wsd to morpheme. 
                #
                wsd_position = None
                wsd_position_candidates = []


                # find all morpheme matching with the given wsd.
                # a word may contain more than two identical morphemes.
                for morph in word._morphs:
                    if wsd.word == morph.form and wsd.pos == morph.label:
                        wsd_position_candidates.append(morph.position)
                        
                # if there is only one morpheme matching with the wsd
                if len(wsd_position_candidates) == 1:
                    wsd_position = wsd_position_candidates[0]
                else:
                    for p in wsd_position_candidates:
                        if word._wsd[p - 1] is None:
                            wsd_position = p
                            break

                    try:
                        m = word._morphs[wsd_position - 1]
                    except:
                        raise Exception('{} {} {} {} {}'.format(sentence.fwid, word.id, word.form, word._morphs, word._wsd))
                        
                   
                    if not (wsd.word == m.form
                    and wsd.pos == m.label
                    and m.position == 1
                    and wsd.begin == word.begin):
                        pass
                        #wsd._error.append('ErrorWSDMorphemeMapping({});'.format(wsd_position_candidates))

            if wsd_position is None:
                # if something unexpected happens (we don't know yet),
                # print an extra line
                print('ERROR', word.id, word.form, wsd, wsd_position_candidates)
            elif word._wsd[wsd_position - 1] is None:
                word._wsd[wsd_position - 1] = wsd
            else:
                # if something unexpected happens (we don't know yet)
                # print an extra line
                print('ERROR', word.id, word.form, word.slice_str, wsd.slice_str, wsd, wsd_position_candidates)

        for word in sentence.word_list:
            n = len(word._wsd)
            for i in range(0, n):
                for j in range(i+1, n):
                    wsd1 = word._wsd[i]
                    wsd2 = word._wsd[j]
                    if wsd1 is None or wsd2 is None :
                        continue
                    elif wsd1.end <= wsd2.begin :
                        # normal
                        continue
                    elif wsd2.end <= wsd1.begin:
                        wsd2._error.append('ErrorWSDBeginEnd({});')
                    else:
                        wsd1._error.append('ErrorWSDBeginEnd(overplap);')
                        wsd2._error.append('ErrorWSDBeginEnd(overplap);')
                        
                

def table(document, spec='min', valid=False):
    valid_ls(document)
    rows = []
    for sentence in document.sentence_list:
        rows.append(sentence_table(sentence, spec=spec, valid=valid))

    return '\n'.join(rows)
 
def sentence_table(sentence, spec='min', valid=False):
    if spec == 'min':
        return sentence_table_min(sentence, valid)
    elif spec == 'full':
        return sentence_table_full(sentence, valid)
    else:
        raise Exception('Not supported spec: {}'.format(spec))

def sentence_table_full(sentence, valid):
    rows = []
    for word in sentence.word_list:
        for morph, wsd in zip(word._morphs, word._wsd):
            if wsd is None:
                wsd_str = morph.str
                wsd_slice_str = ''
            else:
                wsd_str = wsd.str
                wsd_slice_str = wsd.slice_str

                if wsd.word != morph.form:
                    wsd._error.append('ErrorWSDWord(morpheme:{}/{});'.format(morph.form, morph.label))
                elif wsd.pos != morph.label:
                    wsd._error.append('ErrorWSDPos(morpheme:{}/{});'.format(morph.form, morph.label))

            #
            fields = [sentence.fwid,
                    word.slice_str, str(word.id), word.form, 
                    str(morph.position), str(morph.id),
                    wsd_str,
                    wsd_slice_str
            ]
            if valid :
                err = ''.join(word._error)
                err += ''.join(morph._error)
                err += ''.join(wsd._error) if wsd else ''
                fields.append(err)

            rows.append('\t'.join(fields))

    return '\n'.join(rows)


def sentence_table_min(sentence, valid):
    rows = []
    for word in sentence.word_list:

        wsd_str = [] 
        for morph, wsd, err in zip(word._morphs, word._wsd, word._error):

            if wsd is None:
                wsd_str.append(morph.str)
            else:
                wsd_str.append(wsd.str)

        rows.append('\t'.join([word.gid,
                word.form, 
                ' + '.join(wsd_str)
        ]))

    return '\n'.join(rows)
