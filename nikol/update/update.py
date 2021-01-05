import copy
import datetime
from collections import defaultdict
from pathlib import Path
from warnings import warn

class Updater():
    def __init__(self):
        tag_list = 'mp ls ne za_pred za_ante dp_label dp_head sr_pred sr_args cr'.split(' ')
        self.col_idx = {v:i+3 for i,v in zip(range(len(tag_list)), tag_list)}

    def config(self, tsv_path, comment, log):
        self.tsv_path = Path(tsv_path)
        self.comment_file, self.comment_enc = Path(comment.name), comment.encoding
        self.log_file, self.log_enc = Path(log.name), log.encoding
        comment.close(); log.close()
        self.log_file.unlink()
        self.comment_file.unlink()

    def _rec_ddict(self):
        return defaultdict(self._rec_ddict)

    def load_prepatch(self, ppatch_file):
        self.patch = []
        self.comment_list = []
        # define pre_patch
        self.prepatch = self._rec_ddict()
        lines = [line.strip('\n') for line in ppatch_file]
        ppatch_file.close()

        for line in lines:
            one_ppatch = line.strip('\n').split('\t')
            if not len(one_ppatch) == 4:
                raise Exception(f"Line not composed of 4 columns, current line: {line}, number of columns : {len(one_ppatch)}")

            #check if comment
            if not one_ppatch[-1] == '':
                self.comment_list.append('\t'.join(one_ppatch))
            doc_id = '-'.join(one_ppatch[0].split('-')[:2])
            self.prepatch[doc_id][one_ppatch[0]][one_ppatch[1]] = one_ppatch[2]

    def make_patch(self):

        self._patch_dict = self._rec_ddict()

        for doc_id, gwid_items in self.prepatch.items():
            tsv_file = self.tsv_path/f'{doc_id}.unified.min.tsv'

            #TODO: need refactoring, repeated structure.... 1) tsv load and check 2) writable check
            if tsv_file.exists():

                with tsv_file.open(encoding = 'utf8') as f: lines = f.readlines()

                #to check if writable
                copied_tsv = copy.copy(lines)

                for line_idx, line in enumerate(lines):
                    tsv_line= line.strip('\n').split('\t')

                    # if matched line exists in prepatch
                    if tsv_line[0] in self.prepatch[doc_id].keys():

                        self._cp_patchline = copy.copy(self.prepatch[doc_id][tsv_line[0]])

                        for field, after in self.prepatch[doc_id][tsv_line[0]].items():

                            after = after.strip('\n')

                            #  CAUTION, shallow copys, be sure not to make change in nested object
                            del self._cp_patchline[field]

                            # fix morpheme unit in case [mp, ls, en]
                            if field.split('.')[0] in ['mp', 'ls', 'ne'] and '.' in field:

                                field_name, sub_field = field.split('.')
                                field_idx = self.col_idx[field_name]
                                before = tsv_line[field_idx].split(' + ')[int(sub_field)-1]

                                if not before == after:

                                    # --- from write
                                    sub_fields = tsv_line[field_idx].split(' + ')
                                    field_name, sub_idx = field.split('.')
                                    sub_fields[int(sub_idx)-1] = after
                                    tsv_line[field_idx] = ' + '.join(sub_fields)
                                    lines[line_idx] = '\t'.join(tsv_line).strip('\n') + '\n'
                                    # ---

                                    self._patch_dict[doc_id][tsv_line[0]][field] = after
                                    self.patch.append([tsv_line[0], field, before, after, ''])


                            else:
                                field_idx = self.col_idx[field]
                                before = tsv_line[field_idx].strip('\n')

                                if not tsv_line[field_idx] == after:
                                    
                                    # --- from write
                                    field_idx = self.col_idx[field]
                                    tsv_line[field_idx] = after
                                    lines[line_idx] = '\t'.join(tsv_line).strip('\n') + '\n'
                                    # ---                                

                                    self._patch_dict[doc_id][tsv_line[0]][field] = after
                                    self.patch.append([tsv_line[0], field, before, after, ''])



                        # error Not all prepatchs reviewed line field has not existing gwid
                        if self._cp_patchline:
                            raise Exception(f"Some prepatch lines not checked, gwid: {self._cp_patchline.keys()}, field: {tsv_line[0]}")
                        self._cp_patchline = {}
                        
                if not len(lines) == len(copied_tsv):
                    raise Exception(f"{tsv_file.name} tsv patch before/after line number not matched. before: {len(copied_tsv)}, after: {len(lines)}")

            else:
                raise Exception(f"corresponding tsv file doesn't exist, given prepatch document id: {doc_id}")

        self.patch.sort()

    def write(self):
        self.datenow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self._patch_dict:
            for doc_id, gwid_items in self._patch_dict.items():
                tsv_file = self.tsv_path/f'{doc_id}.unified.min.tsv'

                with tsv_file.open(encoding = 'utf8') as f: lines = f.readlines()
                copied_original = copy.copy(lines)

                for line_idx, line in enumerate(lines):
                    tsv_line= line.split('\t')
                    if tsv_line[0] in self._patch_dict[doc_id].keys():
                        for field, after in self._patch_dict[doc_id][tsv_line[0]].items(): 

                            if field.split('.')[0] in ['mp', 'ls', 'ne'] and '.' in field:
                                field_name, sub_idx = field.split('.')
                                field_idx = self.col_idx[field_name]
                                sub_fields = tsv_line[field_idx].split(' + ')
                                sub_fields[int(sub_idx)-1] = after

                                tsv_line[field_idx] = ' + '.join(sub_fields)

                                lines[line_idx] = '\t'.join(tsv_line).strip('\n') + '\n'
                                
                            else:
                                field_idx = self.col_idx[field]

                                tsv_line[field_idx] = after

                                lines[line_idx] = '\t'.join(tsv_line).strip('\n') + '\n'

                if not copied_original == lines:
                    with tsv_file.open('w') as f: print(''.join(lines).strip('\n'), file=f)

        if self.comment_list:
            with self.comment_file.open('w', encoding = self.comment_enc) as f:
                for log in self.comment_list:
                    line = log.split('\t')[:2] + [self.datenow] + [log.split('\t')[-1]]
                    print('\t'.join(line).strip('\n'), file = f)

        if self.patch:
            with self.log_file.open('w', encoding = self.log_enc) as f:
                for log in self.patch:
                    line = log[:2] + [self.datenow] + log[2:4]
                    print('\t'.join(line).strip('\n'), file = f)
