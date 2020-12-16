from collections import defaultdict
from pathlib import Path

from warnings import warn

class Updater():
	def __init__(self, comment = None, log = None):
		self.comment = comment
		self.log = log
		self.tsv_path = Path('/Users/hapkim/Desktop/kr_inst/annotated-documents-split-20-min-tsv/unified_min_tsv')
		self.patch = []

	#TODO: define attributes
	@classmethod
	def Config(cls, comment, log):
		pass

	def _rec_ddict(self):
		return defaultdict(self._rec_ddict)

	def load_prepatch(self, ppatch_path):
		self.prepatch_path = Path(ppatch_path)
		if not self.prepatch_path.suffix == '.tsv':
			warn(f'File extension is not tsv, current: {self.prepatch_path.suffix}')		

		with self.prepatch_path.open() as f:

		# define pre_patch
			self.prepatch = self._rec_ddict()

			for line in f:
				one_ppatch = line.strip('\n').split('\t')
				
				if not len(one_ppatch) == 4:
					raise Exception("Line not composed of 4 columns")

				#check if comment
				if not one_ppatch[-1] == '':
					self.patch.append(one_ppatch)

				
				doc_id = '-'.join(one_ppatch[0].split('-')[:2])
				self.prepatch[doc_id][one_ppatch[0]][one_ppatch[1]] = one_ppatch[2]

	def _field2idx(self):
		tag_list = 'mp ls ne za_pred za_ante dp_label dp_head sr_pred sr_args cr'.split(' ')
		self.col_idx = {v:i+3 for i,v in zip(range(len(tag_list)), tag_list)}

	def make_patch(self):

		self._field2idx()
		for doc_id, gwid_items in self.prepatch.items():
			tsv_file = self.tsv_path/f'{doc_id}.unified.min.tsv'

			# print(f"loaded tsv_file: {tsv_file.stem}")

			if tsv_file.exists():
				with tsv_file.open() as f:

					for line in f:
						tsv_line= line.split('\t')

						# if matched line exists in prepatch
						if tsv_line[0] in self.prepatch[doc_id].keys():

							for field, after in self.prepatch[doc_id][tsv_line[0]].items():

								# fix morpheme unit
								if '.' in field:

									# print(f"check if field match: {field}")

									field_name, sub_field = field.split('.')
									field_idx = self.col_idx[field_name]

									if not tsv_line[field_idx].split(' + ')[sub_field] == after:
										#time, before, after, 
										self.patch.append([tsv_line[0], field, after, ''])

								# fix word unit
								else:
									# print(f"check if field match: {tsv_line[0], field}")
									field_idx = self.col_idx[field]
									if not tsv_line[field_idx] == after:
										self.patch.append([tsv_line[0], field, after, ''])


			else:
				raise Exception(f"corresponding tsv file doesn't exist, given prepatch document id: {doc_id}")

		self.patch.sort()

	def write():
		datetime.datetime.now().strftime("%y%m%d-%H%M%S")
		pass