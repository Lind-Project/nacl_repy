#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the behavior of the file objects read() method.
"""

# Use the API to create a junk file
file_handle = openfile("junk.file.test.out",True)
file_handle.writeat("Test",0)
file_handle.close()

# Use the repy-file object to try to read this
fobj = open("junk.file.test.out")
data = fobj.read()
fobj.close()

# Check the data
if data != "Test":
  print "Read bad data in! Got: "+data

# Remove the file
removefile("junk.file.test.out")

