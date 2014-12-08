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

overlap_threshold = 0.5
min_elements_in_row = 0
line_margin_threshold = 0.25
pages_to_view = 1
titles = ["Important Questions", "Answers", "Why This Matters:"]

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
        for index,row in enumerate(self.rows):
            if len(row) >= min_elements_in_row: 
                output += str(row)
                output += "\n"
            if index is 0:
                output += "|---|---|---|\n"
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

    def remove_upper_elements(self):
        i = 0
        found = False
        for index, r in enumerate(self.rows):
            for d in r.data:
                if strip_text(d.get_text()) in titles:
                    found=True
                    i = index
                    break
            if found is True:
                break
        self.rows = self.rows[i:]

class LTRects:
    def __init__(self, _obj):
        self.obj = _obj;
        self.width = self.obj.x1 - self.obj.x0

def getRows(layout):
    objstack = list(reversed(layout._objs))
    rows = TableRows()
    rectArr = []
    while objstack:
        obj = objstack.pop()
        #print obj
       
        if type(obj) == LTTextBoxHorizontal:
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
        elif type(obj) == LTRect:
            #Keep track of other rects to maybe use later
            rectArr.append(LTRects(obj))

    #Remove rows that are of the wrong size
    rows.rows = [row for row in rows.rows if len(row.data) > 2]

    #Find the top row that has the correct titles
    rows.remove_upper_elements()

    rows.sort()
    print rows

def output_pdf_to_table(path):

    fp = open(path, "rb")
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    laparams.line_margin = line_margin_threshold
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
filename = os.path.join(directory, 'OEMGroup.pdf')
output_pdf_to_table(filename)