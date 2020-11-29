def decompose(han) : 
    num = ord(han) - 0xac00
    lead = num // 588
    vt = num % 588
    vowel = vt // 28
    trail = vt % 28

    return [lead, vowel, trail]



def form_match(lemmatized_form, sentence_form, lemma_position_slice=None):
    
    lemma = lemmatized_form
    if lemma_position_slice is None:
        word = sentence_form
    else:
        word = sentence_form[lemma_position_slice]

    
    result = False 

    
    if lemma == '저' and word == '제' : result = True
    elif lemma == '나' and word == '내' : result = True
    elif lemma == '너' and word == '네' : result = True
    elif lemma == '누구' and word == '누가' : result = True
    elif lemma.endswith('거') and word.endswith('게') and lemma[:-1] == word[:-1] :
        result = True
    elif lemma.endswith('것') and word.endswith('게') and lemma[:-1] == word[:-1] :
        result = True
    elif decompose(lemma[-1])[0:2] == decompose(word[-1])[0:2]:
        result = True 
        
    return result

