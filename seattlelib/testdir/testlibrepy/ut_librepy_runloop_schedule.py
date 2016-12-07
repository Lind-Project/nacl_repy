#pragma repy restrictions.default dylink.repy librepy.repy
"""
This test the scheduling ability of the runloop.
"""

COUNTER = [0]
FINISHED = [False]

def func():
  # Increment the counter, if we reach
  # 3 then set "finished" to true
  COUNTER[0] += 1
  if COUNTER[0] == 3:
    FINISHED[0] = True

# Schedule func to run every .25 seconds
runEvery(0.25, func)

# After 1 second, we should be finished.
sleep(1)

if not FINISHED[0]:
  print "We should have reached 3! Reached: "+str(COUNTER[0])
exitall()

