#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the open() call.

We check:
  1) That we can get a handle to a file
  2) We can get another handle to the same file
"""

# Get the first handle
fobj = open("repy.py")

# Open the second handle
fobj2 = open("repy.py")

# They should be different
if fobj is fobj2:
  print "Objects should be different!"

# Try to read 100 bytes, then seek to the end
data = fobj.read(100)
fobj.seek(0,fromStart=False)

# See if we can read the same data
data2 = fobj2.read(100)

if data != data2:
  print "Data did not match!"

