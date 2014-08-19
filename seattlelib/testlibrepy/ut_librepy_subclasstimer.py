#pragma repy restrictions.default dylink.repy librepy.repy
"""
This test tries to subclass the Timer object
"""

class CustomTimer (Timer):
  def run(self):
    exitall()

# Create a custom timer
ct = CustomTimer(interval=1)
ct.start()

# Sleep for 2 seconds, then print
sleep(2)
print "Should have exitted!"
exitall()


