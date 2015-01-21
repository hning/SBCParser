##### Analyze using other methods (rects, horizontal textboxes, etc)
* Anthem
* OEMGroup
* SeeChange
* CalChoice

All of these files should be able to be analyzed using LTTextBoxHorizontal object.

Issues: Some of the boxes don't have enough space to split horizontally or even vertically? 

#### Method
* Look at text boxes that contain 1+ '?' characters. This textbox is the first column and contains a question or multiple question.
* From these textboxes, infer the y-coordinate ranges for the second column
* Look at textboxes that fall within the y-range with an x-range above the left column
* Infer 2nd column answers
* [For boxes that contain multiple question marks]
	- Boxes should contain '\n' characters for each line break
	- Split the box using the number of newlines
	- Infer y-coordinates for ranges as normal
* [For boxes that contain text after the question mark]
	- Possible answer within the text after the question mark delimiter
	- [SeeChange.pdf] For the last question, the remaining text may be below the table itself

#### Future
* Strip phone numbers and websites for info