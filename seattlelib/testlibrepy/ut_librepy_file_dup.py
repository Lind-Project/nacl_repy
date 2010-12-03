#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the dup() method of the file handle.
"""

# Get a handle
fobj = open("repy.py")

# Duplicate the handle
fobj2 = fobj.dup()

# Seek the first handle
fobj.seek(100)

# Read from both handles
data1 = fobj.read(100)
data2 = fobj2.read(100)

# The data should be different
if data1 == data2:
  print "The data should not match!"

# If we read another 100 from fobj2, it should match data1
data3 = fobj2.read(100)

if data3 != data1:
  print "The data should match now!"


