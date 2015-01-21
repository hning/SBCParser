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

def interval_overlap(first_x0, first_x1 , second_x0, second_x1):
	divisor = max(first_x1 - firstx0, second_x1, second_x0)

	if (first_x0 < second_x0 and first_x1 < second_x0) or \
		(second_x1)

class TableClassHorizontal:
	def __init__(self):
		self.row_delimiters = []
		self.column_delimiters = []
		self.table = []
		self.textboxes = []

	def clear_elements(self):
		self.row_delimiters = []
		self.column_delimiters = []
		self.table = []
		self.textboxes = []

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
		self.post_process_table(0)

	def fill_table(self):
		for el in self.textboxes:
			row_num = -1
			col_num = -1

			# Find elements that overlap into 2 columns or 2 rows


			for c in self.column_delimiters:
				if c > el.x0:
					break
				col_num = col_num + 1
			
			for r in self.row_delimiters:
				if r > el.y0:
					break
				row_num = row_num + 1

			if row_num < 0 or col_num < 0:
				print "Row: {0} Col: {1} Negative".format(row_num, col_num)
				continue

			print "Row: {0} Col: {1}".format(row_num, col_num)
			self.table[row_num][col_num].append(el)

	def post_process_table(self):
		# Find 


	def print_delimiters(self):
		print "\nRow Delimiters: "
		for i in self.row_delimiters:
			print "{0} ".format(i),

		print "\nCol Delimiters: "
		for i in self.column_delimiters:
			print "{0} ".format(i),
		
	def print_table(self):
		for i,r in enumerate(self.table):
			print "\nRow {0}".format(i)
			for c in r:
				for el in c:
					print el






