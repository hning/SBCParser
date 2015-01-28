from pdfminer.pdfparser import PDFParser, PDFSyntaxError
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTTextLineHorizontal, LTTextBoxHorizontal, \
                            LTChar, LTRect, LTLine
from pdfminer.pdfpage import PDFPage
from operator import itemgetter, attrgetter, methodcaller
import os
import base64, re, datetime, StringIO
import math
import sys

from collections import defaultdict

overlap_threshold = 0.7

import math
def is_line_vertical(el):
    horizontal_distance = math.fabs(el.x1 - el.x0)
    vertical_distance = math.fabs(el.y1 - el.y0)

    #Assume that its a vertical line if the horizontal distance 
    # is less than 1% of the vertical distance
    if horizontal_distance <= vertical_distance*.01:
        return True
    return False

def is_line_horizontal(el):
    horizontal_distance = math.fabs(el.x1 - el.x0)
    vertical_distance = math.fabs(el.y1 - el.y0)

    #Assume that its a vertical line if the horizontal distance 
    # is less than 1% of the vertical distance
    if vertical_distance <= horizontal_distance*.01:
        return True
    return False

def overlap_above_row(row_x0, row_x1, x0, x1):
	if x1 >= row_x1:
		return True
	return False

def get_string_from_list(str_list, remove_tuple=(0,0)):
	#Removing below
	print "Before: {0}".format('\n'.join(str_list))
	print remove_tuple
	if remove_tuple[0] > 0:
		del str_list[-remove_tuple[0]:]

	#Removing above
	if remove_tuple[1] > 0:
		del str_list[:remove_tuple[1]]

	print "After: {0}".format('\n'.join(str_list))

	return '\n'.join(str_list)

def get_lines(row_y0, row_y1, textbox_input):
	lines = textbox_input.get_text().splitlines()
	original_num_lines = len(lines)
	text_y0 = textbox_input.y0
	text_y1 = textbox_input.y1

	remove_below = 0
	remove_above = 0

	# Check if the textbox exists below the box; remove those elements
	if text_y0 < row_y0:
		percent = interval_overlap(text_y0, row_y0, text_y0, text_y1, False)
		remove_below = math.trunc(percent * original_num_lines)

		# print "Below: {0}".format(percent)

	# Check if the textbox exists above the box;
	if text_y1 > row_y1:
		percent = interval_overlap(row_y1, text_y1, text_y0, text_y1, False)
		remove_above = math.trunc(percent*original_num_lines)

		# print "After: {0} {1}".format(percent, remove_above)

	print "Tuple: {0} {1}".format(remove_below, remove_above)
	return (remove_below, remove_above)

def interval_overlap(first_x0, first_x1 , second_x0, second_x1, is_min=True):
	if is_min is True:
		divisor = min(first_x1 - first_x0, second_x1 - second_x0)
	else:
		divisor = max(first_x1 - first_x0, second_x1 - second_x0)
	numerator = 0

	# print "{0} {1} {2} {3}".format(first_x0, first_x1 , second_x0, second_x1)

	# None overlap
	if ((first_x0 < second_x0 and first_x1 <= second_x0) or \
		(second_x0 < first_x0 and second_x1 <= first_x0)) and is_min:
		return 0
	# Completely subsumed
	elif ((first_x0 < second_x0 and first_x1 > second_x1) or \
		(second_x0 < first_x0 and second_x1 > first_x1)) and is_min:
		return 1
	# First interval has left overhang
	elif (first_x0 <= second_x0 and first_x1 > second_x0):
		numerator = first_x1 - second_x0
	# Second interval has left overhang
	elif (second_x0 <= first_x0 and second_x1 > first_x0):
		numerator = second_x1 - first_x0

	# if numerator/divisor > 0.9, return 
	return numerator/divisor


class TableClassHorizontal:
	def __init__(self):
		self.row_delimiters = []
		self.column_delimiters = []
		self.table = []
		self.processed_table = []
		self.textboxes = []
		self.overlapping = defaultdict(list)

	def clear_elements(self):
		self.row_delimiters = []
		self.column_delimiters = []
		self.table = []
		self.processed_table = []
		self.textboxes = []
		self.overlapping = defaultdict(list)

	def process_elements(self, element_list):
		self.clear_elements()

		# Find Horizontal Rects
		horizontal_dict = defaultdict(list)

		for el in element_list:
			if type(el) == LTRect:
				if is_line_horizontal(el):
					horizontal_dict[el.x0].append(el)
			elif type(el) == LTTextBoxHorizontal:
				self.textboxes.append(el)

		# Find the x0 values (Column dividers)
		for key,value in list(horizontal_dict.items()):
			if len(value) < 5:
				del horizontal_dict[key]

		row_delimiter_dict = defaultdict(int)

	    # Set column_delimiters and count row_delimiters
		for key,value in list(horizontal_dict.items()):
			for v in value:
				row_delimiter_dict[v.y0] = row_delimiter_dict[v.y0] + 1
			self.column_delimiters.append(key)

	    # Find row delimiters
		for key,value in row_delimiter_dict.items():
			if value >= len(self.column_delimiters):
				self.row_delimiters.append(key)

	    # Sort both lists
		self.column_delimiters.sort()
		self.row_delimiters.sort()

	    # Construct table object
		for i in range(0, len(self.row_delimiters) + 1):
			row = []
			for j in range(0, len(self.column_delimiters) + 1):
				row.append([])

			self.table.append(row)

		self.fill_table()
		self.post_process_table()

	def fill_table(self):
		for el in self.textboxes:
			row_num = 0
			col_num = 0
			found = False

			# Find elements that overlap into 2 columns or 2 rows
			for i in range(1, len(self.column_delimiters)):
				overlap = interval_overlap\
							(self.column_delimiters[i-1], self.column_delimiters[i],\
								el.x0, el.x1)

				if overlap > 0.1:
					break

				col_num = col_num + 1

			for i in range(1, len(self.row_delimiters)):
			#for i in range(len(self.row_delimiters)-1, 0, -1):
				overlap = interval_overlap\
							(self.row_delimiters[i-1], self.row_delimiters[i],\
								el.y0, el.y1)
				if overlap > 0.3:
					print "Overlap: {0}".format(overlap)
					print el
					if overlap < 0.9 or  overlap_above_row(self.row_delimiters[i-1], self.row_delimiters[i],\
								el.y0, el.y1):
						#Deal with vertical overlap
						lines = el.get_text().splitlines()
						print lines

						print "Vertical Overlap: {0} {1} {2} {3}".format(self.row_delimiters[i-1], self.row_delimiters[i],\
									el.y0, el.y1)
						print overlap
						print el

						self.overlapping[row_num].append(col_num)
					break

				row_num = row_num+1

			if row_num < 0 or col_num < 0:
				print "Row: {0} Col: {1} Negative".format(row_num, col_num)
				print el
				continue

			print "Row: {0} Col: {1}".format(row_num, col_num)
			self.table[row_num][col_num].append(el)

	def post_process_table(self):
		# Go through each element that has proven to be vertically overlapping

		print "### POST PROCESS TABLE"
		print self.overlapping
		for row in range(0, len(self.table)):
			self.processed_table.append([])
			for col in range(0, len(self.table[row])):
				cell_text = ""
				if col in self.overlapping[row]:
					for textbox in sorted(self.table[row][col], key=attrgetter('y1'), reverse=True):
						lines_arr = textbox.get_text().splitlines()
						remove_tuple = get_lines(self.row_delimiters[row], self.row_delimiters[row+1], textbox)
						cell_text = get_string_from_list(lines_arr, remove_tuple)

						#There's text above
						if remove_tuple[1] > 0 and (row+1 < len(self.table)):
							self.table[row+1][col].append(textbox)
							self.overlapping[row+1].append(col)
				else:
					
					for textbox in sorted(self.table[row][col], key=attrgetter('y1'), reverse=True):
						cell_text = cell_text + textbox.get_text()

				self.processed_table[row].append(cell_text)

		# for o in self.overlapping:
		# 	row = o[0]
		# 	column = o[1]

		# 	print "{0} {1}".format(row, column)
		# 	for el in self.table[row][column]:
		# 		text = ""
		# 		text = text + el.get_text() + "\n"
		# 		lines = text.splitlines()
		# 		print self.table[row][column]
		# 		print lines




	def print_delimiters(self):
		print "\nRow Delimiters: "
		for i in self.row_delimiters:
			print "{0} ".format(i),

		print "\nCol Delimiters: "
		for i in self.column_delimiters:
			print "{0} ".format(i),
		
	def print_table(self):
		for i,r in enumerate(self.table):
			print "\n\nRow {0}".format(i)
			for c in r:
				print "|",
				for el in c:
					print el

	def print_final_table(self):
		for i,r in enumerate(self.processed_table):
			print "\n\nRow {0}".format(i)
			for c in r:
				print "|",
				print c






