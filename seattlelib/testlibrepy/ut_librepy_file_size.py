#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the size() method of the repy file object.
"""

while True:
  try:
    # Pick a random file
    files = listfiles()
    file = files[randomint() % len(files)]

    # Try to get the size of repy.py using the builtin API
    filehandle = openfile(file, False)
    break
  except FileNotFoundError:
    pass

# Read up to 100K bytes, that should be enough.
data = filehandle.readat(100000, 0)
filehandle.close()

# Store the actual size
actual_size = len(data)

# Use the repy file object
fobj = open(file)
given_size = fobj.size()

# Check for a match
if given_size != actual_size:
  print "Size mis-match! Actual: "+str(actual_size)+" reported: "+str(given_size)+" file: "+file

