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
        return self.__rows

    @property
    def sentence_list(self):
        return self.sentence
        
    @property
    def za_list(self):
        if not hasattr(self, 'ZA'): self.process_za()

        return self.ZA
        
    def process_za(self):
        docrows = self._rows

        # if za columns do not exist
        if docrows[0]._za_pred is None and docrows[0]._za_ante is None:
            return None
        
        self.ZA = []
        for row in docrows:
            za = row.za
            if za is not None: self.ZA.append(za)

            #if row.za_pred != '' or row.za_ante != '':
            #    za = ZA(row, parent=self)
            #    self.ZA.append(za)

   

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
    pass

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
    def from_min(cls,
                 ne_str: str,
                 id: int = None,
                 row = None):
        
        slash_idx = ne_str.rfind('/')
        form = ne_str[:slash_idx]

        #
        # beg: begin character index within a word
        #
        # TODO: compute begin
        #
        label_beg = ne_str[(slash_idx+1):].split('@')
        if len(label_beg) == 1:
            label = label_beg[0]
            w1 = form.split()[0]
            beg = row.word.form.find(w1)
                
        elif len(label_beg) == 2:
            label = label_beg[0]
            beg = int(label_beg[1].strip('()'))
        else:
            raise Exception('Illegal ne_str: {}'.format(ne_str))
                
        if beg == -1:
            pass
            #raise Exception(ne_str, form, label, beg, row)





        if row is not None:
            parent = row.sentence
            begin = row.word.begin + beg
            end = begin + len(form) 
        else:
            parent = None
            begin = None
            end = None

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
                row,    
                parent: Document = None):
        super().__init__(parent=parent)
        self.__row = row
        self.__row.za = self

    @classmethod
    def from_minspec(cls, row, parent: Document = None):
        za = cls(row, parent=parent)
        za.predicate = nikl.ZAPredicate(parent=za)
        za.predicate.form = row._za_pred
        za.predicate.sentence_id = row.sentence.id
        za.antecedent = [] 
        return za

    @classmethod
    def from_fullspec(cls, row, parent: Document = None):
        pass

    def _row(self):
        return self.__row
    
