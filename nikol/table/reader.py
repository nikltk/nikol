from .object import Document, Sentence, Word
from .table import *

def reader(file, format=None):
    """
    :param format: (unified|mp|ls|ne|za|dp|sr|cr).(min|full).(tsv|csv)
    """
    if format.endswith('min.tsv'):
        return NikolMinTableReader(file, format)
    else:
        raise NotImplementedError()

           
class NikolMinTableReader:
    """
    A file reader for (unifiedi|mp|ls|ne|za|dp|sr|cr).min.(tsv|csv)
    """
    def __init__(self, file, format='unified.min.tsv'):
        self.format = format
        self.__file = file
        self.__document_list = None

    @property
    def filename(self):
        return self.__file.name

    @property
    def document_list(self):
        if self.__document_list is None:
            self.__document_list = []
            for doc in self:
                self.__document_list.append(doc)
            
        return self.__document_list


    def __iter__(self):
        if self.format == 'unified.min.tsv' :
            return self.__process_tsv()
        elif self.format == 'unified.min.csv' :
            raise NotImplementedError()
        else:
            raise Exception('Not supported format: {}'.format(self.format))

    def __process_tsv(self):
        file = self.__file
        docid = prev_docid = None
        sentid = prev_sentid = None
        docrows = []
        beg = end = 0
        sentnum = 1
        for line in file:
            fields = line.strip('\n').split('\t')
            sid, wid = fields[0].split('_')
            corpusid, dnum, pnum, snum = sid.split('-')
            
            if corpusid.startswith('N'):
                docid = '{}.{}'.format(corpusid, int(dnum))
                sentid = '{}.{}.{}.{}'.format(corpusid, int(dnum), int(pnum), int(snum))
            elif corpusid.startswith('S'):
                docid = corpusid
                sentid = '{}.{}'.format(corpusid, int(snum))

            # for spoken corpus
            # fill empty fields (dp_label, dp_head, sr_pred, sr_args)
            if len(fields) == 8 : fields += [None, None, None, None] 

            if docid is None:
                pass
            elif prev_docid is None:
                # first row of the data file
                # first document, first sentence
                sentnum = 1
                doc = Document(id=docid, sentence=[])
                sent = Sentence(parent=doc, num=sentnum, id=sentid, sentrows=[])
                beg = 0
                end = beg + len(fields[2])
                row = UnifiedMinRow(fields, sentence=sent)
                word = Word.from_min(row, begin=beg, end=end, parent=sent)
                sent.word.append(word)
                sent.form = word.form
                sent._rows.append(row)
                doc.sentence.append(sent)
            elif docid != prev_docid:
                # next new document
                # first row, first sentence
                yield doc
                doc = Document(id=docid, sentence=[])
                sentnum = 1
                sent = Sentence(parent=doc, num=sentnum, id=sentid, sentrows=[])
                beg = 0
                end = beg + len(fields[2])
                row = UnifiedMinRow(fields, sentence=sent)
                word = Word.from_min(row, begin=beg, end=end, parent=sent)
                sent.word.append(word)
                sent.form = word.form
                sent._rows.append(row)
                doc.sentence.append(sent)
            else:
                #
                # inside a document
                #
                if sentid == prev_sentid:
                    #
                    # inside a sentence
                    #
                    beg = end + 1
                    end = beg + len(fields[2])
                    row = UnifiedMinRow(fields, sentence=sent)
                    word = Word.from_min(row, begin=beg, end=end, parent=sent)
                    sent.word.append(word)
                    sent.form += ' ' + word.form
                    sent._rows.append(row)
                else:
                    #
                    # new sentence
                    # first row
                    #
                    sentnum += 1
                    sent = Sentence(parent=doc, num=sentnum, id=sentid, sentrows=[])
                    beg = 0
                    end = beg + len(fields[2])
                    row = UnifiedMinRow(fields, sentence=sent)
                    word = Word.from_min(row, begin=beg, end=end, parent=sent)
                    sent.word.append(word)
                    sent.form = word.form
                    sent._rows.append(row)
                    doc.sentence.append(sent)

            prev_docid = docid
            prev_sentid = sentid

        yield doc

