# za.py
#
# from scripts/valid-2-za.py
#
# Author: yhj
#
# WARNING: Use this script only for *Subject* ZA Corpus.
#
"""
Validation Level 2 of ZA corpus

Usage: valid-2-za nxza.json 


JSON
================

ZA
  predicate : {form, sentence_id, begin, end}
  antecedent : [ {form, type, sentence_id, begin, end} ]

"""

import sys
import re

from koltk.corpus.nikl.annotated import NiklansonReader 


class Table:
    def __init__(self, object):
        pass

    def valid(self):
        pass
    
        
    def full(self):
        return 'full_table'

    def min(self):
        return 'min_table'




def valid_za(document):
    """
    document: koltk.corpus.nikl.annotated.object.Document
    """
    if not hasattr(document, 'ZA') :
        return None

    for za in document.za_list:
        za._error = []

        if len(za.antecedent) > 1 :
            raise Exception('There are more than two antecedents. Use this script only for subject ZA corpus!')

        pred = za.predicate
        subj = za.antecedent[0]
        
        if subj.type != 'subject':
            raise Exception('Non-subject antecedent. Use this script only for subject ZA corpus!')
            

        #
        # check predicate form and begin:end
        #
        sentence = document.getSentenceById(pred.sentence_id)
        word = sentence.wordAt(pred.begin)
        word._za = za

        if sentence.form[pred.slice] != pred.form:
            za._error.append('ErrorZAPredicateFormBeginEnd();')

        #
        # check predicate form
        #
        word = sentence.wordAt(pred.begin)
        if pred.form != word.form:
            if word.form.strip('”고') == pred.form: continue
            if word.form.strip('’고') == pred.form: continue
            if word.form.strip('"고') == pred.form: continue
            if word.form.strip('.,?!\'"“”‘’…') == pred.form : continue
            za._error.append('ErrorZAPredicateForm();')


        if pred.form.endswith('”고') :
            za._error.append('ErrorZAPredicatForm(”고/JKQ);')

        #
        # check predicate form: quotation marks and parentheses
        #
        # ‘ 0x2018
        # ’ 0x2019
        # “ 0x201c
        # ” 0x201D
        # ' 0x27
        #
        # () <> []
        #
        # Error if
        # - predicate form has only one quotation mark
        # - and word form has both quotation marks




        #
        # check if subject form is empty
        #
        if subj.form == '' :
            za._error.append('ErrorZAAntecedentForm(Empty);')
            
        #
        # check subject form and begin:end
        #
        if subj.sentence_id != '-1':
            s = document.getSentenceById(subj.sentence_id)
            if s.form[subj.slice] != subj.form:
                if subj.form == '저' and s.form[subj.slice] == '제': continue
                if subj.form == '나' and s.form[subj.slice] == '내': continue
                if subj.form == '저' and s.form[subj.slice] == '전': continue
                if subj.form == '너' and s.form[subj.slice] == '네': continue
                if subj.form == '나' and s.form[subj.slice] == '난': continue
                if subj.form == '나' and s.form[subj.slice] == '날': continue
                if subj.form == '거' and s.form[subj.slice] == '게': continue
                if subj.form == '거' and s.form[subj.slice] == '건': continue
                if subj.form == '우리' and s.form[subj.slice] == '우린': continue
                za._error.append('ErrorZAAntecedentFormBeginEnd({})'.format(s.form[subj.slice]))


def table(document, spec='min', valid=False):
    """
    document: koltk.corpus.nikl.annotated.object.Document
    """
 
    if spec == 'min':
        return table_min(document, valid=valid)
    else:
        return table_full(document, valid=valid)
        
    
def table_full(document, valid=False):
    """
    document: koltk.corpus.nikl.annotated.object.Document
    """
 
    valid_za(document)
    rows = []
    for sentence in document.sentence_list:
        for word in sentence.word_list:
            if hasattr(word, '_za'):
                pred = word._za.predicate
                ante = word._za.antecedent[0]
                if ante.sentence_id != '-1':
                    ante_sent = document.getSentenceById(ante.sentence_id)
                    ante_sent_fwid = ante_sent.fwid
                else:
                    ante_sent_fwid = '-1'

                pred_form = pred.form
                ante_form = ante.form
                ante_slice_str = ante.slice_str
                za_errors = ''.join(word._za._error)
            else:
                ante_sent_fwid = ''
                pred_form = ''
                ante_form = ''
                ante_slice_str = ''
                za_errors = ''
                
            rows.append('\t'.join([
                sentence.fwid,
                word.slice_str,
                str(word.id),
                word.form,
                pred_form,
                ante_form,
                ante_sent_fwid,
                ante_slice_str,
                za_errors
            ]))

    return '\n'.join(rows)
 

def table_min(document, valid=False):
    """
    document: koltk.corpus.nikl.annotated.object.Document
    """
 
    valid_za(document)
    rows = []
    for sentence in document.sentence_list:
        for word in sentence.word_list:
            if hasattr(word, '_za'):
                pred = word._za.predicate
                ante = word._za.antecedent[0]
                if ante.sentence_id != '-1':
                    ante_sent = document.getSentenceById(ante.sentence_id)
                    ante_sent_fwid = ante_sent.snum
                    try:
                        ante_word = ante_sent.wordAt(ante.begin)
                        ante_word_id = '{}_{}'.format(ante_sent_fwid, ante_word.id)
                    except:
                        ante_word_id = '{}_*begin{}'.format(ante_sent_fwid, ante.begin)
                else:
                    ante_sent_fwid = '-1'
                    ante_word_id = '-1'

                pred_form = pred.form
                ante_str = '{}__@{}'.format(ante.form, ante_word_id)
                za_errors = ''.join(word._za._error)
            else:
                pred_form = ''
                ante_str = ''
                za_errors = ''

            fields = [
                word.gid,
                word.swid,
                word.form,
                pred_form,
                ante_str
            ]
            if valid: fields.append('### ' + za_errors)

            rows.append('\t'.join(fields))

    return '\n'.join(rows)


       
    
