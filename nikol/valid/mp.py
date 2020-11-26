# mp.py
#
# from scripts/valid-2/valid-2-mp.py
#
# Author: jwk, yhj
#
# tagset checking not yet implemented! 

"""
Validation Level 2 of MP corpus

Usage: mp.py NXMP1902008040.json > nxmp_valid_2.tsv 


JSON:

```
word: { begin, end, id, form }
morpheme: { word_id, position, id, form, label }
```

Table: 

- 1: `sentence.fwid` (fixed width id)
- 2: `word.slice_str`  (`word.begin`:`word.end`)
- 3: `word.id` (`morpheme.word_id`)
- 4: `word.form`
- 5: `morpheme.position`
- 6: `morpheme.id`
- 7: `morpheme.str` (`morpheme.form`/`morpheme.label`)
- 8: error

```
SARW1800001311-0001-00001-00590	0:2	1	어~	1	1	어/IC	### ErrorMorphemeForm();
SARW1800001311-0001-00001-00590	3:6	2	타협과	1	2	타협/NNG	### 
SARW1800001311-0001-00001-00590	3:6	2	타협과	2	3	과/JC	### 
SARW1800001311-0001-00001-00590	7:10	3	화해의	1	4	화해/NNG	### 
SARW1800001311-0001-00001-00590	7:10	3	화해의	2	5	의/JKG	### 
SARW1800001311-0001-00001-00590	11:13	4	길로	1	6	길/NNG	### 
SARW1800001311-0001-00001-00590	11:13	4	길로	2	7	로/JKB	### 
SARW1800001311-0001-00001-00590	14:15	5	어	1	8	어/IC	### 
SARW1800001311-0001-00001-00590	16:18	6	저는	1	9	저/NP	### 
```

Errors
================
- ErrorMorphemeId(): check MP id i.e) 1, 2, 3, ..., n within sentence
- ErrorMorphemeForm(): check if morpheme form/word form is consistent
"""




def valid_morpheme(sentence):
    if not hasattr(sentence, 'morpheme') :
        return None
    
    for word in sentence.word_list:
        word._morph = []

    idx = 1
    for mp in sentence.morpheme_list:
        mp._error = []
        
        word = sentence.word_list[mp.word_id - 1]
        word._morph.append(mp)

        if mp.id != idx: mp._error.append('ErrorMorphemeId();')

        idx += 1

    for word in sentence.word_list:
        if len(word._morph) == 1 and word.form != word._morph[0].form:
            if sentence.id.startswith('S') and word.form.endswith('~') and word._morph[0].label == 'IC':
                pass
            else:
                word._morph[0]._error.append('ErrorMorphemeForm();')
  


def table(document, spec='min', valid=False):
    if document.__class__.__name__ != 'Document':
        raise Exception('Not supported object: {}'.format(document.__class__))
        
    rows = []
    for sentence in document.sentence_list:
        rows.append(sentence_table(sentence, spec=spec, valid=valid))

    return '\n'.join(rows)
        



def sentence_table(sentence, spec='min', valid=False):
    valid_morpheme(sentence)
    if spec == 'min':
        return sentence_table_min(sentence, valid)
    elif spec == 'full':
        return sentence_table_full(sentence, valid)
    else:
        raise Exception('Not supported spec: {}'.format(spec))
    
def sentence_table_full(sentence, valid):
    rows = []
    for word in sentence.word_list:
        for morph in word._morph:
            rows.append('\t'.join([
                sentence.fwid,
                word.slice_str,
                str(word.id),
                word.form,
                str(morph.position),
                str(morph.id),
                morph.str,
                ''.join(morph._error),
            ])) 
    return '\n'.join(rows)

def sentence_table_min(sentence, valid):
    rows = []
    for word in sentence.word_list:
        morph_str = ' + '.join([m.str for m in word._morph])
        rows.append('\t'.join([
            word.gid,
            word.form,
            morph_str,
        ]))

    return '\n'.join(rows)

if __name__ == '__main__':
    import sys
    from koltk.corpus.nikl.annotated import NiklansonReader
    import nikol.valid

    filename = sys.argv[1]
    reader = NiklansonReader(filename)

    for document in reader.document_list:
        for sentence in document.sentence_list:
            print(nikol.valid.mp.table(sentence, spec='full'))
