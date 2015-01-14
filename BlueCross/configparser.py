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
				key_info = self.parse_cell(row[i+1], self.config.data[key])

				if "variable" in self.config.data[key]["type"]:
					for value in key_info:
						print value
				else: 
					if not len(key_info) == len(self.config.data[key]["output_format"]):
						print "Given: {0} Required: {1}".format(len(key_info), len(self.config.data[key]["output_format"]))
						continue
					#Output key-value pairs
					for idx in xrange(len(key_info)):
						print "{0}:{1}".format(self.config.data[key]["output_format"][idx]["name"], key_info[idx])

				if found_all is True and len(key_info) > 0:
					to_delete = key
					print ""
					break
				


			if not to_delete is "":
				del self.config.data[to_delete]

	def variable_money_parse(self, text, info):
		money_arr = [int(s.translate(None, string.punctuation)) for s in text.split() if ("$" in s and s.translate(None, string.punctuation).isdigit())]
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
		else:
			print "Size of money array is not 2 or 4 (Size={0})".format(num_values)

		return output_arr

	def number_parse(self, text):
		return [int(s.translate(None, string.punctuation)) for s in text.split() if s.translate(None, string.punctuation).isdigit()]

	def boolean_parse(self, text, info):
		text = text.lower()

		possible_values = ["true", "false", "yes", "no"]
		replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
		text = text.translate(replace_punctuation)
		text = ' ' + text + ' '

		#Finding the possible values within the boolean
		for val in possible_values:
			if (' ' + val + ' ') in text:
				return [val] 

		return [text.rstrip()]

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
