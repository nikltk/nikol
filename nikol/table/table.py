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
            
            self._dp_head = int(self._dp_head) if self._dp_head is not None else None
        else:
            raise Exception('Need a list of 12 fields. But given : {}'.format(fields))
    
        self._word_id = int(self._gid.split('_')[1])
        self.__morphemes = None



    @property
    def begin(self):
        return self.__begin

    @property
    def end(self):
        return self.__end

    @property
    def morphemes(self):
        if not hasattr(self, '_UnifiedMinRow__morphemes'):
            self.sentence.process_morpheme()

        return self.__morphemes

    @morphemes.setter
    def morphemes(self, value):
        self.__morphemes = value

    @property
    def lss(self):
        if not hasattr(self, '_UnifiedMinRow__lss'):
            self.sentence.process_ls()

        return self.__lss

    @lss.setter
    def lss(self, value):
        self.__lss = value


    @property
    def nes(self):
        if not hasattr(self, '_UnifiedMinRow__nes'):
            self.sentence.process_ne()

        return self.__nes

    @nes.setter
    def nes(self, value):
        self.__nes = value

    @property
    def dp(self):
        if not hasattr(self, '_UnifiedMinRow__dp'):
            self.sentence.process_dp()

        return self.__dp

    @dp.setter
    def dp(self, value):
        self.__dp = value

    @property
    def srl(self):
        if not hasattr(self, '_UnifiedMinRow__srl'):
            self.sentence.process_srl()

        return self.__srl

    @srl.setter
    def srl(self, value):
        self.__srl = value

    @property
    def za(self):
        if not hasattr(self, '_UnifiedMinRow__za'):
            self.document.process_za()

        return self.__za

    @za.setter
    def za(self, value):
        self.__za = value

      
