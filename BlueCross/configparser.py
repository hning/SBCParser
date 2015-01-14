from config import *
from TableClass import *
import string

print "Imported ConfigParser"

class ConfigParser:
	def __init__(self, _config, _table):
		self.config =  _config
		self.table = _table

		self.execute()

	def execute(self):
		#Iterate through rows to determine if they one of the key rows
		#Find first non-empty column

		if len(self.table.table) == 0:
			return

		for row in self.table.table:
			i = 0
			for col in row:
				if len(col) == 0:
					i += 1
				else:
					break

			#Final column or no columns with text
			if i >= (len(row) - 1) or len(row[i]) == 0:
				print "Row wrong {0}".format(i)
				continue

			#Searching for row that matches
			to_delete = ""
			for key in self.config.data:


				found_all = True
				for el in self.config.data[key]["contains"]:
					if not el in row[i].lower():
						found_all = False
						break

				if found_all is False:
					continue
				#Get all elements within cell, assume next cell
				key_info = self.parse_cell(row[i+1], self.config.data[key]["type"])

				if not len(key_info) == len(self.config.data[key]["output_format"]):
					print "Given: {0} Required: {1}".format(len(key_info), len(self.config.data[key]["output_format"]))
					continue

				#Output key-value pairs
				for idx in xrange(len(key_info)):
					print "{0}:{1}".format(self.config.data[key]["output_format"][idx]["name"], key_info[idx])

				if found_all is True:
					to_delete = key
					break

			if not to_delete is "":
				del self.config.data[to_delete]

	def number_parse(self, text):
		return [int(s.translate(None, string.punctuation)) for s in text.split() if s.translate(None, string.punctuation).isdigit()]

	def boolean_parse(self, text, in_type):
		text = text.lower()
		return [text.rstrip()]

	def money_parse(self, text):
		return [int(s.translate(None, string.punctuation)) for s in text.split() if ("$" in s and s.translate(None, string.punctuation).isdigit())]

	def parse_cell(self, cell, in_type):
		#Types: number, boolean

		print in_type

		if in_type == "number":
			return self.number_parse(cell)
		elif "boolean" in in_type:
			return self.boolean_parse(cell, in_type)
		elif in_type == "money":
			return self.money_parse(cell)
		else: 
			print "ERROR: Type '{0}' is not present".format(in_type)

		return []
