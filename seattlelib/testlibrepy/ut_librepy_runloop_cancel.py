#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks that the runloop stopSchedule function works.
"""

COUNTER = [0]
DID_RUN = [False]

def func():
  COUNTER[0] += 1
  if COUNTER[0] == 1:
    DID_RUN[0] = [True]
  elif COUNTER[0] == 2:
    print "We should not have reached 2 runs!"
  

# Schedule this function
handle = runEvery(0.5, func)

# Let it run at least once
sleep(0.75)

# Stop scheduling
stopSchedule(handle)

# Check if it did run
if not DID_RUN[0]:
  print "Function was never executed!"

# Sleep for a while so that we can see if the
# function gets scheduled again
sleep(0.75)

# Something would be printed if it was scheduled.
# We can exit now.
exitall()


