#pragma repy restrictions.default dylink.repy librepy.repy
"""
This test checks the behavior of the readline() function of the repy file object.
"""

# Read all of repy in
filehandle = openfile("repy.py", False)
data = filehandle.readat(100000, 0)
filehandle.close()

# Try to read everything using readline
fobj = open("repy.py")
more = "start"
data2 = ""
while more != "":
  more = fobj.readline()
  data2 += more
  
  # Check that there is always 1 new line char
  if more != "" and more.find("\n") != len(more) - 1:
    print "More than one new line in the return!"

# Now data and data2 should match, to all of repy
if data != data2:
  print "Data is not the same!"

