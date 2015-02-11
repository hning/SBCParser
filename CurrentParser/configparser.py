from config import *
from TableClass import *
import string
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ConfigParser:
	def __init__(self, _config, _table):
		self.config =  _config
		self.table = _table
		
		self.output_dict = {}

		self.execute()

	def get_dict(self):
		print "get_dict {0}".format(len(self.output_dict))
		return self.output_dict

	def get_dict_string(self):

		output_str = ""
		for key,value in self.output_dict.iteritems():
			output_str = output_str + "{0}:{1}\n".format(key,value)
		return output_str

	def write_to_file(self, _output_file):
		output_file = open(_output_file, "a")
		output_file.write(self.get_dict_string());

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

				if found_all is True and key_info is True:
					to_delete = key
					break
				
			if not to_delete is "":
				del self.config.data[to_delete]

	def embedded_money_search(self, text):
		dollar_locations = []
		location = 0
		final_location = len(text)
		money_arr = []
		print final_location
		try:
			while location < final_location:
				new_loc = text[location:].index('$')
				
				dollar_locations.append(location+new_loc)
				location = location + new_loc + 1
		except:
			print "except"
			

		for index in dollar_locations:
			next_index = index+1
			while next_index < final_location and (text[next_index].isdigit() or text[next_index] is ","):
				next_index = next_index + 1
			money_arr.append(int(re.sub(r'[^\w\s]', '', text[index:next_index])))

		return money_arr


	def deductible_parse(self, text, info):
		money_arr = [int(re.sub(r'[^\w\s]', '', s)) for s in text.split() if ("$" in s and re.sub(r'[^\w\s]', '', s).isdigit())]
		num_values = len(money_arr)
		output_arr = []

		if num_values == 0:
			#Search for possible embedded numbers inside strings
			money_arr = self.embedded_money_search(text)
			num_values = len(money_arr)
		# 4 values means contains non-network prices
		# Network prices: Individual/Family
		# Non-Network prices: Individual Family

		if num_values == 4:
			self.output_dict["{0}_individual_in-network".format(info["prefix"])] = money_arr[0]
			self.output_dict["{0}_family_in-network".format(info["prefix"])] = money_arr[1]
			self.output_dict["{0}_individual_out-network".format(info["prefix"])] = money_arr[2]
			self.output_dict["{0}_family_out-network".format(info["prefix"])] = money_arr[3]
			# output_arr.append("{0}_individual_in-network:{1}".format(info["prefix"],money_arr[0]))
			# output_arr.append("{0}_family_in-network:{1}".format(info["prefix"],money_arr[1]))
			# output_arr.append("{0}_individual_out-network:{1}".format(info["prefix"],money_arr[2]))
			# output_arr.append("{0}_family_out-network:{1}".format(info["prefix"],money_arr[3]))
		# 2 values means doesn't matter
		# Individual/Family
		elif num_values == 2:
			self.output_dict["{0}_individual".format(info["prefix"])] = money_arr[0]
			self.output_dict["{0}_family".format(info["prefix"])] = money_arr[1]
			# output_arr.append("{0}_individual:{1}".format(info["prefix"],money_arr[0]))
			# output_arr.append("{0}_family:{1}".format(info["prefix"],money_arr[1]))
		elif num_values == 1:
			self.output_dict[info["prefix"]] = money_arr[0]
			# output_arr.append("{0}:{1}".format(info["prefix"],money_arr[0]))
		else:
			print "Size of money array is not 2 or 4 (Size={0})".format(num_values)
			return False

		return True

	def number_parse(self, text):
		return [int(re.sub(r'[^\w\s]', '', s)) for s in text.split() if (re.sub(r'[^\w\s]', '', s).isdigit())]
		# return [int(s.translate(None, string.punctuation)) for s in text.split() if s.translate(None, string.punctuation).isdigit()]

	def boolean_parse(self, text, info):

		possible_values = ["true", "yes", "false", "no"]
		replace_punctuation = string.maketrans(string.punctuation, ' '*len(string.punctuation))
		no_punc_text = re.sub(r'[^\w\s]', ' ', text).lower()
		no_punc_text = ' ' + no_punc_text + ' '

		output_arr = []
		#Finding the possible values within the boolean
		for val in possible_values:
			if (' ' + val + ' ') in no_punc_text:
				output_arr = [val] 
				break

		info_types = info["type"].split("-")

		for i in range(1,len(info_types)):
			next_arr = []
			if info_types[i] == "number":
				next_arr = self.number_parse(text)
				for i in next_arr:
					output_arr = [output_arr[0] + "|" + str(i)]


		self.output_dict[info["output_format"][0]["name"]] = output_arr[0]
		# self.output_file.write("{0}:{1}\n".format(info["output_format"][0]["name"],output_arr[0]))

		return True

	def money_parse(self, text, info):
		return [int(s.translate(None, string.punctuation)) for s in text.split() if ("$" in s and s.translate(None, string.punctuation).isdigit())]

	def parse_cell(self, cell, info):
		#Types: number, boolean

		# print in_type

		info_types = info["type"].split("-")

		if "number" == info_types[0]:
			return self.number_parse(cell)
		elif "boolean" == info_types[0]:
			return self.boolean_parse(cell, info)
		elif "deductible" == info_types[0]:
			return self.deductible_parse(cell, info)
		elif "money" == info_types[0]:
			return self.money_parse(cell, info)
		# elif in_type == "money-variable":
		# 	return self.variable_deductible_money_parse(cell):
		else: 
			print "ERROR: Type '{0}' is not present".format(in_type)

		return False
		# return output_arr
