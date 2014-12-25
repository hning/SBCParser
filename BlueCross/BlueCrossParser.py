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

overlap_threshold = 0.7
min_elements_in_row = 0

#default 0.3, 0.25 works for OEMgroup
#This is the separation between lines that pdfminer uses for textbox analysis
line_margin_threshold = 0.00000001

#default 0.2
word_margin_threshold = 0.3

pages_to_view = 1
titles = ["Important Questions", "Answers", "Why This Matters:"]

def is_line_vertical(el):
    horizontal_distance = math.fabs(el.x1 - el.x0)
    vertical_distance = math.fabs(el.y1 - el.y0)

    #Assume that its a vertical line if the horizontal distance 
    # is less than 1% of the vertical distance
    if horizontal_distance <= vertical_distance*.01:
        return True
    return False

def strip_text(input):
    return input.replace('\n','').lstrip().rstrip();

class TableRow:
    def __init__(self, element):
        self.data = [element]
        self.min_y = element.y0
        self.max_y = element.y1
        self.max_size = self.max_y - self.min_y

    def __getitem__(self, index):
        return self.data[index]

    def __str__(self):
        output = "|"
        for d in self.data:
            text = strip_text(d.get_text())
            output += text.encode('utf-8');
            output += "|"
        return output

    def __len__(self):
        return len(self.data)
        
    def add(self, obj):
        obj_size = obj.y1 - obj.y0
        if obj_size > self.max_size:
            self.min_y = obj.y0
            self.max_y = obj.y1
            self.max_size = obj_size

        self.data.append(obj);

    def sort(self):
        self.data = sorted(self.data,
            key=attrgetter('x0'))


class TableRows:
    def __init__(self):
        self.rows = []

    def __getitem__(self, index):
        return self.rows[index]

    def __str__(self):
        output = ""
        for row in self.rows:
            if len(row) >= min_elements_in_row: 
                output += str(row)
                output += "\n\n"
        return output

    def __len__(self):
        return len(self.rows)

    def add(self, obj):
        #print obj
        #print strip_text(obj.get_text()).encode('utf-8')
        for row in self.rows:
            #Use set intersection to find rows
            newR = range(int(round(obj.y0)), int(round(obj.y1)))
            rowR = range(int(round(row.min_y)), int(round(row.max_y)))

            newS = set(newR)
            rowS = set(rowR)

            resultIntersect = newS.intersection(rowS)
            minSize = 0
            if((obj.y1 - obj.y0) > (row.max_y - row.min_y)):
                minSize = row.max_y - row.min_y
            else:
                minSize = obj.y1 - obj.y0

            if len(resultIntersect) >= (minSize * overlap_threshold):
                #Found row
                row.add(obj)
                return

        self.rows.append(TableRow(obj))

    #TODO: Finish this method
    #Check for lines that should be part of specific rows,
    #but do not fit within the textbox. Add them to the column
    def merge_rows(self):
        self.rows = sorted(self.rows, key=attrgetter('max_size'))
        for i in range(0,len(self.rows)):
            hi = i

    def sort(self):
        #Need to merge elements before sort
        self.merge_rows()
        
        for row in self.rows:
            row.sort()
        self.rows = sorted(self.rows,
            key=attrgetter('min_y'), reverse=True)

class LTRects:
    def __init__(self, _obj):
        self.obj = _obj;
        self.width = self.obj.x1 - self.obj.x0


class TableClass:
    column_arr = []
    row_arr = []

    #self.table is a 2D array of arrays that contain the text in each square

    def __init__(self, _column_arr, _row_arr):
        self.column_arr.extend(sorted(_column_arr))
        self.row_arr.extend(sorted(_row_arr))
        self.table = [[[] for i in xrange(len(self.column_arr))] for i in xrange(len(self.row_arr))]
            
    def __str__(self):
        output = "y (row): \n"
        for r in self.row_arr:
            output += str(r) + ","
        output += "\nx (col):\n"
        for c in self.column_arr:
            output += str(c) + ","

        output += "\n"
        for row in self.table:
            for col in row:
                cell_arr = sorted(col, key=attrgetter('y0'), reverse = True)
                output += "|"
                for cell in cell_arr:
                    output += cell.get_text().encode('utf-8')
            output += "\n\n"
        return output

    def add_textbox(self, text_box):
        col_num = -1
        row_num = -1
        for i in range(1, len(self.row_arr)):
            #Use set intersection to find rows
            newR = range(int(round(text_box.y0)), int(round(text_box.y1)))
            rowR = range(int(round(self.row_arr[i-1])), int(round(self.row_arr[i])))

            newS = set(newR)
            rowS = set(rowR)

            resultIntersect = newS.intersection(rowS)
            minSize = 0
            if((text_box.y1 - text_box.y0) > (self.row_arr[i] - self.row_arr[i-1])):
                minSize = self.row_arr[i] - self.row_arr[i-1]
            else:
                minSize = text_box.y1 - text_box.y0

            if len(resultIntersect) > (minSize * overlap_threshold):
                #Found found row to insert into
                row_num = i-1
                break

        for i in range(1, len(self.column_arr)):
            #Use set intersection to find columns
            newR = range(int(round(text_box.x0)), int(round(text_box.x1)))
            rowR = range(int(round(self.column_arr[i-1])), int(round(self.column_arr[i])))

            newS = set(newR)
            rowS = set(rowR)

            resultIntersect = newS.intersection(rowS)
            minSize = 0
            if((text_box.x1 - text_box.x0) > (self.column_arr[i] - self.column_arr[i-1])):
                minSize = self.column_arr[i] - self.column_arr[i-1]
            else:
                minSize = text_box.x1 - text_box.x0

            if len(resultIntersect) > (minSize * overlap_threshold):
                #Found found column to insert into
                col_num = i-1
                break

        if row_num == -1 or col_num == -1:
            print "Didn't find place for {0}".format(text_box)

        self.table[row_num][col_num].append(text_box)

    def add_textbox_arr(self, textbox_arr):
        for t in textbox_arr:
            self.add_textbox(t)



def getRows(layout):
    objstack = list(reversed(layout._objs))
    rows = TableRows()
    rectArr = []
    lineArr = []
    textboxArr = []

    column_arr = set()
    row_arr = set()

    max_x = 0
    max_y = 0

    while objstack:
        obj = objstack.pop()
        #print obj
        # print "{0} {1} {2} {3}".format(obj.x0, obj.x1,
        #             obj.y0,obj.y1)
       

        if type(obj) == LTTextBoxHorizontal:
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
            # print obj

        elif type(obj) in [LTLine, LTRect]:
            #Keep track of other rects to maybe use later
            rectArr.append(LTRects(obj))

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

    print ""

    tableClass = TableClass(column_arr, row_arr)
    tableClass.add_textbox_arr(textboxArr)
    print ""
    print tableClass



    # rectArr = sorted(rectArr, key=attrgetter('width'), reverse=True)
    # for r in rectArr:
    #     print r.obj
    #     print "{0} {1} {2} {3}".format(
    #             r.obj.x0,
    #             r.obj.x1,
    #             r.obj.y0,
    #             r.obj.y1
    #         )
    #     print r.width

    # rows.sort()
    # print rows


def output_pdf_to_table(path):

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
        password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
        layout = device.get_result()
        getRows(layout)

directory = os.path.dirname(__file__)
filename = os.path.join(directory, sys.argv[1])
output_pdf_to_table(filename)