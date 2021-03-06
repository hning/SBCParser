# SBCParser

CURRENT WORKING PARSER FOUND UNDER CurrentParser/SBCParser.py

Parse SBC documents using pdfminer.

Mostly uses table parsing to determine the information from SBC forms

## Requirements:
* python 2.7+
* pdfminer

## Usage:
````
python SBCParser.py <input_file> <settings_json_file> <output_file>
````
Right now, all the arguments are necessary. There's also a lot of debugging print statements that occurs. 

## Strategy:

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

#### Analyze using horizontal rects and textboxes
* Anthem
* OEMGroup
* SeeChange
* CalChoice
* Kaiser

##Values Extracted

#### Current Key Values
* Overall deductible (In-Network, Out of Network)
* Specific Service deductible
* Out of pocket limit (In-Network, Out of Network)
* Annual Limit

#### Possible Values
* Referral for specialist
* Network of providers
* Not included in out of pocket limit (List of values)

#Setup File

```
{
	"overall_deductible":	{
		"contains": ["overall","deductible"],
		"multiple": "true",
		"type": "number", 
		"output_format": [
			{"name": "overall_individual_in-network"},
			{"name": "overall_family_in_network"},
			{"name": "overall_individual_out-network"},
			{"name": "overall_family_out-network"}
		]
	},
	"key2": {
		....
	}
}
```

### "contains"

The first non-zero column contains these strings 

### "multiple"

There are multiple hits that are described within "output_format"

### "type" - Types of parsing
* "number"
	- Numeric values
* "money"
	- Numeric values preceded by "$"
* "boolean"
	- looks for "true/false" & "yes/no"
* "boolean-number"
	- "boolean" but also includes the rest of the numbers in the text area

### Output Format
The key pair output that is described within type and given a name

### Improvements
* Add "boolean-number-yes" type. If "Yes", use output_format to read the rest of the numbers on the page. If "No", simply output "No" (Specific Case: BlueCross Out-Of-Pocket limit)
* Contains: use AND, OR, parentheses (etc.) logic for the contains
* Works on badly formatted pdfs (Kaiser etc.)
* Build out y-value from the found sentence
* Out-of-network to In-network values (how they're grouped)

