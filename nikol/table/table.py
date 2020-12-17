import builtins
from .object import Document, Sentence, ZA


class Row(dict):
    def __init__(self, 
                sentence: Sentence = None):

        self.__sentence = sentence

    @property
    def document(self):
        return self.sentence.parent

    @property
    def sentence(self):
        return self.__sentence
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

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
        else:
            raise Exception('Need a list of 12 fields. But given : {}'.format(fields))
    
        self.__word = None
        self._word_id = int(self._gid.split('_')[1])

    @property
    def begin(self):
        return self.__begin

    @property
    def end(self):
        return self.__end

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

    @property
    def word(self):
        return self.__word

    @word.setter
    def word(self, value):
        self.__word = value

