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

import config
from config import *

from TableClass import *

from TableClassHorizontal import *

overlap_threshold = 0.7

min_elements_in_row = 0

#default 0.3, 0.25 works for OEMgroup
#This is the separation between lines that pdfminer uses for textbox analysis
line_margin_threshold = 0.25

#default 0.2
word_margin_threshold = 0.1

#Most information on the tables are within the first two pages
pages_to_view = 1

#Unused at the moment
titles = ["Important Questions", "Answers", "Why This Matters:"]

import configparser
from configparser import *

def getRows(layout, config):
    objstack = list(reversed(layout._objs))
    rows = TableRows()
    objArr = []
    rectArr = []
    lineArr = []
    textboxArr = []

    column_arr = set()
    row_arr = set()

    contains_question = []

    max_x = 0
    max_y = 0

    while objstack:
        obj = objstack.pop()
        objArr.append(obj)
        # print "{0} {1} {2} {3}".format(obj.x0, obj.x1,
        #             obj.y0,obj.y1)
       

        if type(obj) == LTTextBoxHorizontal:
            #Rects could look for question marks. Multiple question marks == Textbox Split
            textboxArr.append(obj)
            text = strip_text(obj.get_text())
            if len(text) > 0:
                # print text.encode('utf-8');
                # print "{0} {1} {2} {3}".format(obj.x0, obj.x1,
                #     obj.y0,obj.y1)
                # print obj
                # print ""
                is_title = False

                if is_title: 
                    continue
                rows.add(obj)

                if "?" in text:
                    contains_question.append(obj)

        elif type(obj) == LTRect:

            if is_line_vertical(obj):
                lineArr.append(obj)
                column_arr.add(obj.x0)
                row_arr.add(obj.y0)
                max_x = max(max_x, obj.x1)
                max_y = max(max_y, obj.y1)
            rectArr.append(obj)



    column_arr.add(max_x)
    row_arr.add(max_y)

    print ""
    textboxArr = sorted(textboxArr, key=attrgetter('x0','y0'))
    for t in textboxArr:
        print t

    print ""
    contains_question  = sorted(contains_question , key=attrgetter('y0'), reverse=True)
    for l in contains_question :
        print l


    tableClass = TableClassHorizontal()
    tableClass.process_elements(objArr)
    tableClass.print_delimiters()
    tableClass.print_table()
    print "FINAL TABLE"
    tableClass.print_final_table()

    # tableClass = TableClass(column_arr, row_arr)
    # tableClass.add_textbox_arr(textboxArr)
    # print ""
    # print tableClass

    # tableClass.process_cells()
    # configparser = ConfigParser(config, tableClass)






def output_pdf_to_table(path, config):

    fp = open(path, "rb")
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    laparams.line_margin = line_margin_threshold
    laparams.word_margin = word_margin_threshold
    codec = 'utf-8'
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    password=""
    maxpages=pages_to_view
    caching=True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, 
        password=password,caching=caching, check_extractable=False):
        interpreter.process_page(page)
        layout = device.get_result()
        getRows(layout, config)

directory = os.path.dirname(__file__)
filename = os.path.join(directory, sys.argv[1])
config = Config(os.path.join(directory, sys.argv[2]))
output_pdf_to_table(filename, config)