"""
"""
import koltk.corpus.nikl.annotated as nikl

class Row(nikl.Niklanson):
    def __init__(self, fields = None, **kwargs):
        """ Row represents a line of unified min table data. 
        Consists of 12 fields: gid, swid, form, mp, ls, ne, za_pred, za_ante, dp_label, dp_head, sr_pred, sr_args.
        """
        if type(fields) is list and len(fields) == 12:
            (self.gid, self.swid, self.form,
             self.mp, self.ls, self.ne,
             self.za_pred, self.za_ante,
             self.dp_label, self.dp_head,
             self.sr_pred, self.sr_args) = fields
        else:
            raise Exception('Need a list of 12 fields. But given : {}'.format(fields));

        for name in kwargs:
            setattr(self, name, kwargs[name])
 
class Document(nikl.Document):
    def __init__(self, docrows):
        """
        :param docrows: list of Rows in the document
        """
        self.__rows = docrows
        self.sentence = None

    @property
    def _rows(self):
        return self.__rows
    
    @property
    def za_list(self):
        if not hasattr(self, 'ZA'): self.process_za()

        return self.ZA
        
    def process_za(self):
        docrows = self._rows

        # if za columns do not exist
        if docrows[0].za_pred is None and docrows[0].za_ante is None:
            return None
        
        self.ZA = []
        for row in docrows:
            if row.za_pred != '' or row.za_ante != '':
                za = ZA(row, parent=self)
                self.ZA.append(za)

    @property
    def sentence_list(self):
        if self.sentence is None: self.process_sentence()

        return self.sentence
    
    def process_sentence(self):
        docrows = self._rows
        self.sentence = []
        prev_sid = None
        sentrows = []
        for row in docrows:
            sid, wid = row.gid.split('_')
            if prev_sid is None:
                sentrows = [row]
            elif sid != prev_sid:
                self.sentence.append(Sentence(sentrows))
                sentrows = [row]
            else:
                sentrows.append(row)

            prev_sid = sid

        self.sentence.append(Sentence(sentrows))


class Sentence(nikl.Sentence):
    def __init__(self, sentrows):
        self.__rows = sentrows
        
        self.id = sentrows[0].gid.split('_')[0]
        self.form = ' '.join([row.form for row in sentrows])
        
    def process(self):
        self.word = []
        self.morpheme = []
        self.WSD = []
        self.NE = []
        self.DP = []
        self.SRL = []

        b = e = 0
        morph_id = 0
        for row in sentrows:
            # word
            e = b + len(row.form)
            w = Word(row, begin=b, end=e, parent=self)
            self.word.append(w)
            b = e + 1

            # morpheme
            for (p, morph_str) in enumerate(row.mp.split(' + ')):
                morph_id += 1
                m = Morpheme(morph_str, id=morph_id, word=w, position=p+1, parent=self)
                self.morpheme.append(m)

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
        if self.word is None:
            self.word = []
            for row in self.rows:
                self.word.append(Word(row))

        return self.word

class Word(nikl.Word):
    def __init__(self, row, begin = None, end = None, parent=None):
        super().__init__(parent=parent)
        self.__row = row
        self.__parent = parent
        self.id = int(row.gid.split('_')[1])
        self.form = row.form
        self.begin = begin
        self.end = end

    @property
    def _row(self):
        return self.__row

    @property
    def gid(self):
        return self.__row.gid

class Morpheme(nikl.Morpheme):
    def __init__(self,
                 morph_str : str,
                 id : int = None,
                 word : Word = None,
                 position : int = None,
                 parent=None):
        super().__init__(parent=parent)
        self.id = id
        slash_idx = morph_str.rfind('/')
        self.form = morph_str[:slash_idx]
        self.label = morph_str[(slash_idx+1):]
        self.__word = word
        self.word_id = word.id if word is not None else None
        self.position = position 
        
    @property
    def _word(self):
        return self.__word

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
        
        self.predicate = nikl.ZAPredicate(parent=self)
        self.predicate.form = row.za_pred
        self.predicate.sentence_id = row.gid.split('_')[0]
        
        self.antecedent = [] 

    def _row(self):
        return self.__row
    
