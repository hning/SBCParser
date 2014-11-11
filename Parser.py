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
        print obj


def convert_pdf_to_txt(path):
    # rsrcmgr = PDFResourceManager()
    # retstr = StringIO()
    # codec = 'utf-8'
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

    
    
    # cin = StringIO.StringIO()
    # pdfbinary = base64.b64decode(text)

    # cin.write(text)
    # cin.seek(0)
    # parser = PDFParser(cin)
    # doc = PDFDocument(parser)
    # parser.set_document(doc)

    fp = open(path, "rb")
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()

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