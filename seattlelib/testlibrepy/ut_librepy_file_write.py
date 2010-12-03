#pragma repy restrictions.default dylink.repy librepy.repy
"""
This test checks the behavior of the repy file objects write() method.
"""

# Create a random file
fobj = open("this.is.a.junk.out.file")

# Write to the file
fobj.write("Hello World!")
fobj.close()

# Try to read this in using the repy API
filehandle = openfile("this.is.a.junk.out.file", False)
data = filehandle.readat(50,0)
filehandle.close()

if data != "Hello World!":
  print "Got bad data! Got: "+data

# Remove the file
removefile("this.is.a.junk.out.file")

