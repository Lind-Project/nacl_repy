#pragma repy restrictions.default dylink.repy librepy.repy
"""
This checks the terminate_runloop call.
"""

# Get the number of events
lim,usage,stops = getresources()

init_events = usage["events"]
terminate_runloop()
sleep(0.5) # Wait for the runloop to terminate

# Check the events again
lim,usage,stops = getresources()

after_events = usage["events"]
if after_events != init_events - 1:
  print "Run loop did not terminate!"

exitall()

