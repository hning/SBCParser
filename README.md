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

Look at vertical lines and determine the boxes from the vertical and horizontal lines.
Use the maximum sensitivity for line breaks and determine which elements are in each box. 

Assume that the columns are laid out like:

| Important Questions | Answers | Why this Matters: |
| ------------------- | ------- | ------------------|
| ...                 | ...     | ...               |

Some pdfs don't have horizontal lines (Anthem). Have to use a different method with rects for those. 

#### Analyze using lines
* Blue Cross
* CA Bronze
* PPO
#### Analyze using other methods (rects, horizontal textboxes, etc)
* Anthem
* OEMGroup
* SeeChange
* CalChoice
#### Unreadable
* Kaiser




