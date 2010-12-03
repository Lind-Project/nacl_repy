#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the lock object.
"""

# Setup a timeout thread
def timeout():
  sleep(5)
  print "Timeout!"
  exitall()
createthread(timeout)

# Create the lock
lock = Lock()

# Acquire the lock
gotit = lock.acquire()
if not gotit:
  print "Should have acquired lock!"

gotit = lock.acquire(False)
if gotit:
  print "Should not have acquired lock!"

lock.release()
gotit = lock.acquire()
if not gotit:
  print "Should have acquired lock! (2)"

exitall()



