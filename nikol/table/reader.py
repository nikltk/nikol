import builtins
from .object import Document


def open(filename, format=None):
    """
    :param format: (unified|mp|ls|ne|za|dp|sr|cr).(min|full).(tsv|csv)
    """
    if format == 'unified.min.tsv':
        return NikolUnifiedMinTableReader(filename, format)
    else:
        raise NotImplementedError()




class Row:
    def __init__(self, fields = None, **kwargs):
        """ Row represents a line of unified min table data. 
        Consists of 12 fields: gid, swid, form, mp, ls, ne, za_pred, za_ante, dp_label, dp_head, sr_pred, sr_args.
        """
        if type(fields) is list and len(fields) == 12:
            (self.gid, self.swid, self.form,
             self.mp, self.ls, self.ne,
             self.za_pred, self.za_ante,
             self.dp_label, self.dp_head,
             self.sr_pred, self.sr_args) = fields
        else:
            raise Exception('Need a list of 12 fields. But given : {}'.format(fields));

        for name in kwargs:
            setattr(self, name, kwargs[name])
            
    def __str__(self):
        return str(self.__dict__)

class NikolUnifiedMinTableReader:
    """
    A file object for unified.min.(tsv|csv)
    """
    def __init__(self, filename, format='unified.min.tsv'):
        self.format = format
        self.__filename = filename
        self.__document_list = None

    @property
    def filename(self):
        return self.__filename

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
        with builtins.open(self.filename) as file:
            docid = prev_docid = None
            docrows = []
            for line in file:
                fields = line.strip('\n').split('\t')
                sid, wid = fields[0].split('_')
                cid, dn, pn, sn = sid.split('-')
                docid = '{}-{}'.format(cid, dn)

                # for spoken corpus
                # fill empty fields (dp.label, dp.head, sr.pred, sr.args)
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

