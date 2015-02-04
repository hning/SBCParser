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
import config
from config import *

from TableClass import *

from TableClassHorizontal import *

overlap_threshold = 0.7

min_elements_in_row = 0

#default 0.3, 0.25 works for OEMgroup
#This is the separation between lines that pdfminer uses for textbox analysis
line_margin_threshold = 0.00000001

#default 0.2
word_margin_threshold = 0.3

#Most information on the tables are within the first two pages
pages_to_view = 2

#Unused at the moment
titles = ["Important Questions", "Answers", "Why This Matters:"]

import configparser
from configparser import *

class SBCParser:
    def __init__(self, _file_name, _config):
        self.file_name = _file_name
        self.config = _config
        self.output_dict = {}

    def get_dict_string(self):
        output_str = ""
        for key,value in self.output_dict.iteritems():
            output_str = output_str + "{0}:{1}\n".format(key,value)
        return output_str

    def write_to_file(self, _output_file):
        output_file = open(_output_file, "a")
        output_file.write(self.get_dict_string());

    def execute(self):
        self.output_pdf_to_table(self.file_name, self.config)

    def get_output_dict(self):
        return self.output_dict

    def getRows(self, layout, config):
        objstack = list(reversed(layout._objs))
        rows = TableRows()
        objArr = []
        rectArr = []
        lineArr = []
        textboxArr = []

        column_arr = set()
        row_arr = set()

        max_x = 0
        max_y = 0

        num_lines = 0
        num_rects = 0

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
            elif type(obj) == LTLine:
                if is_line_vertical(obj):
                    lineArr.append(obj)
                    column_arr.add(obj.x0)
                    row_arr.add(obj.y0)
                    max_x = max(max_x, obj.x1)
                    max_y = max(max_y, obj.y1)

                    # Book-keeping
                    num_lines = num_lines + 1
     

            elif type(obj) == LTRect:
                #Keep track of other rects to (maybe) use later
                rectArr.append(LTRects(obj))
                # Book-keeping
                num_rects = num_rects + 1



        column_arr.add(max_x)
        row_arr.add(max_y)

        print ""
        textboxArr = sorted(textboxArr, key=attrgetter('x0','y0'))
        for t in textboxArr:
            print t


        print ""
        lineArr = sorted(lineArr, key=attrgetter('x0','y0'))
        for l in lineArr:
            print l

        if num_lines > 20: 
            print "LINES {0} > RECTS {1}".format(num_lines, num_rects)
            tableClass = TableClass(column_arr, row_arr)
            tableClass.add_textbox_arr(textboxArr)
            tableClass.process_cells()
        else:
            print "RECTS {0} > LINES {1}".format(num_rects, num_lines)
            tableClass = TableClassHorizontal()
            tableClass.process_elements(objArr)
        # print ""
        # print tableClass

      
        configparser = ConfigParser(config, tableClass.get_table())
        self.output_dict.update(configparser.get_dict())


    def output_pdf_to_table(self, path, config):

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
            self.getRows(layout, config)

directory = os.path.dirname(__file__)
filename = os.path.join(directory, sys.argv[1])
config = Config(os.path.join(directory, sys.argv[2]))
output_file = sys.argv[3]
open(sys.argv[3], 'w').close()

parser = SBCParser(filename, config)
parser.execute()
parser.write_to_file(output_file)

test_dict = parser.get_output_dict()
print test_dict
