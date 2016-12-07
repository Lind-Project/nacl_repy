#pragma repy restrictions.default dylink.repy librepy.repy
"""
This test tries to sub-class the Thread object.
"""

# Create a timeout thread
def timeout():
  sleep(4)
  print "Timeout!"
  exitall()

STARTED = [False]

class CustomThread (Thread):
  def run(self):
    STARTED[0] = True
    sleep(1)


# Create an instance of our custom thread
ct = CustomThread()

# Start the thread
ct.start()
if not ct.is_alive():
  print "Thread should be alive!"

# Join the thread
ct.join()

if ct.is_alive():
  print "Thread should be dead!"

if not STARTED[0]:
  print "Thread never started!"

exitall()


