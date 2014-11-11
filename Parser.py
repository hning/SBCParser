from pdfminer.pdfparser import PDFParser, PDFSyntaxError
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTTextLineHorizontal, LTTextBoxHorizontal, \
                            LTChar, LTRect, LTLine
from pdfminer.pdfpage import PDFPage
from operator import itemgetter
# from cStringIO import StringIO
import os
import base64, re, datetime, StringIO

def FindLines(layout):
    objstack = list(reversed(layout._objs))
    xlines = [ ]
    ylines = [ ]
    while objstack:
        obj = objstack.pop()

       
        if type(obj) in [LTTextBoxHorizontal]:
            text = obj.get_text().replace('\n', '')
            text = text.lstrip().rstrip();

            if len(text) > 0:
                print text.encode('utf-8');
                print "{0} {1} {2} {3}".format(obj.x0, obj.x1,
                    obj.y0,obj.y1)
                print obj
                print ""

    #TODO Add code to determine which boxes are in the same row
    #Strategy: Keep a 2D array of objects that hold lists of elements for each row
    #For each box 
    #   if box either subsumes or is subsumed by one of the rows
    #       Add box to the row
    #       if the box subsumed the row
    #           update the row min and max y  
    #   else
    #       create new row with bounds from box


def convert_pdf_to_txt(path):
    # rsrcmgr = PDFResourceManager()
    # retstr = StringIO()
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
        FindLines(layout)
        print layout


    return str

directory = os.path.dirname(__file__)
filename = os.path.join(directory, '../ExampleSBC/Anthem.pdf')
print convert_pdf_to_txt(filename)