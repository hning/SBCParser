# SBCParser

Parse SBC documents using pdfminer

Mostly uses table parsing to determine the information from SBC forms

## Requirements:
* python 2.7+
* pdfminer

## Usage:
````
python Parser.py
````
Files are hardcoded for now.

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

#### Analyze using other methods (rects, horizontal textboxes, etc)
* Anthem
* OEMGroup
* SeeChange
* CalChoice

#### Unreadable
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
* "money-variable"
	- Determines whether there is a non-network option and then generates correct output based on the given information
* "boolean"
	- looks for "true/false" & "yes/no"
* "boolean-extra"
	- "boolean" but also includes the extra information within the second box

### Output Format
The key pair output that is described within type and given a name

### Improvements
* Variable numbers (For example: 2 numbers may indicate that there are no out of network penalties)
	- Possibly "money-variable": Creates names and parses based on the number of money items within the text
* Add "boolean-number-yes" type. If "Yes", use output_format to read the rest of the numbers on the page. If "No", simply output "No" (Specific Case: BlueCross Out-Of-Pocket limit)
* Contains: use AND, OR, parentheses (etc.) logic for the contains

