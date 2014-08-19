#pragma repy restrictions.default dylink.repy librepy.repy
"""
This test tries to join a subclass-ed timer object.
"""

# Setup a timeout thread
def timeout():
  sleep(5)
  print "Timeout!"
  exitall()
createthread(timeout)


class CustomTimer (Timer):
  def run(self):
    sleep(3)

# Create a custom timer
ct = CustomTimer(interval=0.2)
ct.start()

# Wait then join the timer
sleep(0.3)
if not ct.is_alive():
  print "Timer should be running now!"

ct.join()

if ct.is_alive():
  print "Timer should be dead now!"

# Exit normally
exitall()

