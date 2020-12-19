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
        self.morpheme = []
        self.WSD = []
        self.NE = []
        self.DP = []
        self.SRL = []

        morph_id = 0
        for row in sentrows:
            # WSD
            for wsd in row.ls.split(' + '):
                self.WSD.append(wsd)

            # NE
            if row.ne != '' and row.ne != '&':
                for ne in row.ne.split(' + '):
                    self.NE.append(ne)

            # DP: 
            if row.dp_label is None and row.dp_head is None:
                pass
            else:
                d = DP(word=w, head=row.dp_head, label=row.dp_label, dependent=[], parent=self)
                self.DP.append(d)

        for row in sentrows:
            # SRL:
            if row.sr_pred is None and row.sr_args is None:
                pass
            elif row.sr_pred != '' or row.sr_args != '':
                s = SRL(row.sr_pred, row.sr_args, w, parent=self)
                self.SRL.append(s)
                
                
        # DP: add dependent        
        if self.DP != []:
            for dp in self.DP:
                if dp.head != -1:
                    dp.head_node.dependent.append(dp.word_id)
                
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
            row.morphemes = []
            for (p, morph_str) in enumerate(row._mp.split(' + ')):
                morph_id += 1
                m = cls.from_min(morph_str, id=morph_id, position=p+1, row=row)
                row.morphemes.append(m)
                morphemes.append(m)

        return morphemes

class WSD(nikl.WSD):
    pass

class NE(nikl.NE):
    pass


class DP(nikl.DP):
    def __init__(self,
                 word: Word = None,
                 head: int = None,
                 label: str = None,
                 dependent = None,
                 parent: Sentence = None):
        super().__init__(parent=parent)
        self.__word = word
        self.word_id = word.id
        self.word_form = word.form
        self.head = int(head)
        self.label = label
        self.dependent = dependent
        
    @property
    def _word(self):
        return self.__word

class SRL(nikl.SRL):
    def __init__(self,
                pred_str,
                args_str,
                 word,
                parent: Sentence = None):
        
        super().__init__(parent=parent)
        self.__word = word

        #
        # predicate
        #
        self.predicate = nikl.SRLPredicate(parent=self)
        pred_lemma, pred_sense_id = pred_str.split('__')
        self.predicate.lemma = pred_lemma
        try:
            self.predicate.sense_id = int(pred_sense_id)
        except:
            self.predicate.sense_id = pred_sense_id

        # form processing...
        self.predicate.form = word.form
        self.predicate.begin = word.begin
        self.predicate.end = word.end

        #
        # arguments
        #
        self.argument = []
        for arg_str in args_str.split():
            
            slash = arg_str.rfind('/')
            arg_form = arg_str[:slash]
            label_wordrange_str = arg_str[(slash+1):]
            label, wordrange_str = label_wordrange_str.split('__')
            wordids = wordrange_str.lstrip('@').split('-')
            w1 = self.parent.word_list[int(wordids[0]) - 1]
            w2 = self.parent.word_list[int(wordids[1]) - 1] if len(wordids) == 2 else w1
            
            arg = nikl.SRLArgument(parent=self)
            arg.begin = w1.begin
            arg.end = w2.begin + len(arg_form)
            arg.form = self.parent.form[arg.begin:arg.end]
            arg.label = label

            self.argument.append(arg)

            
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
    
