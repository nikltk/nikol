"""Nikol Table Tag Strings
"""
import re
from koltk.corpus.nikl.annotated.tag import POS_TAGS, NE_TAGS, SYN_TAGS, FUN_TAGS, SR_TAGS


class NikolTableTagString(dict):
    def __init__(self, x = None, **kwargs):
        """
        """
        if x is None:
            self.update(kwargs)
        elif type(x) is str:
            self.update(**self.parse(x))
        elif type(x) is dict:
            self.update(**dict)
    
    @property
    def str(self):
        return self.__str__()
            
    def __getattr__(self, name):
        if not name.startswith('_'):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name)
        else:
            try:
                return super().__getattr__(name)
            except KeyError:
                raise AttributeError(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self[name] = value
            
    def __delattr__(self, name):
        if name.startswith('_'):
            super().__delattr__(name)
        else:
            del self[name]



class MP_str(NikolTableTagString):
    @classmethod
    def parse(cls, mp_str):
        """
        :param mp_str: example) 'HHH/NNP', '//SP'
        """
        morph_str = mp_str
        try:
            slash_idx = morph_str.rfind('/')
            form = morph_str[:slash_idx]
            label = morph_str[(slash_idx+1):]
        except:
            raise ValueError("invalid literal for mp_str: '{}'".format(mp_str))

        if label not in POS_TAGS:
            raise ValueError("invalid label for mp_str: '{}'".format(mp_str))

        return {'form' : form, 'label': label}
        
    def __str__(self):
        return '{form}/{label}'.format(**self)


class LS_str(NikolTableTagString):
    @classmethod
    def parse(cls, ls_str):
        """
        :param ls_str: eg) '한글__001/NNG', '가/JKS'
        :return: eg) {'form': '한글', 'sense_id': 1, 'pos': 'NNG'}, {'form': '가', 'sense_id': None, 'pos': 'JKS'}
        """
        try:
            slash_idx = ls_str.rfind('/')
            pos = ls_str[(slash_idx+1):]
            form_sense = ls_str[:slash_idx].split('__')
        except:
            raise ValueError("invalid literal for ls_str: '{}'".format(ls_str)) 

        if pos not in POS_TAGS:
            raise ValueError("invalid pos for ls_str: '{}'".format(ls_str))

        if len(form_sense) == 1:
            form = form_sense[0]
            sense_id = None
        elif len(form_sense) == 2:
            form = form_sense[0]
            try:
                sense_id = int(form_sense[1])
            except:
                raise ValueError("invalid sense_id for ls_str: '{}'".format(ls_str)) 

            if len(form_sense[1]) != 3:
                raise ValueError("invalid sense_id literal for ls_str: '{}'".format(ls_str)) 
            
            if not (0 < sense_id < 90 or sense_id in [777, 888, 999]):
                raise ValueError("invalid sense_id for ls_str: '{}'".format(ls_str)) 

        else:
            raise ValueError("invalid literal for ls_str: '{}'".format(ls_str)) 
        

        return {'form' : form, 'sense_id' : sense_id, 'pos' : pos }
        
    def __str__(self):
        if hasattr(self, 'sense_id') and self.sense_id is not None:
            return '{form}__{sense_id:03d}/{pos}'.format(**self)
        else:
            return '{form}/{pos}'.format(**self)

class NE_str(NikolTableTagString):
    @classmethod
    def parse(cls, ne_str):
        """
        :param ne_str: eg) 'HHH/PS@(0)'
        :type ne_str: str
        
        :return: eg) {'form' : 'HHH', 'label' : 'PS', 'begin_within_word' : 0 }
        :rtype: NE_str
        """
 
        slash_idx = ne_str.rfind('/')
        if slash_idx == -1:
            raise ValueError("invalid literal for ne_str: '{}'".format(ne_str))

        form = ne_str[:slash_idx]
        label_beg = ne_str[(slash_idx+1):].split('@')
        if len(label_beg) == 1:
            label = label_beg[0]
            beg = None
        elif len(label_beg) == 2:
            label = label_beg[0]
            beg = int(label_beg[1].strip('()'))
        else:
            raise ValueError("invalid literal for ne_str: '{}'".format(ne_str))


        if label not in NE_TAGS:
            raise ValueError("invalid label for ne_str: '{}'".format(ne_str))

        return {'form' : form, 'label' : label, 'begin_within_word' : beg }
 
   
    def __str__(self):
        if hasattr(self, 'begin_within_word') and self.begin_within_word is not None:
            s = '{form}/{label}@({begin_within_word})'.format(**self)
        else:
            s = '{form}/{label}'.format(**self)
            
        return s

class SR_ARG_str(NikolTableTagString):
    @classmethod
    def parse(cls, sr_arg_str):
        """
        :param sr_args_str: eg) 'HHHHHH/ARG0__@4-9' (multiword) or 'HH/ARG1__@13' (one word)
        :type sr_args_str: str

        :return: {'form' : 'HHHHHH', 'label' : 'ARG0', 'begin_word_id' : 4, 'end_word_id' : 9}
        """
        try:
            slash_idx = sr_arg_str.rfind('/')
            arg_form = sr_arg_str[:slash_idx]
            label_wordrange_str = sr_arg_str[(slash_idx+1):]
            label, wordrange_str = label_wordrange_str.split('__@')
        except:
            raise ValueError("invalid literal for sr_arg_str: '{}'".format(sr_arg_str))

        if label not in SR_TAGS:
            raise ValueError("invalid label for sr_arg_str: '{}'".format(sr_arg_str))

        if re.match('^[0-9]+(-[0-9]+)?$', wordrange_str) is None:
            raise ValueError("invalid word range literal for sr_arg_str: '{}'".format(sr_arg_str))
            
        wordids = wordrange_str.split('-')
        w1id = int(wordids[0])
        w2id = int(wordids[1]) if len(wordids) == 2 else w1id

        if w1id > w2id: 
            raise ValueError("invalid word range for sr_arg_str: '{}'".format(sr_arg_str))
        
        return {'form' : arg_form, 'label' : label, 'begin_word_id' : w1id, 'end_word_id' : w2id }
        

    def __str__(self):
        if self.begin_word_id == self.end_word_id:
            return '{form}/{label}__@{begin_word_id}'.format(**self)
        else:
            return '{form}/{label}__@{begin_word_id}-{end_word_id}'.format(**self)

class ZA_ANTE_str(NikolTableTagString):
    @classmethod
    def parse(cls, za_snte_str):
        """
        :param za_ante_str: example) HHH__@s3_9
        :type za_ante_str: str

        :return: example) {'form': 'HHH', 'snum': 's3', 'word_id': 9}
        """
        try:
            #
            # eg) za_ante_str = 'HHH__@s3_9' or 'HHH__@-1'
            #
            ante_form, ante_swid = za_ante_str.split('__@')

            if ante_swid == '-1':
                ante_sid = '-1'
                ante_wid = None
            else:
                ante_sid, ante_wid = ante_swid.split('_')
                ante_wid = int(ante_wid)

        except:
            raise ValueError("invalid literal for za_ante_str: '{}'".format(za_ante_str))
 
        return {'form' : ante_form, 'snum' : ante_sid, 'word_id' : ante_wid}

    def __str__(self):
        return '{form}__@{snu}_{word_id}'.format(**self)
