#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the behavior of librepyrandom.

We check:
  1) The return type is correct
  2) We can generate 100 random result from each API
"""

# Check that all the functions work at some level
num1 = randomint()
if type(num1) is not int:
  print "Result of randomint() is not an int! Type: "+str(type(num1))

num2 = randomlong()
if type(num2) is not long:
  print "Result of randomlong() is not a long! Type: "+str(type(num2))

num3 = randomfloat()
if type(num3) is not float:
  print "Result of randomfloat() is not a float! Type: "+str(type(num3))

data = randomstring(64)
if type(data) is not str:
  print "Result of randomstring() is not a string! Type: "+str(type(data))

elif len(data) != 64:
  print "Data provided by randombytes is not the correct length!"


# Try to generate 100 unique of each
unique_int = set([])
for x in xrange(100):
  n = randomint()
  if n in unique_int:
    print "Generated non-unique number!"
  if n < 0:
    print "Generated negative int!"
  unique_int.add(n)

unique_long = set([])
for x in xrange(100):
  n = randomlong()
  if n in unique_long:
    print "Generated non-unique long!"
  if n < 0:
    print "Generated negative long!"
  unique_long.add(n)

unique_float = set([])
for x in xrange(100):
  n = randomfloat()
  if n in unique_float:
    print "Generated non-unique float!"
  if n >= 1 or n <= 0:
    print "Generated float out of bounds: "+str(n)
  unique_float.add(n)

unique_str = set([])
for x in xrange(100):
  s = randomstring(32)
  if s in unique_str:
    print "Generated non-unique str!"
  if len(s) != 32:
    print "Generated string is wrong length! Length: "+str(len(s))
  unique_str.add(s)


