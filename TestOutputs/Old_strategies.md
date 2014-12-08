Iteration 1

Keep a 2D array of objects that hold lists of elements for each row
For each box 
  if box either subsumes or is subsumed by one of the rows
      Add box to the row
      if the box subsumed the row
          update the row min and max y  
  else
      create new row with bounds from box

Additional: Also take into account the x coordinates of the column to determine 
which column the box is in.

