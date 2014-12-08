SBCParser
=========

Parse SBC documents using pdfminer

Mostly uses table parsing to determine the information from SBC forms (Works for OEM group perfect at the moment)

###

Look at `OEMOutput.md` above

### Usage

```
pip install -r requirements.txt
python OEMParser.py > OEMOutput.md
```

### Parsing

* Creates rows based on the LTTextBoxHorizontal of pdf miner
* Sorts rows based on height
* Uses keywords to strip rows that are above the title row (Right now using `["Important Questions", "Answers", "Why This Matters:"]`)