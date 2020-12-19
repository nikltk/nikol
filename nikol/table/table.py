import builtins
from .object import Document, Sentence, ZA


class Row:
    def __init__(self, 
                sentence: Sentence = None):

        self.__sentence = sentence

    @property
    def document(self):
        return self.sentence.parent

    @property
    def sentence(self):
        return self.__sentence

    def __repr__(self):
        return repr(self.__dict__)

class UnifiedMinRow(Row):
    def __init__(self, 
                fields, 
                sentence = None,
                ):
        """ Row represents a line of unified min table data. 

        :param fields: list of 12 fields (strings): gid, swid, form, mp, ls, 
               ne, za_pred, za_ante, dp_label, dp_head, sr_pred, sr_args.
        """
        super().__init__(sentence = sentence)
        if type(fields) is list and len(fields) == 12:
            (self._gid, self._swid, self._form,
             self._mp, self._ls, self._ne,
             self._za_pred, self._za_ante,
             self._dp_label, self._dp_head,
             self._sr_pred, self._sr_args) = fields
            
            self._dp_head = int(self._dp_head)
        else:
            raise Exception('Need a list of 12 fields. But given : {}'.format(fields))
    
        self._word_id = int(self._gid.split('_')[1])



    @property
    def begin(self):
        return self.__begin

    @property
    def end(self):
        return self.__end

    @property
    def dp(self):
        if not hasattr(self, '__dp'):
            self.sentence.process_dp()

        return self.__dp

    @dp.setter
    def dp(self, value):
        self.__dp = value


    @property
    def morphemes(self):
        if not hasattr(self, '__morphemes'):
            self.sentence.process_morpheme()

        return self.__morphemes

    @morphemes.setter
    def morphemes(self, value):
        self.__morphemes = value


    @property
    def za(self):
        if not hasattr(self, '__za'):
            if self._za_pred is None and self._za_ante is None:
                self.__za = None
            elif self._za_pred == '' and self._za_ante == '':
                self.__za = None
            else:
                self.__za = ZA.from_minspec(self, parent=self.sentence)

        return self.__za
       
