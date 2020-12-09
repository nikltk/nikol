
import koltk.corpus.nikl.annotated as nikl

class Document(nikl.Document):
    def __init__(self, docrows):
        """
        :param docrows: list of Rows in the document
        """
        self.__rows = docrows
        self.sentence = None
        self.__process()
        


    @property
    def rows(self):
        return self.__rows
    
    @property
    def sentence_list(self):
        if self.sentence is None:
            self.__process()


        return self.sentence
    
    def __process(self):
        docrows = self.rows
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
        
        self.word = []
        self.morpheme = []
        self.WSD = []
        self.NE = []
        beg = end = 0
        for row in sentrows:
            end = beg + len(row.form)
            self.word.append(Word(row, begin=beg, end=end))
            beg = end + 1

            for morph in row.mp.split(' + '):
                self.morpheme.append(morph)
            for wsd in row.ls.split(' + '):
                self.WSD.append(wsd)

            if row.ne != '' and row.ne != '&':
                for ne in row.ne.split(' + '):
                    self.NE.append(ne)
            #self.DP = []
            #self.SRL = []
            
        
    @property
    def rows(self):
        return self.__rows

    @property
    def word_list(self):
        if self.word is None:
            self.word = []
            for row in self.rows:
                self.word.append(Word(row))

        return self.word

class Word(nikl.Word):
    def __init__(self, row, begin = None, end = None):
        self.__row = row
        self.id = int(row.gid.split('_')[1])
        self.form = row.form
        self.begin = begin
        self.end = end


    @property
    def row(self):
        return self.__row


    @property
    def gid(self):
        return self.__row.gid

class Morpheme(nikl.Morpheme):
    pass

class WSD(nikl.WSD):
    pass

class NE(nikl.NE):
    pass


