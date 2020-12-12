import builtins
from .object import Document, Row


def reader(file, format=None):
    """
    :param format: (unified|mp|ls|ne|za|dp|sr|cr).(min|full).(tsv|csv)
    """
    if format == 'unified.min.tsv':
        return NikolUnifiedMinTableReader(file, format)
    elif format == 'mp.min.tsv':
        return NikolMPMinTableReader(file, format)
    else:
        raise NotImplementedError()

           
class NikolUnifiedMinTableReader:
    """
    A file object for unified.min.(tsv|csv)
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
        docrows = []
        for line in file:
            fields = line.strip('\n').split('\t')
            sid, wid = fields[0].split('_')
            cid, dn, pn, sn = sid.split('-')
            docid = '{}-{}'.format(cid, dn)

            # for spoken corpus
            # fill empty fields (dp_label, dp_head, sr_pred, sr_args)
            if len(fields) == 8 : fields += [None, None, None, None] 


            if docid is None:
                pass
            elif prev_docid is None:
                docrows = [Row(fields)]
            elif docid != prev_docid:
                yield Document(docrows)
                docrows = [Row(fields)]
            else:
                docrows.append(Row(fields))

            prev_docid = docid

        yield Document(docrows)

