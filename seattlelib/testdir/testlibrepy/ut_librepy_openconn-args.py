"""
This unit test checks that the argument checking for
openconn() is sane. This is a librepy test.
"""
#pragma repy restrictions.default dylink.repy librepy.repy

# Try some invalid host args
try:
  sock = openconn(123, 80)
  print "Got a socket! Bad host arg!"
  sock.close()
except RepyArgumentError:
  pass

# Try bad ports
try:
  sock = openconn("google.com", 3.14)
  print "Got a socket! Bad port arg!"
  sock.close()
except RepyArgumentError:
  pass

# Try bad localip, should get binding error
try:
  sock = openconn("google.com", 80, "123.213.111.222")
  print "Got a socket! Bad local ip!"
  sock.close()
except AddressBindingError:
  pass

# Try an invalid IP, argument error
try:
  sock = openconn("google.com", 80, 123)
  print "Got a socket! Invalid local ip!"
  sock.close()
except RepyArgumentError:
  pass

# Try a bad local port, we don't have access
try:
  sock = openconn("google.com", 80, "127.0.0.1", 80)
  print "Got a socket! Bad port!"
  sock.close()
except ResourceForbiddenError:
  pass

# Try an invalid local port
try:
  sock = openconn("google.com", 80, "127.0.0.1", 3.14)
  print "Got a socket! Invalid port!"
  sock.close()
except RepyArgumentError:
  pass

# Try a negative timeout
try:
  sock = openconn("google.com", 80, timeout=-2)
  print "Got a socket! Negative timeout!"
  sock.close()
except RepyArgumentError:
  pass


