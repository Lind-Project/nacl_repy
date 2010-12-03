#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the seek() and tell() functions of the repy file object.
"""

# Determine the size of repy.py
filehandle = openfile("repy.py", False)
data = filehandle.readat(100000,0)
filehandle.close()

# Get a repy file object
fobj = open("repy.py")

# Get the cursor, should be 0
if fobj.tell() != 0:
  print "Cursor should start at 0"

# Seek to the end
fobj.seek(0, fromStart=False)

# The cursor should match the size of the file
if fobj.tell() != len(data):
  print "Cursor should be at the end of the file."

# Seek to 100
fobj.seek(100)

# Check
if fobj.tell() != 100:
  print "Cursor should be at 100 bytes"

# Read 32 bytes
fobj.read(32)

# Check the cursor
if fobj.tell() != 132:
  print "Cursor should have incremented 32 bytes!"

