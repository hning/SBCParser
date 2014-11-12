from pdfminer.pdfparser import PDFParser, PDFSyntaxError
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTTextLineHorizontal, LTTextBoxHorizontal, \
                            LTChar, LTRect, LTLine
from pdfminer.pdfpage import PDFPage
from operator import itemgetter, attrgetter, methodcaller
# from cStringIO import StringIO
import os
import base64, re, datetime, StringIO

overlap_threshold = 0.5

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
            #print strip_text(d.get_text())
            text = strip_text(d.get_text())
            output += text.encode('utf-8');
            output += "|".format()
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
            output += str(row)
            output += "\n"
        return output

    def __len__(self):
        return len(self.rows)

    def add(self, obj):
        #print obj
        #print strip_text(obj.get_text()).encode('utf-8')
        for row in self.rows:
            #Use set intersection
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
    def merge_rows(self):
        self.rows = sorted(self.rows, key=attrgetter('max_size'))
        for i in range(0,len(self.rows)):


    def sort(self):
        #Need to merge elements before sort
        self.merge_rows()
        
        for row in self.rows:
            row.sort()
        self.rows = sorted(self.rows,
            key=attrgetter('min_y'), reverse=True)


def getRows(layout):
    objstack = list(reversed(layout._objs))
    rows = TableRows()
    while objstack:
        obj = objstack.pop()

       
        if type(obj) in [LTTextBoxHorizontal]:
            # text = obj.get_text().replace('\n', '')
            # text = text.lstrip().rstrip();

            text = strip_text(obj.get_text())
            if len(text) > 0:
                # print text.encode('utf-8');
                # print "{0} {1} {2} {3}".format(obj.x0, obj.x1,
                #     obj.y0,obj.y1)
                # print obj
                # print ""

                rows.add(obj)

    rows.sort()
    print ""
    print rows


    #TODO Add code to determine which boxes are in the same row
    #Strategy: Keep a 2D array of objects that hold lists of elements for each row
    #For each box 
    #   if box either subsumes or is subsumed by one of the rows
    #       Add box to the row
    #       if the box subsumed the row
    #           update the row min and max y  
    #   else
    #       create new row with bounds from box
    #
    #Additional: Also take into account the x coordinates of the column to determine 
    # which column the box is in. 
    # 
    #Deal with overflow

def convert_pdf_to_txt(path):
    # rsrcmgr = PDFResourceManager()
    # retstr = StringIO
    # laparams = LAParams()
    # device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    # fp = file(path, 'rb')
    # interpreter = PDFPageInterpreter(rsrcmgr, device)
    # password = ""
    # maxpages = 0
    # caching = True
    # pagenos=set()
    # for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
    #     interpreter.process_page(page)
    # fp.close()
    # device.close()
    # str = retstr.getvalue()
    # retstr.close()

    fp = open(path, "rb")
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    codec = 'utf-8'
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    password=""
    maxpages=2
    caching=True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, 
        password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
        layout = device.get_result()
        getRows(layout)
       # print layout


    return str

directory = os.path.dirname(__file__)
filename = os.path.join(directory, '../ExampleSBC/Anthem.pdf')
print convert_pdf_to_txt(filename)