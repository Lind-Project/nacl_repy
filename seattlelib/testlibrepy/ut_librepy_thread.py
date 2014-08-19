#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the Thread object.
"""

# Start a timeout thread
def timeout():
  sleep(5)
  print "Timeout!"
  exitall()
createthread(timeout)


# This is the target of the thread
STARTED = [False]
def thread_func():
  STARTED[0] = True
  sleep(2)
  
# Create a thread object
tobj = Thread(target=thread_func)

# Start the thread, check if it is alive
tobj.start()
if not tobj.is_alive():
  print "Thread should be alive!"

# Join the thread
tobj.join()

# Check that the thread is now dead
if tobj.is_alive():
  print "Thread should be dead!"

if not STARTED[0]:
  print "Thread never started!"

exitall()

