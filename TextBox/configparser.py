from config import *
from TableClass import *
import string
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def translate_non_alphanumerics(to_translate, translate_to=u'_'):
    not_letters_or_digits = u'!"#%\'()*+,-./:;<=>?@[\]^_`{|}~'
    translate_table = dict((ord(char), translate_to) for char in not_letters_or_digits)
    return to_translate.translate(translate_table)

class ConfigParser:
	def __init__(self, _config, _table, _output_file):
		self.config =  _config
		self.table = _table
		self.output_file = open(_output_file, "a")

		self.execute()

	def execute(self):
		#Iterate through rows to determine if they one of the key rows
		#Find first non-empty column

		if len(self.table) == 0:
			return

		for row in self.table:
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
				key_info = self.parse_cell(row[i+1], self.config.data[key])

				if "variable" in self.config.data[key]["type"]:
					for value in key_info:
						self.output_file.write("{0}\n".format(value))
				else: 
					if not len(key_info) == len(self.config.data[key]["output_format"]):
						self.output_file.write("Given: {0} Required: {1}\n".format(len(key_info), len(self.config.data[key]["output_format"])))
						continue
					#Output key-value pairs
					for idx in xrange(len(key_info)):
						self.output_file.write("{0}:{1}\n".format(self.config.data[key]["output_format"][idx]["name"], key_info[idx]))

				if found_all is True and len(key_info) > 0:
					to_delete = key
					break
				
			if not to_delete is "":
				del self.config.data[to_delete]

	def variable_money_parse(self, text, info):
		money_arr = [int(re.sub(r'[^\w\s]', '', s)) for s in text.split() if ("$" in s and re.sub(r'[^\w\s]', '', s).isdigit())]
		num_values = len(money_arr)
		output_arr = []

		# 4 values means contains non-network prices
		# Network prices: Individual/Family
		# Non-Network prices: Individual Family
		if num_values == 4:
			output_arr.append("{0}_individual_in-network:{1}".format(info["prefix"],money_arr[0]))
			output_arr.append("{0}_individual_in-network:{1}".format(info["prefix"],money_arr[1]))
			output_arr.append("{0}_individual_in-network:{1}".format(info["prefix"],money_arr[2]))
			output_arr.append("{0}_individual_in-network:{1}".format(info["prefix"],money_arr[3]))
		# 2 values means doesn't matter
		# Individual/Family
		elif num_values == 2:
			output_arr.append("{0}_individual:{1}".format(info["prefix"],money_arr[0]))
			output_arr.append("{0}_individual:{1}".format(info["prefix"],money_arr[1]))
		elif num_values == 1:
			output_arr.append("{0}:{1}".format(info["prefix"],money_arr[0]))
		else:
			print "Size of money array is not 2 or 4 (Size={0})".format(num_values)

		return output_arr

	def number_parse(self, text):
		return [int(s.translate(None, string.punctuation)) for s in text.split() if s.translate(None, string.punctuation).isdigit()]

	def boolean_parse(self, text, info):

		possible_values = ["true", "yes", "false", "no"]
		replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
		# no_punc_text = text.translate(replace_punctuation).lower()
		no_punc_text = re.sub(r'[^\w\s]', ' ', text).lower()
		no_punc_text = ' ' + no_punc_text + ' '

		output_arr = []
		#Finding the possible values within the boolean
		for val in possible_values:
			if (' ' + val + ' ') in no_punc_text:
				output_arr = [val] 
				break

		if len(output_arr) == 0:
			return output_arr

		if "extra" in info["type"]:
			output_arr = [output_arr[0] + "|" + text]

		return output_arr

	def money_parse(self, text, info):
		if "variable" in info["type"]:
			return self.variable_money_parse(text, info)
		return [int(s.translate(None, string.punctuation)) for s in text.split() if ("$" in s and s.translate(None, string.punctuation).isdigit())]

	def parse_cell(self, cell, info):
		#Types: number, boolean

		# print in_type

		if info["type"] == "number":
			return self.number_parse(cell)
		elif "boolean" in info["type"]:
			return self.boolean_parse(cell, info)
		elif "money" in info["type"]:
			return self.money_parse(cell, info)
		# elif in_type == "money-variable":
		# 	return self.variable_deductible_money_parse(cell):
		else: 
			print "ERROR: Type '{0}' is not present".format(in_type)

		return []
