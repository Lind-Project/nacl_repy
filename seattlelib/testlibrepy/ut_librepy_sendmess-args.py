"""
This unit test checks that the argument checking for
sendmess() is sane. This is a librepy test.
"""
#pragma repy restrictions.default dylink.repy librepy.repy

# Try some invalid host args
try:
  sent = sendmess(123, 80, "Test")
  print "Sent mess! Bad host arg!"

except RepyArgumentError:
  pass

# Try bad ports
try:
  sent = sendmess("google.com", 3.14, "Test")
  print "Sent mess! Bad port arg!"

except RepyArgumentError:
  pass

# Try bad localip, should get binding error
try:
  sent = sendmess("google.com", 80, "Test", "123.213.111.222")
  print "Sent mess! Bad local ip!"

except AddressBindingError:
  pass

# Try an invalid IP, argument error
try:
  sent = sendmess("google.com", 80, "Test", 123)
  print "Sent mess! Invalid local ip!"

except RepyArgumentError:
  pass

# Try a bad local port, we don't have access
try:
  sent = sendmess("google.com", 80, "Test", "127.0.0.1", 80)
  print "Sent mess! Bad port!"

except ResourceForbiddenError:
  pass

# Try an invalid local port
try:
  sent = sendmess("google.com", 80, "Test", "127.0.0.1", 3.14)
  print "Sent mess! Invalid port!"

except RepyArgumentError:
  pass

