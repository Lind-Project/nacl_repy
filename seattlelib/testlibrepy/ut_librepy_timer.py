#pragma repy restrictions.default dylink.repy librepy.repy
"""
This unit test checks the Timer object.
"""

# Create a timer object to call exitall in 1 second
timer = Timer(interval=1, target=exitall)

# Start the timer
timer.start()

# Sleep for 2 seconds, and then print
sleep(2)
print "Should have exitted!"
exitall()

