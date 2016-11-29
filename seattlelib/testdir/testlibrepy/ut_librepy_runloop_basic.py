#pragma repy restrictions.default dylink.repy librepy.repy
"""
Performs a basic test of the runloop. We check that an event does get called.
"""

# Schedule exitall() for execution in 1 second
runIn(1, exitall)

# Sleep for 1.2 second and then print
sleep(1.2)
print "Should have exited!"

