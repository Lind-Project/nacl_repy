"""
Author: Armon Dadgar
Start Date: March 31st, 2009
Description:
  Provides a tool-chain for altering resource files.

"""

# Finds all resource files
import glob

# Used for moving files
import os

def read_restrictions_file(file):
  """
  <Purpose>
    Reads in the contents of a restrictions file.
    
  <Arguments>
    file: name/path of the file to open
  
  <Returns>
    A list, where each element is a line in the file  
  """
  # Get the file object, read mode with universal newlines
  fileo = open(file,"rU")
  
  # Read in all the contents
  contents = fileo.readlines()
  
  # Close the file object
  fileo.close()
  
  return contents
  
def write_restrictions_file(file, buffer):
  """
  <Purpose>
    Writes in the contents of a restrictions file. Tries to do this safely,
    by writing to a new file, backing-up the original, renaming the new file, and finally deleting the backup.
    
  <Arguments>
    file: name/path of the file to open
    buffer: A list, where each element is a line in the file
  
  <Returns>
    Nothing  
  """
  # Get the file object, write mode
  # Use a .new suffix, so as not to corrupt the current file
  fileo = open(file+".new", "w")
  
  # Write in all the buffer
  for line in buffer:
    fileo.write(line)
  
  # Close the file object
  fileo.close()
  
  # Move the original to *.bak if it exists
  if os.path.exists(file):
    os.rename(file, file+".bak")
  
  # Move the new one to the original
  os.rename(file+".new", file)
  
  # Cleanup, remove the backup
  if os.path.exists(file+".bak"):
    os.remove(file+".bak")
  

def update_restriction(lines, restriction, restype, val, func=False):
  """
  <Purpose>
    Updates a resource in a restrictions file
  
  <Arguments>
    lines: The contents of the restrictions file, list each element is a line
    restriction: The name of the restriction e.g. resource, call
    restype: The type of restriction, e.g. events
    val: Either a new absolute value, or a callback function
    func: If true, this indicates that val is a function. That function will be given a list of the elements on the current line, and is expected
    to return the appropriate val to use.
  
  <Side Effects>
    The restrictions file will be modified
  
  <Returns>
    The contents of the new restrictions file, list each element is a line
  """
  # Empty buffer for new contents
  newContents = []
  
  # Store the length of the restriction
  restrictionLength = len(restriction)
  
  # Check each line if it contains the resource
  for line in lines:
    # Check if the line starts with a comment or the restriction as an optimization
    # This prevents us from processing every single line needlessly
    if not line[0] == "#" and restriction == line[0:restrictionLength]:
      # Explode on space
      lineContents = line.split(" ")
      
      # Make sure this is the correct resource
      # This is okay if there are comments, because either the index will be offset
      # Or the value of the index will be changed, and will not match
      if not lineContents[0] == restriction or not lineContents[1] == restype:
        # Wrong line, continue after appending this line
        newContents.append(line)
        continue
        
      # Check if we are using a callback function
      if func:
        userVal = val(lineContents)
      else:
        # Otherwise, this is just the real value
        userVal = val
    
      # Change the value to the string val
      lineContents[2] = str(userVal)
      
      # Re-create the line string, with the modifications
      lineString = ""
      for elem in lineContents:
        lineString += elem + " "
      lineString = lineString.strip()
      lineString += "\n"
      
      # Append the new line to the buffer
      newContents.append(lineString)
      
    else:
      # Just append this line to the buffer
      newContents.append(line)
      
  # Return the modified buffer
  return newContents


def get_all_resource_files():
  """
  <Purpose>
    Returns a list with all the resource files.
  
  <Returns>
    A list object with file names.  
  """
  return glob.glob("resource.v*")
  

def process_restriction_file(file, tasks):
  """
  <Purpose>
    Serves as a useful macro for processing a resource file.
  
  <Argument>
    file: The name of a resource file.
    tasks: A list of tuple objects. Each tuple should contain the following:
    (restriction, restype, val, func). See update_restriction for the meaning of these values.
  
  <Returns>
    Nothing
  """
  # Get the content
  content = read_restrictions_file(file)

  # Create a new buffer to store the changes
  newContent = content
  
  # Run each task against the restrictions file
  for task in tasks:
    (restriction, restype, val, func) = task
    newContent = update_restriction(newContent, restriction, restype, val, func)
  
  # Check if there were any changes
  if content != newContent:
    # Write out the changes
    write_restrictions_file(file, newContent)
    
    
def process_all_files(tasks):
  """
  <Purpose>
    Serves as a useful macro for processing all resource files.
  
  <Arguments>
    tasks: A list of tuple objects. Each tuple should contain the following:
    (restriction, restype, val, func). See update_restriction for the meaning of these values.
  
  <Returns>
    A list of all the failures. They are in the form of tuples: (file, exception)
  """
  # Get all the resource files
  allFiles = get_all_resource_files()
  
  # Stores the name of all files that failed
  failedFiles = []
  
  # Process each one
  for rFile in allFiles:
    try:
      # Process this file
      process_restriction_file(rFile, tasks)
    
    # Log if any files fail
    except Exception, exp:
      failedFiles.append((rFile, exp))
  
  # Return the list of failed files 
  return failedFiles


