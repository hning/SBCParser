SBCParser
=========

Parse SBC documents using pdfminer

Mostly uses table parsing to determine the information from SBC forms

Requirements:
* python 2.7+
* pdfminer

Usage:
````
python Parser.py
````
Files are hardcoded for now.

Strategy
~~Keep a 2D array of objects that hold lists of elements for each row
For each box 
  if box either subsumes or is subsumed by one of the rows
      Add box to the row
      if the box subsumed the row
          update the row min and max y  
  else
      create new row with bounds from box

Additional: Also take into account the x coordinates of the column to determine 
which column the box is in.~~

Look at vertical lines and determine the boxes from the vertical and horizontal lines.
Use the maximum sensitivity for line breaks and determine which elements are in each box. 

Assume that the columns are laid out like:
Important Questions | Answers | Why this Matters:|
--------------------| ------- | ---------------- |
...                 | ...     | ...              |

