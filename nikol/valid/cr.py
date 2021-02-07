# cr.py
#
# from scripts/valid-2/valid-2-cr.py
#
# Author: yhj
#

"""
Validation Level 2 of CR corpus

Usage: valid-2-cr SXCR1902005140.json  


JSON
================

sentence
  words
CR 
  mention
    { sentence_id, form, mention: null, begin, end, word_ids, ne_id: -1 }

"""
from . import util


def table(document, spec='min', valid=False):
    rows = []
    for cr in document.cr_list:
        antecedent = cr.mention_list[0]
        ante_sent = document.getSentenceById(antecedent.sentence_id)

        for mention in cr.mention_list:
            if not hasattr(mention, '_error'):
                mention._error = []

            if mention.form.strip() != mention.form:
                mention._error.append('ErrorCRMentionForm(strip);')
            sent = document.getSentenceById(mention.sentence_id)


            if mention.slice.start == -1:
                mention._error.append('ErrorCRMentionBeginEnd();')
            elif sent.form[mention.slice] != mention.form:
                try: 
                    if util.form_match(mention.form, sent.form, mention.slice): continue
                except Exception as e:
                    if valid:
                        raise Exception('''sentence.id: {}\nsentence.form: {}\nmention.form: {}\nmention.slice: {}'''
                                        .format(sent.id,
                                                sent.form,
                                                mention.form, mention.slice, str(e)))


                
                mention._error.append('ErrorCRMentionForm({});'.format(sent.form[mention.slice]))

            try:
                if mention.begin < 0:
                    w1_id = '?'
                else:
                    w1 = sent.wordAt(mention.begin)
                    w1_id = w1.id
            except Exception as e:
                w1_id = '?'
                mention._error.append('ErrorCRMentionBeginEnd({});'.format(sent.form[mention.slice]))
                
            if len(mention.form.split()) == 1:
                word_range = '{}'.format(w1_id)
            else:
                try:
                    wn = sent.wordAt(mention.end - len(mention.form.split()[-1]))
                    word_range = '{}-{}'.format(w1_id, wn.id)
                except Exception as e:
                    word_range = '{}-?'.format(w1_id)
                    mention._error.append('ErrorCRMentionBeginEnd({});'.format(sent.form[mention.slice]))

                
            if spec == 'full' :
                fields = [ante_sent.fwid,
                    antecedent.slice_str,
                    sent.fwid,
                    mention.slice_str,
                    #sent.snum,
                    #w1.id,
                    #wn.id,
                    mention.form
                ]
            elif spec == 'min' :
                
                sent_form = '{}___{}___{}'.format(
                    sent.form[:mention.slice.start],
                    sent.form[mention.slice],
                    sent.form[mention.slice.stop:]
                )

                fields = [
                     '{}_{:03d}:{:03d}'.format(ante_sent.fwid, antecedent.slice.start, antecedent.slice.stop),
                     '{}_{:03d}:{:03d}'.format(sent.fwid, mention.slice.start, mention.slice.stop),
                     sent.snum,
                    word_range,
                     mention.form,
                     '### {} {}'.format(sent.snum, sent_form)
                ]
                
            if valid : fields.append(''.join(mention._error))

            rows.append('\t'.join(fields))

    return '\n'.join(rows)



def table_full():
            print(document.fwid, ante_sent.dsid, #ante_sent.fwid,
                  antecedent.slice_str,
                  sent.dsid, #sent.fwid,
                  mention.slice_str,
                  #reader.basename.rstrip('.json'),
                  mention.form,
                  '### ' + ''.join(mention._error),
                  sent.dsid,
                  sent.form,
                  sep='\t')
