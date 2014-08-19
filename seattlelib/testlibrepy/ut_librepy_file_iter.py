#pragma repy restrictions.default dylink.repy librepy.repy
"""
This test checks the behavior of the repy file object when iterating over it.
"""

# Read all of repy in
filehandle = openfile("repy.py", False)
data = filehandle.readat(100000, 0)
filehandle.close()

# Try to read everything using an iterator
fobj = open("repy.py")
data2 = ""
for more in fobj:
  # Store this line
  data2 += more
  
  # Check that there is always 1 new line char
  if more.find("\n") != len(more) - 1:
    print "More than one new line in the return!"

# Now data and data2 should match, to all of repy
if data != data2:
  print "Data is not the same!"

