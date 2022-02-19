"""Nikol Table Rows
"""
import builtins
from .object import Document, Sentence, ZA


class Row:
    def __init__(self, 
                 id: int = None,
                 parent=None):

        self._id = id
        self.__parent = parent

    def __repr__(self):
        return repr(self.__dict__)

    @property
    def parent(self):
        return self.__parent
    
    @property
    def prev(self):
        return self.neighborAt(-1)

    @property
    def next(self):
        return self.neighborAt(1)

    def __next__(self):
        return self.neighborAt(1)
    
    def neighborAt(self, relative_index):
        """
        Return neighbor row at the relative_index. Or default if index is out of range.
        
        :param relative_index: eg) +1 for the next row, -1 for the previous row. 
        """
        ind = self._id - 1 + relative_index
        
        if 0 <= ind < len(self.sentence._rows):
            return self.sentence._rows[ind]
        else:
            raise IndexError('list index out of range')
        
    def neighbors(self, first=None, last=None, mapf=None, filterf=None):
        """
        Return list of the neighbor rows from first to last.
        
       :param first: first relative index 
       :param last: last relative index 
        """
        ind1 = max(0, self._id - 1 + first) if first is not None else 0
        ind2 = self._id + last if last is not None else len(self.sentence._rows)

        if mapf is not None and filterf is not None:
            return [mapf(x) for x in self.sentence._rows[ind1:ind2] if filterf(x)]
        elif mapf is not None and filterf is None:
            return [mapf(x) for x in self.sentence._rows[ind1:ind2]]
        elif mapf is None and filterf is not None:
            return [x for x in self.sentence._rows[ind1:ind2] if filterf(x)]
        else:
            return self.sentence._rows[ind1:ind2]
        

class UnifiedMinRow(Row):
    def __init__(self, 
                fields, 
                sentence = None,
                ):
        """ Row represents a line of unified min table data. 

        :param fields: list of 12 fields (strings): gid, swid, form, mp, ls, 
               ne, za_pred, za_ante, dp_label, dp_head, sr_pred, sr_args.
        """
        if type(fields) is list and len(fields) == 12:
            (self._gid, self._swid, self._form,
             self._mp, self._ls, self._ne,
             self._za_pred, self._za_ante,
             self._dp_label, self._dp_head,
             self._sr_pred, self._sr_args) = fields
            
            self._word_id = int(self._gid.split('_')[1])
            self._id = self._word_id
            self._dp_head = int(self._dp_head) if self._dp_head is not None else None

            super().__init__(id=self._id, parent=sentence)
        else:
            raise Exception('Need a list of 12 fields. But given : {}'.format(fields))
    
        self.__morphemes = None

    @property
    def document(self):
        return self.sentence.parent

    @property
    def sentence(self):
        return super().parent

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


