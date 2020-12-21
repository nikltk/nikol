"""
"""
import koltk.corpus.nikl.annotated as nikl

class Document(nikl.Document):
    def __init__(self,
                 id: str = None,
                 sentence = [],
                 parent: nikl.Corpus = None,
                 metadata: nikl.DocumentMetadata = None):
        
        if parent is not None or metadata is not None:
            super().__init__(parent=parent, metadata=metadata)

        self.id = id
        self.sentence = sentence

    @property
    def _rows(self):
        for sent in self.sentence:
            for row in sent._rows:
                yield row

    @property
    def sentence_list(self):
        return self.sentence
        
    @property
    def za_list(self):
        if not hasattr(self, 'ZA'):
            self.process_za()

        return self.ZA
        
    def process_za(self):
        row1 = self.sentence_list[0]._rows[0]
        if row1._za_pred is None and row1._za_ante is None:
            self.ZA = []
        else:
            self.ZA = ZA.process_docrows(self) 
  

class Sentence(nikl.Sentence):

    def __init__(self, 
                id: str = None, 
                form: str = None,
                sentrows = None,
                parent: Document = None):
        super().__init__(parent=parent)
        self.id = id
        self.form = form
        self.word = []
        self.__rows = sentrows

    def process(self, sentrows):
        self.WSD = []

        morph_id = 0
        for row in sentrows:
            # WSD
            for wsd in row.ls.split(' + '):
                self.WSD.append(wsd)

        for row in sentrows:
            # SRL:
            if row.sr_pred is None and row.sr_args is None:
                pass
            elif row.sr_pred != '' or row.sr_args != '':
                s = SRL(row.sr_pred, row.sr_args, w, parent=self)
                self.SRL.append(s)
                
                
               
    @property
    def _rows(self):
        return self.__rows

    @property
    def word_list(self):
        #if not hasattr(self, 'word'):
        #    self.process_word()

        return self.word

    #def process_word(self):
    #    sentrows = self._rows
    #    self.word = []
    #    for row in sentrows:
    #        w = Word(row, parent=self)
    #        row.word = w
    #        self.word.append(w)


    @property 
    def morpheme_list(self):
        if not hasattr(self, 'morpheme'):
            self.process_morpheme()

        return self.morpheme

    def process_morpheme(self):
        self.morpheme = Morpheme.process_sentrows(self._rows)

    @property 
    def ls_list(self):
        if not hasattr(self, '_ls'):
            self.process_ls()

        return self._ls

    def process_ls(self):
        self._ls = WSD.process_sentrows(self._rows, morpheme_as_wsd=True)

    @property
    def wsd_list(self):
        if not hasattr(self, 'WSD'):
            self.process_wsd_and_morpheme()

        return self.WSD
            
    def process_wsd_and_morpheme(self):
        self.morpheme, self.WSD = WSD.process_sentrows(self._rows)

    @property 
    def ne_list(self):
        if not hasattr(self, 'NE'):
            self.process_ne()

        return self.NE

    def process_ne(self):
        self.NE = NE.process_sentrows(self._rows)

    @property
    def dp_list(self):
        if not hasattr(self, 'DP'):
            self.process_dp()

        return self.DP

    def process_dp(self):
        self.DP = DP.process_sentrows(self._rows)

    @property
    def srl_list(self):
        if not hasattr(self, 'SRL'):
            self.process_srl()

        return self.SRL

    def process_srl(self):
        self.SRL = SRL.process_sentrows(self._rows)


class Word(nikl.Word):
    """
    parent: Sentence
    id
    form
    begin
    end
    """
    def __init__(self, 
                id,
                form,
                begin,
                end,
                parent: Sentence = None,
                ):
        super().__init__(parent=parent)
        #self.__row = row
        self.__parent = parent
        self.id = id #row._word_id
        self.form = form #row._form
        self.begin = begin #row.begin
        self.end = end #row.end

    @classmethod
    def from_min(cls, 
                row,
                begin,
                end,
                parent: Sentence):

        word = cls(parent=parent, id=row._word_id, form=row._form, begin=begin, end=end)
        row.word = word
        word._row = row
        return word


class Morpheme(nikl.Morpheme):
    def __init__(self,
                 parent: Sentence,
                 id: int,
                 form: str,
                 label: str,
                 word_id: int,
                 position: int,
                 row = None):
        super().__init__(parent=parent, id=id, form=form, label=label, word_id=word_id, position=position)
        self._row = row

    @classmethod
    def from_min(cls,
                 morph_str: str,
                 id: int = None,
                 row = None,
                 position: int = None):
        
        slash_idx = morph_str.rfind('/')
        form = morph_str[:slash_idx]
        label = morph_str[(slash_idx+1):]

        if row is not None:
            parent = row.sentence
            word_id = row.word.id
        else:
            parent = None
            word_id = None

        return cls(parent=parent, id=id, form=form, label=label,
                   word_id=word_id, position=position, row=row)

    @classmethod
    def process_sentrows(cls, sentrows):
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            return Morpheme.process_min_sentrows(sentrows)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows(cls, sentrows):
        morphemes = []
        morph_id = 0
        for row in sentrows:
            row_morphs = []
            for (p, morph_str) in enumerate(row._mp.split(' + ')):
                morph_id += 1
                m = cls.from_min(morph_str, id=morph_id, position=p+1, row=row)
                row_morphs.append(m)

            row.morphemes = row_morphs
            morphemes += row_morphs

        return morphemes

class WSD(nikl.WSD):
    def __init__(self,
                 parent: Sentence = None,
                 word: str = None,
                 sense_id: int = None,
                 pos : str = None,
                 begin: int = None,
                 end: int = None,
                 row = None):
 
        super().__init__(parent=parent, word=word, sense_id=sense_id, pos=pos, begin=begin, end=end)
        self._row = row

    @classmethod
    def from_min(cls,
                 ls_str: str,
                 begin: int = None,
                 end: int = None,
                 row = None):
        
        slash_idx = ls_str.rfind('/')
        pos = ls_str[(slash_idx+1):]
        form_sense = ls_str[:slash_idx].split('__')

        if len(form_sense) == 1:
            form = form_sense[0]
            sense_id = None
        elif len(form_sense) == 2:
            form = form_sense[0]
            sense_id = int(form_sense[1])
        else:
            raise Exception('Illegal ls_str: {}'.format(ls_str))

        if row is not None:
            parent = row.sentence
        else:
            parent = None

        return cls(parent=parent, word=form, sense_id=sense_id, pos=pos,
                   begin=begin, end=end, row=row)

    @classmethod
    def process_sentrows(cls, sentrows, morpheme_as_wsd=False):
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            if morpheme_as_wsd:
                return WSD.process_min_sentrows_ls(sentrows)
            else:
                return WSD.process_min_sentrows_wsd_and_morpheme(sentrows)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows_ls(cls, sentrows):
        lss = []
        for row in sentrows:
            row_lss = []
            beg = 0
            for (p, ls_str) in enumerate(row._ls.split(' + ')):
                l = cls.from_min(ls_str, row=row)
                begin = row.word.begin + beg
                end = begin + len(l.word)
                l.begin = begin
                l.end = end
                row_lss.append(l)
                beg += len(l.word)

            row.lss = row_lss
            lss += row_lss

        return lss

    @classmethod
    def process_min_sentrows_wsd_and_morpheme(cls, sentrows):
        wsds = []
        morphemes = []
        morph_id = 0
        for row in sentrows:
            beg = 0
            for (p, ls_str) in enumerate(row._ls.split(' + ')):
                morph_id += 1
                if ls_str.find('__') != -1:
                    #
                    # TODO: begin, end
                    #
                    l = cls.from_min(ls_str, row=row)
                    l.begin = row.word.begin + beg
                    l.end = l.begin + len(l.word)
                    l.word_id = row.word.id
                    wsds.append(l)

                    morph_str = '{}/{}'.format(l.word, l.pos)
                    m = Morpheme.from_min(morph_str, id=morph_id, position=p+1, row=row)
                    morphemes.append(m)

                    beg += len(l.word)
                else:    
                    m = Morpheme.from_min(ls_str, id=morph_id, position=p+1, row=row)
                    morphemes.append(m)

                    beg += len(m.form)

        return morphemes, wsds 


class NE(nikl.NE):
    def __init__(self,
                 parent: Sentence = None,
                 id: int = None,
                 form: str = None,
                 label: str = None,
                 begin: int = None,
                 end: int = None,
                 row = None):
        super().__init__(parent=parent, id=id, form=form, label=label, begin=begin, end=end)
        self._row = row

    @classmethod
    def parse_ne_str(cls, ne_str):
        
        slash_idx = ne_str.rfind('/')
        if slash_idx == -1:
            raise ValueError("invalid literal for ne_str: '{}\'".format(ne_str))

        form = ne_str[:slash_idx]
        label_beg = ne_str[(slash_idx+1):].split('@')
        if len(label_beg) == 1:
            label = label_beg[0]
            beg = None
        elif len(label_beg) == 2:
            label = label_beg[0]
            beg = int(label_beg[1].strip('()'))
        else:
            raise ValueError('invalid liter for ne_str: \'{}\''.format(ne_str))

        return {'form' : form, 'label' : label, 'begin_within_word' : beg }
        
    @classmethod
    def from_min(cls,
                 ne_str: str,
                 id: int,
                 row):
        
        parsed = NE.parse_ne_str(ne_str)
        form = parsed['form']
        label = parsed['label']
        beg = parsed['begin_within_word']

        slash_idx = ne_str.rfind('/')
        form = ne_str[:slash_idx]

        #
        # TODO: compute begin and end
        #
        if beg is None:
            w1 = form.split()[0]
            beg = row.word.form.find(w1)
                
        if beg == -1:
            beg = 0
            #raise Exception(ne_str, form, label, beg, row)

        parent = row.sentence
        begin = row.word.begin + beg
        end = begin + len(form) 

        return cls(parent=parent, id=id, form=form, label=label, begin=begin, end=end, row=row) 

    @classmethod
    def process_sentrows(cls, sentrows):
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            return NE.process_min_sentrows(sentrows)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows(cls, sentrows):
        nes = []
        ne_id = 0
        for row in sentrows:
            row_nes = []
            if row._ne == '' or row._ne == '&':
                row.nes = None
                continue
            for ne_str in row._ne.split(' + '):
                if ne_str == '&' : continue
                ne_id += 1
                n = cls.from_min(ne_str, id=ne_id, row=row)
                row_nes.append(n)

            row.nes = row_nes
            nes += row_nes

        return nes
 
        


class DP(nikl.DP):
    def __init__(self,
                 parent: Sentence = None,
                 word_id: int = None,
                 word_form: str = None,
                 head: int = None,
                 label: str = None,
                 dependent = [],
                 row = None):
        super().__init__(parent=parent, word_id=word_id, word_form=word_form, head=head, label=label, dependent=dependent)
        self._row = row

    @classmethod
    def from_min(cls, row):
        return cls(parent = row.sentence,
                   word_id = row.word.id,
                   word_form = row.word.form,
                   head = row._dp_head,
                   label = row._dp_label,
                   dependent = [],
                   row = row)
        
    @property
    def _word(self):
        return self.__word

    @classmethod
    def process_sentrows(cls, sentrows):
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            return DP.process_min_sentrows(sentrows)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows(cls, sentrows):
        dps = []
        for row in sentrows:
            d = DP.from_min(row)
            row.dp = d
            dps.append(d)

            

        for dp in dps:
            if dp.head != -1:
                head_node = dps[dp.head - 1]
                head_node.dependent.append(dp.word_id)

        return dps


class SRL(nikl.SRL):
    def __init__(self,
                 parent: Sentence = None,
                 predicate: nikl.SRLPredicate = None,
                 argument_list = None,
                 row = None):
        
        super().__init__(parent=parent)
        self.predicate = predicate
        self.argument = argument_list
        self._row = row

    @classmethod
    def from_min(cls, row):
        srl = cls(parent=row.sentence, row=row)

        pred_str = row._sr_pred
        args_str = row._sr_args
        word = row.word
        parent = row.sentence

        #
        # predicate
        #
        predicate = nikl.SRLPredicate(parent=srl)
        pred_lemma, pred_sense_id = pred_str.split('__')
        predicate.lemma = pred_lemma
        try:
            predicate.sense_id = int(pred_sense_id)
        except:
            predicate.sense_id = pred_sense_id

        # form processing...
        predicate.form = word.form
        predicate.begin = word.begin
        predicate.end = word.end

        #
        # arguments
        #
        arguments = []
        for arg_str in args_str.split():
            
            slash = arg_str.rfind('/')
            arg_form = arg_str[:slash]
            label_wordrange_str = arg_str[(slash+1):]
            label, wordrange_str = label_wordrange_str.split('__')
            wordids = wordrange_str.lstrip('@').split('-')
            w1 = parent.word_list[int(wordids[0]) - 1]
            w2 = parent.word_list[int(wordids[1]) - 1] if len(wordids) == 2 else w1
            
            arg = nikl.SRLArgument(parent=srl)
            arg.begin = w1.begin
            arg.end = w2.begin + len(arg_form)
            arg.form = parent.form[arg.begin:arg.end]
            arg.label = label

            arguments.append(arg)

        srl.predicate = predicate
        srl.argument = arguments

        return srl 

    @classmethod
    def process_sentrows(cls, sentrows):
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            return SRL.process_min_sentrows(sentrows)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows(cls, sentrows):
        srls = []
        for row in sentrows:
            if row._sr_pred is None and row._sr_args is None:
                row.srl = None
                continue
            elif row._sr_pred == '' and row._sr_args == '':
                row.srl = None
                continue
            srl = SRL.from_min(row)
            row.srl = srl
            srls.append(srl)

        return srls
            
            
    @property
    def _word(self):
        return self.__word


class ZA(nikl.ZA):
    def __init__(self,
                 parent: Document = None,
                 predicate = None,
                 antecedent_list = None,
                 row = None):
        super().__init__(parent=parent)
        self.predicate = predicate
        self.antecedent = antecedent_list
        self._row = row

    @classmethod
    def from_min(cls, row, parent: Document = None):
        pred_str = row._za_pred
        ante_str = row._za_ante
        doc = row.document

        za = cls(parent=parent, row=row)


        #
        # predicate
        #
        # TODO: begin, end
        pred_word = row.word
        beg = pred_word.form.find(pred_str)
        if beg == -1:
            pred_begin = pred_word.begin
            pred_end = pred_word.end
        else:
            pred_begin = pred_word.begin + beg
            pred_end = pred_begin + len(pred_str)
        
        za.predicate = nikl.ZAPredicate(parent=za, form=pred_str, sentence_id=row.sentence.id,
                                        begin=pred_begin, end=pred_end)

        #
        # antecendent
        #
        # TODO: begin, end
        ante_form, ante_swid = ante_str.split('__@')
        if ante_swid == '-1':
            ante_sent_id = '-1'
            ante_begin = -1
            ante_end = -1
        else:
            ante_sid, ante_wid = ante_swid.split('_')
            ante_sid = int(ante_sid.lstrip('s'))
            ante_wid = int(ante_wid)

            ante_sent = doc.sentence_list[ante_sid - 1]
            ante_sent_id = ante_sent.id

            ante_word = ante_sent.word_list[ante_wid - 1]
            beg = ante_word.form.find(ante_form)

            if beg == -1 :
                #print('ERROR', ante_form, ante_word, ante_word._row.morphemes)
                ante_begin = ante_word.begin
                ante_end = ante_word.end
            else:    
                ante_begin = ante_word.begin + beg
                ante_end = ante_begin + len(ante_form)


        za.antecedent = [nikl.ZAAntecedent(parent=za, form=ante_form, type='subject', sentence_id=ante_sent_id,
                                           begin=ante_begin, end=ante_end)] 

        return za

 
    @classmethod
    def from_full(cls, row, parent: Document = None):
        pass

    @classmethod
    def process_docrows(cls, document):
        if type(document.sentence_list[0]._rows[0]).__name__ == 'UnifiedMinRow':
            return ZA.process_min_docrows(document)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_docrows(cls, document):

        # if za columns do not exist
        #if docrows[0]._za_pred is None and docrows[0]._za_ante is None:
        #    return None
        
        zas = []
        for row in document._rows:
            if row._za_pred != '' or row._za_ante != '':
                z = ZA.from_min(row, parent=document)
                row.za = z
                zas.append(z)

        return zas
 

 
