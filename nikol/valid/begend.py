from copy import copy

class BegEndClass(object):
    def __init__(self, word, mp_list):

        self.word = word
        self.mp_list = mp_list

    def find_begend(self):
        self._begend_list = []
        self._crt_idx = 0
        self._word = copy(self.word)
        self._mp_list = copy(self.mp_list)
        self._idx = 0

        if ''.join([i['form'] for i in self.mp_list]) == self._word:
            for vals in self.mp_list:
                self._begend_list.append((self._crt_idx, self._crt_idx+len(vals['form'])))
                self._mp_list.pop(0)
                self._crt_idx += len(vals['form'])
        while self._mp_list:
            # print(f"{self._idx}th mp: {self._word, self._crt_idx}, {self._mp_list}, {self._crt_idx}, \n{self._begend_list},")
            self.one_step(self._mp_list[0], self._idx)
            if self._idx > 100:
                raise Exception('iteration exceeded')
                break
        if self._begend_list:
            if self._begend_list[-1][-1] != len(self.word):
                raise Exception('last end value not matched to word legnth')

        if len(self._begend_list) != len(self.mp_list):
            raise Exception('len(ls_morpheme) != len(begend_list)')

        if self._begend_list[0][0] != 0:
            raise Exception("begin not starts with zero")
        self.output = copy(self.mp_list)
        for idx, ls_mp in enumerate(self.output):
            ls_mp['begin'] = self._begend_list[idx][0]
            ls_mp['end'] = self._begend_list[idx][1]

        return self.output

    def one_step(self, mp, idx):
        self._mp, self._mp_pos = mp['form'], mp['label']

        if len(self._word) > len(self._mp):
            if (self._mp_pos in ['VA', 'XSA']) and (get_cv_list(self._mp)[-1] == 'ㅂ'):
                cv_list = get_cv_list(self._mp)
                mp0_len, mp1_len = len(self._mp), len(self._mp_list[1]['form'])
                if (self._mp_list[1]['form'].startswith('ㄴ')) and (self._mp_list[1]['label'].startswith('E')):
                    # print(self._mp_list, self._word)
                    if self._word[mp0_len] == '운':
                        self._begend_list.append((self._crt_idx, self._crt_idx+mp0_len+1))
                        self._begend_list.append((self._crt_idx+mp0_len, self._crt_idx+mp0_len+mp1_len)) #update etm index
                        self._crt_idx += (mp0_len + mp1_len)
                        self._mp_list = self._mp_list[2:]
                        self._word = self._word[(mp0_len + mp1_len):]
                    else:
                        pass
                elif (self._mp_list[1]['form'].startswith('어')) and (self._mp_list[1]['label'].startswith('E')):
                    if self._word[mp0_len] == '워':
                        self._begend_list.append((self._crt_idx, self._crt_idx+mp0_len+1))
                        self._begend_list.append((self._crt_idx+mp0_len, self._crt_idx+mp0_len+mp1_len)) #update etm index
                        self._crt_idx += (mp0_len + mp1_len)
                        self._mp_list = self._mp_list[2:]
                        self._word = self._word[(mp0_len + mp1_len):]
                    else:
                        pass
                elif (self._mp_list[1]['form'] == 'ㄹ') and (self._mp_list[1]['label'] == 'ETM'):
                    if self._word[mp0_len] == '울':
                        self._begend_list.append((self._crt_idx, self._crt_idx+mp0_len+1))
                        self._begend_list.append((self._crt_idx+mp0_len, self._crt_idx+mp0_len+mp1_len)) #update etm index
                        self._crt_idx += (mp0_len + mp1_len)
                        self._mp_list = self._mp_list[2:]
                        self._word = self._word[(mp0_len + mp1_len):]
                    else:
                        pass
                elif (self._mp_list[1]['form'] == '었') and (self._mp_list[1]['label'] == 'EP'):
                    if self._word[mp0_len] == '웠':
                        self._begend_list.append((self._crt_idx, self._crt_idx+mp0_len+1))
                        self._begend_list.append((self._crt_idx+mp0_len, self._crt_idx+mp0_len+mp1_len)) #update etm index
                        self._crt_idx += (mp0_len + mp1_len)
                        self._mp_list = self._mp_list[2:]
                        self._word = self._word[(mp0_len + mp1_len):]
                    else:
                        pass

        if not self._mp_list:
            self._idx += 1
            return
        else:
            self._mp, self._mp_pos = self._mp_list[0]['form'], self._mp_list[0]['label']

        #contracted
        if len(self._mp_list) > 1:
            # tense                 
            if (self._mp_pos in ['VV','VX','XSV']) and ((self._mp_list[1]['label'] in ['EP']) and (self._mp_list[1]['form'] in ['았', '었'])):
                if (get_cv_list(self._mp)[-1] in ['ㅏ', 'ㅐ', 'ㅓ', 'ㅔ', 'ㅣ', 'ㅡ', 'ㅗ', 'ㅜ','ㅎ']) and self._mp != '하':
                    self._begend_list.append((self._crt_idx, self._crt_idx+len(self._mp)))
                    if (get_cv_list(self._mp)[-1] == 'ㅎ') and get_cv_list(self._word[len(self._mp)])[-2:] != ['ㅘ', 'ㅆ']:
                        self._crt_idx += len(self._mp)+1
                        self._begend_list.append((self._crt_idx-1, self._crt_idx))
                        self._word = self._word[len(self._mp)+1:]
                    else:
                        self._crt_idx += len(self._mp)
                        self._begend_list.append((self._crt_idx-1, self._crt_idx))
                        self._word = self._word[len(self._mp):]
                    self._mp_list = self._mp_list[2:]
                else:
                    pass

            # ending
            if (self._mp_pos == 'VCP' and self._mp == '이') and (self._mp_list[1]['form'] == '라는' and self._mp_list[1]['label'] == 'ETM'):
                if self._word[:2] == '라는':
                    self._begend_list.append((self._crt_idx, self._crt_idx+1))
                    self._begend_list.append((self._crt_idx, self._crt_idx+2))
                    self._word = self._word[2:]
                    self._crt_idx += 2
                    self._mp_list = self._mp_list[2:]

            if (self._mp_pos == 'VCP' and self._mp == '이') and (self._mp_list[1]['form'] == 'ㄹ' and self._mp_list[1]['label'] == 'ETM'):
                if self._word[0] == 'ㄹ':
                    self._begend_list.append((self._crt_idx, self._crt_idx+1))
                    self._begend_list.append((self._crt_idx, self._crt_idx+1))
                    self._crt_idx += 1
                    self._word = self._word[1:]
                    self._mp_list = self._mp_list[2:]


        if not self._mp_list:
            self._idx += 1
            return
        else:
            self._mp, self._mp_pos = self._mp_list[0]['form'], self._mp_list[0]['label']

        if self._word[:3] in PREV_DICT.keys():
            vals = PREV_DICT[self._word[:3]]
            mp_forms = vals['form']
            trg_forms = [i['form'] for i in self._mp_list[:len(mp_forms)]]

            if not list(mp_forms) == trg_forms:
                pass
            else:
                begend_ls = PREV_DICT[self._word[:3]]['begend']
                self._begend_list += list(map(lambda x: (x[0]+self._crt_idx, x[1]+self._crt_idx), begend_ls))
                self._crt_idx += begend_ls[-1][-1]
                self._mp_list = self._mp_list[len(mp_forms):]
                self._word = self._word[3:]

        elif self._word[:2] in PREV_DICT.keys():
            vals=PREV_DICT[self._word[:2]]
            mp_forms = vals['form']
            trg_forms = [i['form'] for i in self._mp_list[:len(mp_forms)]]
            if not list(mp_forms) == trg_forms:
                pass
            else:
                begend_ls = PREV_DICT[self._word[:2]]['begend']
                self._begend_list += list(map(lambda x: (x[0]+self._crt_idx, x[1]+self._crt_idx), begend_ls))
                self._crt_idx += begend_ls[-1][-1]
                self._mp_list = self._mp_list[len(mp_forms):]
                self._word = self._word[2:]

        elif self._word[:1] in PREV_DICT:
            # print('case3')
            vals = PREV_DICT[self._word[:1]]
            mp_forms = vals['form']

            trg_forms = [i['form'] for i in self._mp_list[:len(mp_forms)]]
            if not list(mp_forms) == trg_forms:
                pass
            else:
                begend_ls = PREV_DICT[self._word[:1]]['begend']
                self._begend_list += list(map(lambda x: (x[0]+self._crt_idx, x[1]+self._crt_idx), begend_ls))
                self._crt_idx += begend_ls[-1][-1]

                self._mp_list = self._mp_list[len(mp_forms):]
                self._word = self._word[1:]

        elif self._word[:len(self._mp)] == self._mp:
            # print('case4')
            """Match without any exception"""
            self._begend_list.append((self._crt_idx, self._crt_idx + len(self._mp)))
            self._mp_list.pop(0)
            self._crt_idx += len(self._mp)
            self._word = self._word[len(self._mp):]


        elif self._mp in LEAD_DICT:
            # print('case5')
            word_form = LEAD_DICT[self._mp]['form'][0]
            if self._word[:len(word_form)] == word_form:
                begend_ls = LEAD_DICT[self._mp]['begend']
                self._begend_list += list(map(lambda x: (x[0]+self._crt_idx, x[1]+self._crt_idx), begend_ls))
                self._crt_idx += begend_ls[-1][-1]
                self._word = self._word[len(word_form):]
                self._mp_list.pop(0)

        elif check_decompose(self._word, self._mp):
            """decompose c/v and match"""
            wd_dc, mp_dc = check_decompose(self._word, self._mp)
            if mp_dc == wd_dc[:len(mp_dc)]:
                mp_form_list = [i['form'] for i in self._mp_list[1:] if i['form'].startswith('ㄹ')]
                # print("""decompose c/v and match""")
                if wd_dc[len(mp_dc)] == 'ㄹ' and not mp_form_list:
                    # print('1st if')
                    # print(f"current morpheme and word: {self._mp, self._word} , list of remained morpheme : {self._mp_list}")
                    self._begend_list.append((self._crt_idx, self._crt_idx + len(self._mp)))
                    self._mp_list.pop(0)
                    self._crt_idx += len(self._mp)
                    self._word = self._word[len(self._mp):]
                else:
                    # print('1st else')
                    # print(f"current morpheme and word: {self._mp, self._word} , list of remained morpheme : {self._mp_list}")
                    self._begend_list.append((self._crt_idx, self._crt_idx + len(self._mp)))
                    self._mp_list.pop(0)
                    self._crt_idx += len(self._mp)-1
                    self._word = wd_dc[len(mp_dc)] + self._word[len(self._mp):]
            else:
                pass
            # find gliding vowels

        elif self._word[:2] in NEXT_DICT:
            # print('case7')
            vals = NEXT_DICT[self._word[:2]]
            mp_forms = vals['form']
            trg_forms = [i['form'] for i in self._mp_list[:(len(mp_forms))]]
            if not list(mp_forms) == trg_forms:
                pass
            else:
                begend_ls =NEXT_DICT[self._word[:2]]['begend']
                updated = list(map(lambda x: (x[0]+self._crt_idx, x[1]+self._crt_idx), begend_ls))
                self._begend_list += updated
                self._crt_idx += begend_ls[-1][-1]
                self._mp_list = self._mp_list[len(mp_forms):]
                self._word = self._word[2:]

        elif self._word[:1] in NEXT_DICT:
            # print('case8')
            vals = NEXT_DICT[self._word[:1]]
            mp_forms = vals['form']

            trg_forms = [i['form'] for i in self._mp_list[:(len(mp_forms))]]
            if not list(mp_forms) == trg_forms:
                pass
            else:
                begend_ls =NEXT_DICT[self._word[:1]]['begend']
                self._begend_list += list(map(lambda x: (x[0]+self._crt_idx, x[1]+self._crt_idx), begend_ls))
                self._crt_idx += begend_ls[-1][-1]
                self._mp_list = self._mp_list[len(mp_forms):]
                self._word = self._word[1:]

        elif get_cv_list(self._mp)[-1] == 'ㅎ' and self._mp_pos == 'VA':
            # print('case9')
            if self._mp_list[1]['form'] in ['ㄹ', 'ㄴ']:
                tmp_trg = self._mp_list[2]['form']
                mp_len = len(self._mp)
                if tmp_trg == self._word[mp_len:(mp_len+len(tmp_trg))]:
                    self._begend_list.append((self._crt_idx, self._crt_idx + len(self._mp)))
                    self._begend_list.append((self._crt_idx-1, self._crt_idx + len(self._mp)))
                    self._mp_list = self._mp_list[2:]
                    self._crt_idx += len(self._mp)
                    self._word = self._word[len(self._mp):]

                else:
                    #todo: warning
                    pass
            else:
                #todo: warning
                pass
        else:
            #todo: warning
            pass

        # ------

        if not self._mp_list:
            self._idx += 1
            return
        else:
            self._mp, self._mp_pos = self._mp_list[0]['form'], self._mp_list[0]['label']

        if self._mp in ETC_DICT:
            if self._mp != self._mp_list[0]['form']:
                #todo: warning
                pass

            next_mps = ''.join([i['form'] for i in self._mp_list[1:]])
            mp_tuple = tuple([i['form'] for i in self._mp_list[1:]])

            if len(self._mp_list) < 2: next_mps = ''

            next_mps_cvs = get_cv_list(next_mps)
            words_cvs = get_cv_list(self._word)
            next_dict_forms = {i['form']:k for k, i in NEXT_DICT.items()}

            if self._mp_pos == ETC_DICT[self._mp]['label']:
                if (next_mps_cvs == words_cvs):
                    self._mp_list.pop(0)
                    begend_tup = tuple(map(lambda x: self._crt_idx+x, ETC_DICT[self._mp]['begend']))
                    self._begend_list.append(begend_tup)
                elif (mp_tuple in next_dict_forms) and (self._word == next_dict_forms[mp_tuple]):
                    self._mp_list.pop(0)
                    begend_tup = tuple(map(lambda x: self._crt_idx+x, ETC_DICT[self._mp]['begend']))
                    self._begend_list.append(begend_tup)

        self._idx += 1

def get_cv_list(chars):
    res = []
    for char in chars:
        if 'ㄱ'<= char <='ㅣ':
            res += char
        elif '가' <= char <= '힣':
            cho, jung, jong = decompose(char)
            res += [cho_ls[cho], jung_ls[jung]]
            if jong:
                res += [jong_ls[jong]]
        else:
            res += char
    return res

def check_decompose(word, mp):

    mp_dc = get_cv_list(mp)
    wd_dc = get_cv_list(word)
    if wd_dc[:len(mp_dc)] == mp_dc:
        return wd_dc, mp_dc
    else:
        return False

def decompose(han):
    num = ord(han) - 0xac00
    lead = num // 588
    vt = num % 588
    vowel = vt // 28
    trail = vt % 28

    return [lead, vowel, trail]


def begend(words, mps):
    begend_inst = BegEndClass(words, mps)
    return begend_inst.find_begend()

# cho list        
cho_ls = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
# jung list
jung_ls = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
# jong list
jong_ls = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

ETC_DICT={
    '하':{'form':('하',),'begend': (0,1), 'label':'XSA'},
    '하':{'form':('하',),'begend': (0,1), 'label':'VX'},
    '이':{'form':('이',),'begend': (0,1), 'label':'VCP'},
    '아':{'form':('아',),'begend': (-1,0), 'label':'EC'},
    '아':{'form':('아',),'begend': (-1,0), 'label':'EF'},
    '어':{'form':('어',),'begend': (-1,0), 'label':'EF'},
    'ㄹ':{'form':('ㄹ',),'begend': (-1,0), 'label':'ETM'},
    }


PREV_DICT = {
    '몇며시' : { 'form' : ('몇몃', '이'), 'begend' :[(0,3), (2,3)]},

    '이던지': {'form': ('이든지',),'begend': [(0, 3)]},
    '스런': {'form': ('스럽', 'ㄴ'), 'begend': [(0,2), (1,2)]},
    '당해': {'form': ('당하', '아'),'begend': [(0,2), (1,2)]},
    '이랬': {'form': ('이러', '었'),'begend': [(0,2), (1,2)]},
    '드려': {'form': ('드리', '어'),'begend': [(0,2), (1,2)]},
    '숨져': {'form': ('숨지', '어'),'begend': [(0,2), (1,2)]},
    '속여': {'form': ('속이', '어'),'begend': [(0,2), (1,2)]},
    '챙겨': {'form': ('챙기', '어'),'begend': [(0,2), (1,2)]},

    '시켜도': {'form': ('시키', '어도'),'begend': [(0,2), (1,3)]},
    '시켜라': {'form': ('시키', '어라'),'begend': [(0,2), (1,3)]},
    '시켜야': {'form': ('시키', '어야'),'begend': [(0,2), (1,3)]},
    '시켜요': {'form': ('시키', '어요'),'begend': [(0,2), (1,3)]},
    '시켜서': {'form': ('시키', '어서'),'begend': [(0,2), (1,3)]},
    '딱딱해': {'form': ('딱딱하', '아'),'begend': [(0,3), (2,3)]},

    '지으면': {'form': ('짓', '으면'),'begend': [(0,1), (1,3)]},
    '걸어': {'form': ('걷', '어'),'begend': [(0,1), (1,2)]},
    '걸로': {'form': ('거', '로'),'begend': [(0,1), (1,2)]},
    '걸로': {'form': ('거', 'ㄹ로'), 'begend': [(0, 1), (1, 2)]},

    '드는': {'form': ('들', '는'),'begend': [(0,1), (1,2)]},
    '달랐': {'form': ('다르', '았'),'begend': [(0,1), (1,2)]},
    '만드는': {'form': ('만들', '는'),'begend': [(0,2), (2,3)]},
    '먼거리':{'form': ('멀', 'ㄴ', '거리'),'begend': [(0,1), (0,1), (2,3)]},
    '사시는': {'form': ('살','시', '는'),'begend': [(0,1), (1,2), (2,3)]},
    '사는': {'form': ('살', '는'),'begend': [(0,1), (1,2)]},
    '아실': {'form': ('알', '시', 'ㄹ'),'begend': [(0,1), (1,2), (1,2)]},
    '아는': {'form': ('알', '는'),'begend': [(0,1), (1,2)]},
    '무는': {'form': ('알', '는'),'begend': [(0,1), (1,2)]},
    '지음': {'form': ('짓', 'ㅁ'),'begend': [(0,1), (1,2)]},
    '깨달은': {'form': ('깨닫', '은'),'begend': [(0,2), (2,3)]},


    '하여': {'form': ('하', '아'),'begend': [(0,1), (1,2)]},
    '하였': {'form': ('하', '았'),'begend': [(0,1), (1,2)]},
    '해야': {'form': ('하', '아야'),'begend': [(0,1), (0,2)]},

    '해야죠': {'form': ('하', '아야지', '요'),'begend': [(0,1), (0,3), (2,3)]},
    '하셔야': {'form': ('하', '시', '어야'),'begend': [(0,1), (1,2), (1,3)]},
    '하셔도': {'form': ('하', '시', '어도'),'begend': [(0,1), (1,2), (1,3)]},
    '돼야지': {'form': ('되', '어야지'),'begend': [(0,1), (0,3)]},
    '돼선': {'form': ('되', '어서', 'ㄴ'),'begend': [(0,1), (0,2), (1,2)]},

    '거깄': {'form': ('거기', '있'),'begend': [(0,2), (1,2)]},
    '여깄': {'form': ('여기', '있'),'begend': [(0,2), (1,2)]},
    '어딨': {'form': ('어디', '있'),'begend': [(0,2), (1,2)]},
    '누가': {'form': ('누구', '가'),'begend': [(0,2), (1,2)]},

    '이게': {'form': ('이거', '이'),'begend': [(0,2), (1,2)]},
    '요게': {'form': ('요거', '이'),'begend': [(0,2), (1,2)]},
    '그게': {'form': ('그거', '이'),'begend': [(0,2), (1,2)]},
    '저게': {'form': ('저거', '이'),'begend': [(0,2), (1,2)]},
    '고게': {'form': ('고거', '이'),'begend': [(0,2), (1,2)]},

    '나눠': {'form': ('나누', '어'),'begend': [(0,2), (1,2)]},
    '맞춰': {'form': ('맞추', '어'),'begend': [(0,2), (1,2)]},
    '나눠요': {'form': ('나누', '어요'),'begend': [(0,2), (1,3)]},
    '비겨': {'form': ('비기', '어'),'begend': [(0,2), (1,2)]},
    '시켜': {'form': ('시키', '어'),'begend': [(0,2), (1,2)]},
    '지쳐': {'form': ('지치', '어'),'begend': [(0,2), (1,2)]},
    '붙여':{'form': ('붙이', '어'),'begend': [(0,2), (1,2)]},

    '걸까':{'form':('거', '이', 'ㄹ까'),'begend': [(0,1), (0,1), (0,2)]},
    '간다':{'form': ('가', 'ㄴ다'),'begend': [(0,1), (0,2)]},
    '가서':{'form': ('가', '아서'),'begend': [(0,1), (0,2)]},

    '네겐': {'form': ('너', '에게', 'ㄴ'),'begend': [(0,1), (0,2), (1,2)]},
    '내겐': {'form': ('나', '에게', 'ㄴ'),'begend': [(0,1), (0,2), (1,2)]},
    '내게서': {'form': ('나', '에게서'),'begend': [(0,1), (0,3)]},

    '거구나': {'form': ('것', '이', '구나'),'begend': [(0,1), (1,2), (1,3)]},
    '뭐시여': {'form': ('뭣', '이', '어'),'begend': [(0,2), (1,3), (2,3)]},

    '지음': {'form': ('짓', '음'),'begend': [(0,1), (1,2)]},
}

NEXT_DICT = {

    '텐데': {'form': ('터', '이', 'ㄴ데'),'begend': [(0,1), (0,1), (0,2)]},
    '텐가': {'form': ('터', '이', 'ㄴ가'),'begend': [(0,1), (0,1), (0,2)]},
    '해선': {'form': ('하', '아서', 'ㄴ'),'begend': [(0,1), (0,2), (1,2)]},
    '세요': {'form': ('시', '어요'),'begend': [(0,1), (0,2)]},
    '에요': {'form': ('이', '어요'),'begend': [(0,1), (0,2)]},

    '줘야': {'form': ('주', '어야'),'begend': [(0,1), (0,2)]},
    '둬야': {'form': ('두', '어야'),'begend': [(0,1), (0,2)]},

    '져서': {'form': ('지', '어서'),'begend': [(0,1), (0,2)]},
    '뭘까': {'form': ('뭐', '이', 'ㄹ까'),'begend': [(0,1), (0,1), (0,2)]},

    '했었': {'form': ('하', '았었'),'begend': [(0,1), (0,2)]},
    '하야': {'form': ('하', '아야'),'begend': [(0,1), (0,2)]},
    '해야': {'form': ('하', '아야'),'begend': [(0,1), (0,2)]},
    '해도': {'form': ('하', '아도'),'begend': [(0,1), (0,2)]},
    '해요': {'form': ('하', '아요'),'begend': [(0,1), (0,2)]},
    '해서': {'form': ('하', '아서'),'begend': [(0,1), (0,2)]},
    '해라': {'form': ('하', '아라'),'begend': [(0,1), (0,2)]},

    '봐도': {'form': ('보', '아도'),'begend': [(0,1), (0,2)]},
    '봐야': {'form': ('보', '아야'),'begend': [(0,1), (0,2)]},
    '봐서': {'form': ('보', '아서'),'begend': [(0,1), (0,2)]},

    '됐었': {'form': ('되', '었었'),'begend': [(0,1), (0,2)]},
    '돼야': {'form': ('되', '어야'),'begend': [(0,1), (0,2)]},
    '돼도': {'form': ('되', '어도'),'begend': [(0,1), (0,2)]},
    '돼요': {'form': ('되', '어요'),'begend': [(0,1), (0,2)]},
    '돼서': {'form': ('되', '어서'),'begend': [(0,1), (0,2)]},

    '였었': {'form': ('이', '었었'),'begend': [(0,1), (0,2)]},
    '여야': {'form': ('이', '어야'),'begend': [(0,1), (0,2)]},
    '여도': {'form': ('이', '어도'),'begend': [(0,1), (0,2)]},
    '예요': {'form': ('이', '에요'),'begend': [(0,1), (0,2)]},
    '여서': {'form': ('이', '어서'),'begend': [(0,1), (0,2)]},
    '셔서': {'form': ('시', '어서'),'begend': [(0,1), (0,2)]},

    '네게': {'form': ('너', '에게'),'begend': [(0,1), (0,2)]},
    '제게': {'form': ('저', '에게'),'begend': [(0,1), (0,2)]},
    '내게': {'form': ('나', '에게'),'begend': [(0,1), (0,2)]},

    '마': {'form': ('말', '아'),'begend': [(0,1), (0,1)]},
    '해': {'form': ('하', '아'),'begend': [(0,1), (0,1)]},
    '했': {'form': ('하', '았'),'begend': [(0,1), (0,1)]},
    '셔': {'form': ('시', '어'),'begend': [(0,1), (0,1)]},
    '셨': {'form': ('시', '었'),'begend': [(0,1), (0,1)]},
    '돼': {'form': ('되', '어'),'begend': [(0,1), (0,1)]},
    '됐': {'form': ('되', '었'),'begend': [(0,1), (0,1)]},

    '봤': {'form': ('보', '았'),'begend': [(0,1), (0,1)]},
    '줬': {'form': ('주', '었'),'begend': [(0,1), (0,1)]},
    '졌': {'form': ('지', '었'),'begend': [(0,1), (0,1)]},
    '였': {'form': ('이', '었'),'begend': [(0,1), (0,1)]},
    '왔': {'form': ('오', '았'),'begend': [(0,1), (0,1)]},
    '와': {'form': ('오', '아'),'begend': [(0,1), (0,1)]},
    '봐': {'form': ('보', '아'),'begend': [(0,1), (0,1)]},

    '네': {'form': ('너', '의'),'begend': [(0,1), (0,1)]},
    '게': {'form': ('거', '이'),'begend': [(0,1), (0,1)]},
    '제': {'form': ('저', '의'),'begend': [(0,1), (0,1)]},
    '내': {'form': ('나', '의'),'begend': [(0,1), (0,1)]},

    '테': {'form': ('터', '이'),'begend': [(0,1), (0,1)]},
    '줘': {'form': ('주', '어'),'begend': [(0,1), (0,1)]},
    '쳐': {'form': ('치', '어'),'begend': [(0,1), (0,1)]},
    '치': {'form': ('하', '지'),'begend': [(0,1), (0,1)]},
    '여': {'form': ('이', '어'),'begend': [(0,1), (0,1)]},
    '져': {'form': ('지', '어'),'begend': [(0,1), (0,1)]},

    '키': {'form': ('하', '기'),'begend': [(0,1), (0,1)]},
    '코자': {'form': ('하', '고자'),'begend': [(0,1), (0,2)]},
}

LEAD_DICT = {
    '이든': {'form': ('든',),'begend': [(0, 1)]},
    '이라던가': {'form': ('라던가',),'begend': [(0, 3)]},
    '이라던지': {'form': ('라던지',),'begend': [(0, 3)]},
    '이라든지': {'form': ('라든지',),'begend': [(0, 3)]},
    '이라든가': {'form': ('라든가',),'begend': [(0, 3)]},
    '이라고': {'form': ('라고',),'begend': [(0, 2)]},
 }
