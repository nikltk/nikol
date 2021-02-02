"""
"""
import koltk.corpus.nikl.annotated as nikl
import nikol.valid

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
        
    def process_za(self, valid = False):
        row1 = self.sentence_list[0]._rows[0]
        if row1._za_pred is None and row1._za_ante is None:
            self.ZA = []
        else:
            self.ZA = ZA.process_docrows(self, valid = valid) 


    def make_mp_corpus(self, valid = False):
        for s in self.sentence_list:
            s.process_morpheme(valid = valid)

    def make_ls_corpus(self, valid = False):
        for s in self.sentence_list:
            s.process_wsd_and_morpheme(valid = valid)

    def make_ne_corpus(self, valid = False):
        for s in self.sentence_list:
            s.process_ne(valid = valid)

    def make_za_corpus(self, valid = False):
        self.process_za(valid = valid)
 
    def make_dp_corpus(self, valid = False):
        for s in self.sentence_list:
            s.process_dp(valid = valid)

    def make_sr_corpus(self, valid = False):
        for s in self.sentence_list:
            s.process_srl(valid = valid)

class Sentence(nikl.Sentence):

    def __init__(self, 
                parent: Document = None,
                num: int = None,
                id: str = None, 
                form: str = None,
                sentrows = None):
        """
        :param sentrows: list of rows. see nikol.table.table.Row.

        """
        super().__init__(parent=parent, num=num)
        self.id = id
        self.form = form
        self.word = []
        self.__rows = sentrows

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

    def process_morpheme(self, valid = False):
        self.morpheme = Morpheme.process_sentrows(self._rows, valid = valid)

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
            
    def process_wsd_and_morpheme(self, valid = False):
        self.morpheme, self.WSD = WSD.process_sentrows(self._rows, valid = valid)

    @property 
    def ne_list(self):
        if not hasattr(self, 'NE'):
            self.process_ne()

        return self.NE

    def process_ne(self, valid = False):
        self.NE = NE.process_sentrows(self._rows, valid = valid)

    @property
    def dp_list(self):
        if not hasattr(self, 'DP'):
            self.process_dp()

        return self.DP

    def process_dp(self, valid = False):
        self.DP = DP.process_sentrows(self._rows, valid = valid)

    @property
    def srl_list(self):
        if not hasattr(self, 'SRL'):
            self.process_srl()

        return self.SRL

    def process_srl(self, valid = False):
        self.SRL = SRL.process_sentrows(self._rows, valid = valid)

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
                 position: int = None,
                 valid = False):
        
        parsed = cls.parse_mp_str(morph_str)
        form = parsed['form'] 
        label = parsed['label'] 

        if row is not None:
            parent = row.sentence
            word_id = row.word.id
        else:
            parent = None
            word_id = None

        return cls(parent=parent, id=id, form=form, label=label,
                   word_id=word_id, position=position, row=row)

    @classmethod
    def parse_mp_str(cls, mp_str: str):
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

        return {'form' : form, 'label': label}
        
    @classmethod
    def process_sentrows(cls, sentrows, valid = False):
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            return Morpheme.process_min_sentrows(sentrows, valid = valid)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows(cls, sentrows, valid = False):
        morphemes = []
        morph_id = 0
        for row in sentrows:
            row_morphs = []
            for (p, morph_str) in enumerate(row._mp.split(' + ')):
                morph_id += 1
                m = cls.from_min(morph_str, id=morph_id, position=p+1, row=row, valid = valid)
                row_morphs.append(m)
                
            if valid:
                try:
                    nikol.valid.begend(row._form, row_morphs)
                except Exception as e:
                    raise Exception('Morpheme.process_min_sentrows', row._form, row._mp, e)

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

        parsed = cls.parse_ls_str(ls_str)
        form = parsed['form']
        sense_id = parsed['sense_id']
        pos = parsed['pos']
        
        if row is not None:
            parent = row.sentence
        else:
            parent = None

        return cls(parent=parent, word=form, sense_id=sense_id, pos=pos,
                   begin=begin, end=end, row=row)

    @classmethod
    def parse_ls_str(cls, ls_str):
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

        if len(form_sense) == 1:
            form = form_sense[0]
            sense_id = None
        elif len(form_sense) == 2:
            form = form_sense[0]
            sense_id = int(form_sense[1])
        else:
            raise ValueError("invalid literal for ls_str: '{}'".format(ls_str)) 

        return {'form' : form, 'sense_id' : sense_id, 'pos' : pos }
        

    @classmethod
    def process_sentrows(cls, sentrows, morpheme_as_wsd = False, valid = False):
        """
        :param sentrows: list of rows in the sentence. see nikol.table.table module.
        :param morpheme_as_wsd: if True, morphemes are coerced to WSDs.
        """
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            if morpheme_as_wsd:
                return WSD.process_min_sentrows_ls(sentrows, valid = valid)
            else:
                return WSD.process_min_sentrows_wsd_and_morpheme(sentrows, valid = valid)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows_ls(cls, sentrows, valid = False):
        """
        :param sentrows: list of nikol.table.table.UnifiedMinRow
        :return: list of WSD. morphemes are coerced to WSDs with sense_id = 'None'.
        """
 
        sent_lss = []

        morph_id = 0
        for row in sentrows:
            mps = []
            row_lss = []
            beg = 0
            for (p, ls_str) in enumerate(row._ls.split(' + ')):
                morph_id += 1
                ls = cls.from_min(ls_str, row=row)
                ls._morpheme_id = morph_id
                ls._morpheme_position = p + 1
                ls._word_id = row.word.id
                ls.word_id = row.word.id
                row_lss.append(ls)
                
                mp = { 'form': ls.word, 'label' : ls.pos }
                mps.append(mp)
                
            try:
                mps = nikol.valid.begend(row._form, mps)
                for mp, ls in zip(mps, row_lss):
                    ls.begin = row.word.begin + mp['begin']
                    ls.end = row.word.begin + mp['end']
            except Exception as e:
                # nikol.valid.begend() fails to compute begin:end
                #
                if row._ls.find('__') > -1:
                    # if the word (row) contains a WSD
                    #
                    for ls in row_lss:
                        if ls.sense_id is not None:
                            # if ls is a WSD, try to compute begin:end
                            ind = row._form.find(ls.word)
                            indr = row._form.rfind(ls.word)
                            if ind != -1 and ind == indr:
                                #
                                # if ls.form is found in word.form:
                                #
                                ls.begin = row.word.begin + ind
                                ls.end = ls.begin + len(ls.word)
                            else:
                                # CRITICAL ERROR:
                                # need to compute begin:end
                                if valid:
                                    print(Exception("# ErrorWSDBeginEnd(); ls.str: {} word.form: {} row._ls: {} sentence.form: {} sentence.id: {}\nbegend('{}', {}) # => {}"
                                                    .format(ls.str, row.word.form, row._ls,
                                                            row.sentence.form, row.sentence.id,
                                                            row.word.form, mps, e)))
                                else:
                                    # WARNING!!!
                                    #
                                    # TODO: rewrite this! (or better to improve nikol.valid.begend())
                                    #
                                    #
                                    # if ls.form is not found in word.form:
                                    #
                                    ls.begin = row.word.begin
                                    ls.end = ls.begin + len(ls.word)
                        else:
                            # if sense_id is None (if ls is not a WSD), just pass it
                            # no need to compute begin:end for a Morpheme
                            pass
                else:
                    # if there is no WSD in the word (row), pass it
                    pass
                                
                        
            row.lss = row_lss
            sent_lss += row_lss
            
        return sent_lss

    @classmethod
    def process_min_sentrows_wsd_and_morpheme(cls, sentrows, valid = False):
        """
        :param sentrows: list of nikol.table.table.UnifiedMinRow
        :return: list of morphemes, list of WSDs.
        """
        lss = cls.process_min_sentrows_ls(sentrows, valid = valid)

        wsds = []
        morphemes = []
        for ls in lss:
            morphemes.append(Morpheme(parent = ls.parent,
                                      id = ls._morpheme_id,
                                      form = ls.word,
                                      label = ls.pos,
                                      word_id = ls._word_id,
                                      position = ls._morpheme_position))
            if ls.sense_id is not None:
                wsds.append(ls)

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
        """
        :param ne_str: eg) 'HHH/PS@(0)'
        :type ne_str: str
        
        :return: eg) {'form' : 'HHH', 'label' : 'PS', 'begin_within_word' : 0 }
        :rtype: dict
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

        return {'form' : form, 'label' : label, 'begin_within_word' : beg }
        
    @classmethod
    def begend(cls, wordform, morphemes, subwordform):
        """
        eg) wordform = '연구교숩니다'
            morphemes = '연구/NNG + 교수/NNG + 이/VCP + ㅂ니다/EF + ./SF'
            subwordform = '연구교수'
        
        Or morphemes = list of dict {'form', 'label'}
        """
        if type(morphemes) is str:
            mps = [Morpheme.parse_mp_str(mp) for mp in morphemes.split(' + ')]
        elif type(morphemes) is list:
            mps = morphemes
        


        mps_begend = nikol.valid.begend(wordform, mps)
        mp_matches = [mp for mp in mps_begend if mp['form'] == subwordform]
        if len(mp_matches) == 1:
            mp_matched = mp_matches[0]
            begin = mp_matched['begin']
            end = mp_matched['end']
        elif len(mp_matches) == 0:
            finds = []
            head = ''
            tail = subwordform
            for mp in mps_begend:
                b = tail.find(mp['form'])
                if b != -1:
                    finds.append(mp['begin'])
                    head += mp['form']
                    tail = tail[b:]

            if head == subwordform:
                begin = finds[0]
                end = begin + len(head)
            else:
                raise Exception('NE.begend', subwordform, finds, morphemes)
            
        else:
            raise Exception('NE.begend', wordform, morphemes, subwordform)
 
        return begin, end

    @classmethod
    def from_min(cls,
                 ne_str: str,
                 id: int,
                 row,
                 valid = False):
        try:
            parsed = NE.parse_ne_str(ne_str)
            form = parsed['form']
            label = parsed['label']
            begin_within_word = parsed['begin_within_word']
        except Exception as e:
            raise ValueError("{} at '{}' ({})".format(e, row._ne, row._gid))
            
        #
        # compute begin and end
        #
        toks = form.split()
        n = len(toks)
        try:
            last_word = row.neighborAt(n-1).word
        except:
            last_word = row.word
            
        if begin_within_word is not None:
            # eg)
            # ne_str = '이/PS@(0)'
            # word.form = '이감독이라고' 
            #
            begin = row.word.begin + begin_within_word
            end = begin + len(form) 
        else:
            if n == 1:
                # single word NE
                b = row._form.find(form)
                if b != -1:
                    begin = row.word.begin + b
                    end = begin + len(form)
                else:
                    try:
                        b, e = cls.begend(row._form, row._mp, form)
                        begin = row.word.begin + b
                        end = row.word.begin + e
                    except Exception as e:
                        raise Exception('NE.from_min:single_word', row._gid, row._form, row._ne,
                                        ne_str, row._mp, e)
                        
                   
            else:
                # multiword NE
                ind = row.sentence.form.find(form)
                indr = row.sentence.form.rfind(form)
                if (ind == indr
                    and row.word.id == row.sentence.wordAt(ind).id):
                    begin = ind
                    end = begin + len(form)
                else:
                    b = row._form.find(toks[0])
                    begin = row.word.begin + b
                    end = last_word.begin + last_word.form.find(toks[n-1]) + len(toks[n-1])
                    if form != row.sentence.form[begin:end]:
                        try:
                            b, _ = cls.begend(row._form, row._mp, toks[0])
                            _, e = cls.begend(last_word.form, last_word._row._mp, toks[n-1])
                            begin = row.word.begin + b
                            end = last_word.begin + e
                        except:
                            raise Exception('NE.from_min:multiword', row._gid, row._form, ne_str, begin, end, row.sentence.form)
            
        return cls(parent = row.sentence, id = id, form = form, label = label, begin = begin, end = end, row = row) 

    @classmethod
    def process_sentrows(cls, sentrows, valid = False):
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            return NE.process_min_sentrows(sentrows, valid = valid)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows(cls, sentrows, valid = False):
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
                n = cls.from_min(ne_str, id = ne_id, row = row, valid = valid)
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
    def from_min(cls, row, valid = False):
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
    def process_sentrows(cls, sentrows, valid = False):
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            return DP.process_min_sentrows(sentrows, valid = valid)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows(cls, sentrows, valid = False):
        dps = []
        for row in sentrows:
            d = DP.from_min(row, valid = valid)
            row.dp = d
            dps.append(d)

        for dp in dps:
            if dp.head != -1:
                try:
                    head_node = dps[dp.head - 1]
                except IndexError:
                    raise IndexError('dp.head out of range at {} (dp : {})'.format(dp._row.word.gid, dp))
                
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
    def from_min(cls, row, valid = False):
        args_str = row._sr_args

        srl = cls(parent=row.sentence, row=row)

        predicate = SRLPredicate.from_min(row, parent = srl, valid = valid)
        arguments = []
        for arg_str in args_str.split():
            arguments.append(SRLArgument.from_min(arg_str, parent=srl, valid = valid))

        srl.predicate = predicate
        srl.argument = arguments
        return srl 

    @classmethod
    def parse_sr_arg_str(cls, sr_arg_str):
        return SRLArgument.parse_sr_arg_str(sr_arg_str)

    @classmethod
    def process_sentrows(cls, sentrows, valid = False):
        if type(sentrows[0]).__name__ == 'UnifiedMinRow':
            return SRL.process_min_sentrows(sentrows, valid = valid)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_sentrows(cls, sentrows, valid = False):
        srls = []
        for row in sentrows:
            if row._sr_pred is None and row._sr_args is None:
                row.srl = None
                continue
            elif row._sr_pred == '' and row._sr_args == '':
                row.srl = None
                continue
            srl = SRL.from_min(row, valid = valid)
            row.srl = srl
            srls.append(srl)

        return srls
            
            
    @property
    def _word(self):
        return self.__word

class SRLPredicate(nikl.SRLPredicate):
    def __init__(self,
                 parent: SRL = None,
                 form: str = None,
                 begin: int = None,
                 end: int = None,
                 lemma: str = None,
                 sense_id: int = None):
        super().__init__(parent=parent, form=form, begin=begin, end=end, lemma=lemma, sense_id=sense_id)

    @classmethod
    def from_min(cls, row, parent: SRL, valid = False):
        pred_str = row._sr_pred
        word = row.word

        try:
            parsed = cls.parse_sr_pred_str(pred_str)
            lemma = parsed['lemma']
            sense_id = parsed['sense_id']
        except Exception as e:
            raise ValueError("{} at '{}' ({})".format(e, pred_str, row))
        
        #
        # proess form
        # - remove period (.) and comma (,)
        # - compute begin and end
        #
        form = word.form.strip('.,')
        begin = word.begin + word.form.find(form)
        end = begin + len(form)

        return SRLPredicate(parent = parent, form = form, begin = begin, end = end,
                            lemma = lemma, sense_id = sense_id)

    @classmethod
    def parse_sr_pred_str(cls, sr_pred_str):
        """
        :param sr_pred_str:  eg) 'HHHHH__4444401'
        :type sr_pred_str: str
        """
        try:
            pred_lemma, pred_sense_id = sr_pred_str.split('__')
            pred_sense_id = int(pred_sense_id)
        except:
            raise ValueError("invalid literal for sr_pred_str: '{}'".format(sr_pred_str))

        return {'lemma' : pred_lemma, 'sense_id' : pred_sense_id}


class SRLArgument(nikl.SRLArgument):
 
    def __init__(self,
                 parent: SRL = None,
                 form: str = None,
                 label: str = None,
                 begin: int = None,
                 end: int = None):
        super().__init__(parent = parent, form = form, label = label, begin = begin, end = end)

    @classmethod
    def from_min(cls, sr_arg_str, parent: SRL, valid = False):
        sent = parent.parent
        row = parent._row
        parsed = cls.parse_sr_arg_str(sr_arg_str)
        last_word_form = parsed['form']
        label = parsed['label']
        w1id = parsed['begin_word_id']
        w2id = parsed['end_word_id']

        w1 = sent.word_list[w1id - 1]
        w2 = sent.word_list[w2id - 1]
        if w1id == w2id:
            # single word argument

            arg_form = last_word_form
            ind = w1.form.find(arg_form)
            indr = w1.form.rfind(arg_form)
            if ind != -1 and ind == indr:
                begin = w1.begin + ind
                end = begin + len(arg_form)
            else:
                try:
                    b, e = NE.begend(w1.form, w1._row._mp, arg_form)
                    begin = w1.begin + b
                    end = w1.begin + e
                except Exception as err:
                    if len(last_word_form) > 1 and w2.form.startswith(last_word_form[:-1]):
                        decomp1 = nikol.valid.util.decompose(last_word_form[-1])
                        decomp2 = nikol.valid.util.decompose(w2.form[len(last_word_form)-1])
                        if decomp1[:-1] == decomp2[:-1]:
                            begin = w1.begin 
                            end = w2.begin + len(last_word_form)
                        else:
                            #
                            # rough guess. possibly bad guess
                            #
                            begin = w1.begin
                            end = w2.begin + len(last_word_form)
                            if valid :
                                print('ERROR_SRLArgument.from_min:single_word1', row._gid, row._form, row._sr_pred, row._sr_args,
                                      '# {} => {} ({})'.format(sr_arg_str, w2.form, w2._row._mp), sep="\t")
                                #raise Exception('SRLArgument.from_min:singleword', row._gid, sr_arg_str, w2.form, w2._row._mp)
                    else:
                        #
                        # rough guess. possibly bad guess
                        #
                        begin = w1.begin
                        end = w2.begin + len(last_word_form)
                        if valid:
                            print('ERROR_SRLArgument.from_min:single_word2', row._gid, row._form, row._sr_pred, row._sr_args,
                                  '# {} => {} ({})'.format(sr_arg_str, w2.form, w2._row._mp), sep="\t")
                            #raise Exception('SRLArgument.from_min:single_word2', row._gid, sr_arg_str, w1.form, w1._row._mp)
        else:
            # multiword argument
            w2 = sent.word_list[w2id - 1]
 
            begin = w1.begin
        
            if w2.form.startswith(last_word_form): 
                end = w2.begin + len(last_word_form)
            elif len(last_word_form) > 1 and w2.form.startswith(last_word_form[:-1]):
                decomp1 = nikol.valid.util.decompose(last_word_form[-1])
                decomp2 = nikol.valid.util.decompose(w2.form[len(last_word_form)-1])
                if decomp1[:-1] == decomp2[:-1]:
                    end = w2.begin + len(last_word_form)
                else:
                    #
                    # rough guess. possibly bad guess.
                    #
                    end = w2.begin + len(last_word_form)
                    if valid :
                        print('ERROR_SRLArgument.from_min:multiword1', row._gid, row._form, row._sr_pred, row._sr_args,
                              '# {} => {} ({})'.format(sr_arg_str, w2.form, w2._row._mp), sep="\t")
                        #raise Exception('SRLArgument.from_min:multiword1', row._gid, sr_arg_str, w2.form, w2._row._mp)
            else:
                try:
                    b, e = NE.begend(w2.form, w2._row._mp, last_word_form)
                    end = w2.begin + e
                except Exception as err:
                    #
                    # rough guess. possibly bad guess.
                    #
                    end = w2.begin + len(last_word_form)
                    if valid :
                        print('ERROR_SRLArgument.from_min:multiword2', row._gid, row._form, row._sr_pred, row._sr_args,
                              '# {} => {} ({})'.format(sr_arg_str, w2.form, w2._row._mp), sep="\t")
                        #raise Exception('SRLArgument.from_min:multiword2', row._gid, sr_arg_str, w2.form, w2._row._mp, err)


            arg_form = sent.form[begin:end]

        arg = cls(parent = parent, form = arg_form, label = label, begin = begin, end = end)

        return arg


    @classmethod
    def parse_sr_arg_str(cls, sr_arg_str):
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
            wordids = wordrange_str.split('-')
            w1id = int(wordids[0])
            w2id = int(wordids[1]) if len(wordids) == 2 else w1id
        except:
            raise ValueError("invalid literal for sr_arg_str: '{}'".format(sr_arg_str))


        return {'form' : arg_form, 'label' : label, 'begin_word_id' : w1id, 'end_word_id' : w2id }
    

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
    def from_min(cls, row, parent: Document = None, valid = False):
        pred_form = row._za_pred
        ante_str = row._za_ante
        doc = row.document

        za = cls(parent=parent, row=row)


        #
        # predicate
        #
        # compute begin, end
        pred_word = row.word
        beg = pred_word.form.find(pred_form)
        if beg != -1:
            pred_begin = pred_word.begin + beg
            pred_end = pred_begin + len(pred_form)
        else:
            ind = row.sentence.form.find(pred_form)
            indr = row.sentence.form.rfind(pred_form)
            if ind == indr:
                pred_begin = ind
                pred_end = pred_begin + len(pred_form)
            else:
                raise Exception('ZA', pred_form, pred_word.form, beg, row)
        
        za.predicate = nikl.ZAPredicate(parent=za, form=pred_form, sentence_id=row.sentence.id,
                                        begin=pred_begin, end=pred_end)

        #
        # antecendent
        #
        za.antecedent = [ ZAAntecedent.from_min(row=row, parent=za, valid = valid) ]

        return za

    @classmethod
    def parse_za_ante_str(cls, ante_str):
        return ZAAntecedent.parse_za_ante_str(ante_str)

    @classmethod
    def from_full(cls, row, parent: Document = None):
        pass

    @classmethod
    def process_docrows(cls, document, valid = False):
        if type(document.sentence_list[0]._rows[0]).__name__ == 'UnifiedMinRow':
            return ZA.process_min_docrows(document, valid = valid)
        else:
            raise NotImplementedError

    @classmethod
    def process_min_docrows(cls, document, valid = False):
        # if za columns do not exist
        #if docrows[0]._za_pred is None and docrows[0]._za_ante is None:
        #    return None
        
        zas = []
        for row in document._rows:
            if row._za_pred != '' or row._za_ante != '':
                z = ZA.from_min(row, parent=document, valid = valid)
                row.za = z
                zas.append(z)
            else:
                row.za = None

        return zas
 

class ZAAntecedent(nikl.ZAAntecedent): 
    def __init__(self,
                 parent: ZA = None,
                 form: str = None,
                 type: str = None,
                 sentence_id: int = None,
                 begin: int = None,
                 end: int = None):
        super().__init__(parent=parent, type=type, form=form, sentence_id=sentence_id, begin=begin, end=end)
 
    @classmethod
    def from_min(cls, row, parent: ZA, valid = False):
        ante_str = row._za_ante
        doc = row.document

        try:
            parsed = cls.parse_za_ante_str(ante_str)
        except Exception as e:
            raise Exception('{} ({})'.format(e, row._gid))
        ante_form = parsed['form']
        snum = parsed['snum']
        ante_wid = parsed['word_id']
        
        if snum == '-1':
            ante_sent_id = '-1'
            ante_begin = -1
            ante_end = -1
        else:
            ante_sid = int(snum.lstrip('s'))

            ante_sent = doc.sentence_list[ante_sid - 1]
            ante_sent_id = ante_sent.id

            ante_word = ante_sent.word_list[ante_wid - 1]
            beg = ante_word.form.find(ante_form)

            #
            # compute begin and end
            #
            if beg != -1:
                ante_begin = ante_word.begin + beg
                ante_end = ante_begin + len(ante_form)
            else:
                try:
                    b, e = NE.begend(ante_word._row._form, ante_word._row._mp, ante_form)
                    ante_begin = ante_word.begin + b
                    ante_end = ante_word.begin + e
                except:
                    #
                    # rough guess. possibly bad guess.
                    #
                    ante_begin = ante_word.begin
                    ante_end = ante_begin + len(ante_form)
                    if valid:
                        print('ERROR_ZAAntecedent.from_min', row._gid, row.word.swid, row._form, row._za_pred, row._za_ante,
                              '# {} ({})'.format(ante_word.form, ante_word._row._mp),
                              sep = '\t')
                        #raise Exception('ZAAntecedent.from_min', row._gid, row._form, ante_str, ante_word.form, ante_word._row._mp)


        return cls(parent=parent, form=ante_form, type='subject', sentence_id=ante_sent_id,
                   begin=ante_begin, end=ante_end) 

    
    @classmethod
    def parse_za_ante_str(cls, za_ante_str):
        """
        :param za_ante_str: example) HHH__@s3_9
        :type za_ante_str: str

        :return: example) {'form': 'HHH', 'snum': 's3', 'word_id': 9}
        :rtype: dict
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

 


