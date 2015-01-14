from config import *
from BlueCrossParser import *

class ConfigParser:
	def __init__(self, _config, _table):
		self.config =  _config
		self.table = _table

		self.execute()

	def execute(self):
		#Iterate through rows to determine if they one of the key rows
		#Find first non-empty column

		if len(table.table) == 0:
			return

		for row in table.table:
			i = 0
			for col in row:
				if len(col.get_text().strip()) == 0:
					break
				else:
					i += 1

			#Final column or no columns with text
			if i >= (len(row) - 1) or len(row[i].get_text().strip()) == 0:
				continue

			#Searching for row that matches
			to_delete = ""
			for key in self.config.data:
				found_all = True
				for el in self.config.data[key].contains:
					if not el in row[i]:
						found_all = False
						break

				#Get all elements within cell, assume next cell
				key_info = parse_cell(row[i+1], self.config.data[key]["type"])

				if not len(key_info) == len(self.config.data[key]["output_format"]):
					continue

				#Output key-value pairs
				for idx in xrange(len(key_info)):
					print "{0}:{1}\n".format(self.config.data[key]["output_format"][idx], key_info[indx])

				if found_all is True:
					to_delete = key
					break

			if not to_delete is "":
				del self.config.data[to_delete]

	def number_parse(self, text):
		return [int(s) for s in text.split() if s.isdigit()]

	def boolean_parse(self, text, in_type):
		text = text.lower()
		return [text]

	def parse_cell(self, cell, in_type):
		#Types: number, boolean

		text = ""
		for cell in cell_arr:
            text += cell.get_text().encode('utf-8')

		if in_type is "number":
			return self.number_parse(text)
		elif "boolean" in in_type:
			return self.boolean_parse(text, in_type)
		else: 
			print "ERROR: Type '{0}' is not present\n".format(in_type)

		return []
