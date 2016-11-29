#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the RLock() object.
"""

# Create a new instance
rl = RLock()

# Main entry for another thread
def thread():
  gotit = rl.acquire(False)
  if gotit:
    print "Second thread should not get the lock!"
  gotit = rl.acquire()
  if not gotit:
    print "Second thread should acquire the lock!"

# Thread to time us out if we take too long.
def timeout():
  sleep(5)
  print "Timeout!"
  exitall()

# Launch the timeout thread
createthread(timeout)

# Acquire the lock in the main thread
rl.acquire()

# Launch the other thread
createthread(thread)

# Re-acquire in this thread
rl.acquire()
rl.acquire()

# Release now
rl.release()
rl.release()
rl.release()

# Sleep a bit, then terminate
sleep(1)
exitall()


