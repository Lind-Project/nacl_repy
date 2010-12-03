"""
This unit test checks the argument checking for recvmess().
"""
#pragma repy restrictions.default dylink.repy librepy.repy

def noop(ip, port, mess):
  sock.close()
  print "Bad! noop() called!"

# We don't have port 80
try:
  stop_func = recvmess(80,noop)
  stop_func()
  print "Port 80 allowed!"
except ResourceForbiddenError:
  pass

# Float is not allowed as a port
try:
  stop_func = recvmess(12345.0, noop)
  stop_func()
  print "Floating port allowed!"
except RepyArgumentError:
  pass

# Try a bad localip
try:
  stop_func = recvmess(12345, noop, "321.123.444.555")
  stop_func()
  print "Bad localip allowed!"
except RepyArgumentError:
  pass

# Try a really bad localip
try:
  stop_func = recvmess(12345, noop, "hi there")
  stop_func()
  print "Really bad localip allowed!"
except RepyArgumentError:
  pass

# Try a negative check interval
try:
  stop_func = recvmess(12345, noop, check_intv=-1)
  stop_func()
  print "Negative check interval worked!"
except RepyArgumentError:
  pass

# Try a 0 check interval
try:
  stop_func = recvmess(12345, noop, check_intv=0)
  stop_func()
  print "0 check interval worked!"
except RepyArgumentError:
  pass

# Try a bad thread pool
try:
  stop_func = recvmess(12345, noop, thread_pool="test")
  stop_func()
  print "Bad thread pool argument worked!"
except RepyArgumentError:
  pass

